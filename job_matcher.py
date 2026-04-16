# YC Job Matcher Agent
# github.com/Anantha018
# Licensed under MIT

"""
job_matcher.py — entry point

Usage:
  python match.py              → run matching
  python match.py --validate   → check profile.json only

Setup:
  1. Create profile.json based on profile.sample.json
  2. Choose your LLM provider and add API key
  3. Run: python match.py

Supported LLM providers:
  ollama   → free, local, no API key needed
  groq     → free tier, fast, needs GROQ key
  openai   → GPT models, needs OPENAI key
  claude   → Anthropic models, needs ANTHROPIC key
  gemini   → Google models, needs GEMINI key

Results saved to:
  job_matches/matches_YYYYMMDD_HHMMSS.json
  job_matches/matches_YYYYMMDD_HHMMSS.xlsx
"""

import sys
import random
from tqdm import tqdm
from colorama import Fore, Style, init
import httpx

from profile import load_profile, validate_profile
from filters import hard_filter
from llm import call_llm, extract_json
from display import print_result, save_results

init(autoreset=True)

API_URL = "https://ycagentbackend.up.railway.app"


def fetch_jobs() -> list:
    """
    Fetches all current job listings from the Launchlist API.

    The API is backed by a Supabase database that gets refreshed
    daily via a GitHub Actions cron job at 3am UTC. Jobs are
    scraped from ycombinator.com/companies.

    Returns:
        List of job dicts from the API

    Exits:
        sys.exit(1) if API is unreachable
    """
    try:
        r = httpx.get(f"{API_URL}/jobs", timeout=30)
        r.raise_for_status()
        return r.json().get("jobs", [])
    except httpx.ConnectError:
        print(Fore.RED + "\n Cannot reach API. Check your internet connection." + Style.RESET_ALL)
        sys.exit(1)
    except Exception as e:
        print(Fore.RED + f"\n Failed to fetch jobs: {e}" + Style.RESET_ALL)
        sys.exit(1)


def match(profile: dict, jobs: list, top_n: int = 10) -> list:
    """
    Runs semantic LLM matching against a list of jobs.

    Process:
    1. Splits jobs into batches of 5
    2. Sends each batch to the LLM with the user's profile
    3. LLM scores each job 0-100 and picks top 2 per batch
    4. Deduplicates and sorts all results by score
    5. Returns top_n results

    The prompt includes:
    - User summary, years experience, target roles
    - Preferred industries, locations
    - Deal breakers (hard no conditions)

    Args:
        profile: User profile dict from profile.json
        jobs:    List of filtered job dicts to match against
        top_n:   Number of top results to return (default 10)

    Returns:
        Sorted list of top_n match dicts with score and reason
    """
    provider = profile.get("llm_provider", "ollama")
    model = profile.get("model", None)
    api_key = profile.get("api_key", None)
    summary = profile.get("summary", "")
    deal_breakers = profile.get("deal_breakers", [])
    roles = profile.get("roles_looking_for", [])
    industries = profile.get("industries", [])
    locations = profile.get("locations", [])
    years = profile.get("years_experience", "")
    batch_size = 5
    best = []

    batches = [jobs[i:i + batch_size] for i in range(0, len(jobs), batch_size)]

    for batch in tqdm(batches, desc="Matching", unit="batch", colour="green"):
        jobs_text = ""
        for idx, job in enumerate(batch):
            jobs_text += f"""
JOB {idx + 1}:
Company: {job.get('company_name', '')} | Title: {job.get('title', '')}
Salary: {job.get('salary', '')} | Equity: {job.get('equity', '')} | Location: {job.get('location', '')}
Type: {job.get('job_type', '')} | Role: {job.get('role', '')} | Exp: {job.get('experience', '')}
Skills: {job.get('skills', '')} | Visa: {job.get('visa', '')}
Description: {(job.get('description') or '')[:300]}
---"""

        prompt = f"""You are a senior technical recruiter at a YC startup.
Match this candidate to jobs semantically — not just keywords.

CANDIDATE:
{summary}
Years experience: {years}
Looking for: {', '.join(roles)}
Industries: {', '.join(industries)}
Locations: {', '.join(locations)}
{f"HARD NO — skip if any apply: {', '.join(deal_breakers)}" if deal_breakers else ""}

JOBS:
{jobs_text}

Score each job 0-100. Consider:
- Skill overlap (semantic not just keywords)
- Role seniority match
- Company stage match
- Location match
- Industry alignment

Pick top 2 with score >= 65.
Return ONLY a JSON array. Each object MUST have all three fields:
- job_number: integer between 1 and {len(batch)} (REQUIRED)
- score: integer between 0 and 100 (REQUIRED)
- reason: one sentence string (REQUIRED)

Example:
[{{"job_number":1,"score":85,"reason":"strong Python match"}}]

If no good match return exactly: []
DO NOT add any text before or after the JSON array."""

        try:
            text = call_llm(prompt, provider, model, api_key)
            matches = extract_json(text)
            for m in matches:
                idx = m.get("job_number", 0) - 1
                if 0 <= idx < len(batch):
                    job = batch[idx]
                    best.append({
                        "score": int(m.get("score", 0) or 0),
                        "reason": m.get("reason", ""),
                        "url": job.get("url", ""),
                        "company": job.get("company_name", ""),
                        "title": job.get("title", ""),
                        "salary": job.get("salary", ""),
                        "equity": job.get("equity", ""),
                        "location": job.get("location", ""),
                        "job_type": job.get("job_type", ""),
                        "role": job.get("role", ""),
                        "experience": job.get("experience", ""),
                        "skills": job.get("skills", ""),
                        "visa": job.get("visa", ""),
                        "founders": job.get("founders", []),
                    })
        except Exception as e:
            tqdm.write(Fore.RED + f"  Batch error: {e}" + Style.RESET_ALL)

    # deduplicate
    seen_urls = set()
    unique = []
    for m in best:
        if m["url"] not in seen_urls:
            seen_urls.add(m["url"])
            unique.append(m)

    # sort and cut
    unique.sort(key=lambda x: x.get("score", 0), reverse=True)
    top = unique[:top_n]

    # print final ranked results
    print(Fore.GREEN + f"\n{'═'*52}")
    print(f" FINAL TOP {len(top)} MATCHES")
    print(f"{'═'*52}" + Style.RESET_ALL)
    for rank, m in enumerate(top, 1):
        print_result(m, rank=rank)

    return top


def main():
    """
    Main entry point for the YC job matcher.

    Flow:
    1. Load profile.json
    2. Fetch jobs from API
    3. Hard filter irrelevant jobs
    4. Shuffle for coverage across runs
    5. Cap to scan_limit if set
    6. Run LLM matching in batches
    7. Print ranked results
    8. Save to JSON + Excel

    Flags:
    --validate   → only check profile.json, skip matching
    """
    print(Fore.WHITE + " ⚡ YC Job Matcher Agent by " + Fore.CYAN + "@Anantha018")
    print(Fore.WHITE + " " + Fore.CYAN + "github.com/Anantha018/YC_Job_Matcher" + Style.RESET_ALL)

    # handle --validate flag
    if "--validate" in sys.argv:
        profile = load_profile()
        validate_profile(profile)
        return

    profile = load_profile()
    scan_limit = profile.get("scan_limit", None)
    top_n = profile.get("top_n", 10)

    print(f"{'─'*30}" + Style.RESET_ALL)
    print(f" Profile:  " + Fore.WHITE + f"{profile.get('name', 'unknown')}")
    print(f" LLM:      " + Fore.MAGENTA + f"{profile.get('llm_provider', 'ollama')} · {profile.get('model', 'default')}" + Style.RESET_ALL)
    print(f" Scan:     " + Fore.YELLOW + f"{scan_limit or 'all'} jobs → top {top_n} results" + Style.RESET_ALL)

    # fetch jobs
    jobs = fetch_jobs()
    print(f" Fetched   " + Fore.GREEN + f"{len(jobs)} jobs from server" + Style.RESET_ALL)

    # hard filter
    jobs = hard_filter(jobs, profile)
    print(f" Filtered  " + Fore.YELLOW + f"{len(jobs)} candidates remain" + Style.RESET_ALL)

    # shuffle for coverage across runs
    random.shuffle(jobs)

    # cap to scan_limit after filter
    if scan_limit:
        jobs = jobs[:scan_limit]
        print(f" Capped    " + Fore.YELLOW + f"{len(jobs)} sent to LLM" + Style.RESET_ALL)

    print()
    results = match(profile, jobs, top_n=top_n)

    # save results
    folder = "job_matches"
    print(Fore.CYAN + f"\n{'─'*52}")
    print(f" Saving results to ./{folder}/")
    print(f"{'─'*52}" + Style.RESET_ALL)
    save_results(results)
    print(Fore.GREEN + f"\n ✓ Open ./{folder}/ to view your matches." + Style.RESET_ALL)
    print(Fore.WHITE + f" ✓ Done. Showed top {len(results)} matches.\n" + Style.RESET_ALL)


if __name__ == "__main__":
    main()