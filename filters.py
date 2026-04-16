# YC Job Matcher Agent
# github.com/Anantha018
# Licensed under MIT

def hard_filter(jobs: list, profile: dict) -> list:
    """
    Filters out irrelevant jobs before sending to LLM.
    
    This is a fast, deterministic filter — no AI involved.
    Removes jobs that are obviously wrong matches based on
    simple rules so the LLM only sees relevant candidates.
    
    Rules applied:
    - Skip non-job listings (advisors, ambassadors, referrals)
    - Skip visa mismatches (US citizen only if user needs sponsorship)
    - Skip topics user explicitly said they're not interested in
    
    Args:
        jobs:    List of job dicts fetched from the API
        profile: User's profile.json loaded as a dict
    
    Returns:
        Filtered list of jobs ready for LLM scoring
    """
    skip_titles = ["former founder", "advisor", "investor", "ambassador", "referral"]
    not_interested = [x.lower() for x in profile.get("not_interested_in", [])]

    filtered = []
    for job in jobs:
        title = (job.get("title") or "").lower()
        description = (job.get("description") or "").lower()
        visa = (job.get("visa") or "").lower()
        skills = (job.get("skills") or "").lower()

        # skip non-job listings
        if any(kw in title for kw in skip_titles):
            continue

        # skip visa mismatch
        if profile.get("needs_visa"):
            job_requires_citizen = "us citizen" in visa
            job_offers_sponsorship = "sponsor" in visa

            if job_requires_citizen and not job_offers_sponsorship:
                continue

        # skip not interested topics
        combined = f"{title} {description} {skills}"
        if any(kw in combined for kw in not_interested):
            continue

        filtered.append(job)

    return filtered