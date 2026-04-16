# YC Job Matcher Agent
# github.com/Anantha018
# Licensed under MIT

import os
import json
from datetime import datetime
from colorama import Fore, Style


def print_result(m: dict, rank: int = None):
    """
    Prints a single job match result to the terminal with color coding.

    Color scheme:
    - Green  → STRONG match (score >= 80)
    - Yellow → GOOD match   (score >= 65)
    - Cyan   → POSSIBLE     (score < 65)

    Fields printed:
    - Rank, score, verdict
    - Company, role, type, experience
    - Salary, equity, location, visa
    - Skills, reason, apply URL
    - Founders with LinkedIn links

    Args:
        m:    Match result dict containing job details and score
        rank: Optional rank number to display (e.g. #1, #2)
    """
    score = m.get("score", 0)

    if score >= 80:
        verdict = "STRONG"
        color = Fore.GREEN
    elif score >= 65:
        verdict = "GOOD"
        color = Fore.YELLOW
    else:
        verdict = "POSSIBLE"
        color = Fore.CYAN

    rank_str = f"#{rank} " if rank else ""
    print(color + f"\n{'─'*52}")
    print(f" {rank_str}[{score}/100] {verdict}")
    print(f"{'─'*52}" + Style.RESET_ALL)
    print(Fore.WHITE   + f" Company   " + Style.RESET_ALL + f"{m['company']}")
    print(Fore.WHITE   + f" Role      " + Style.RESET_ALL + f"{m['title']}")
    print(Fore.WHITE   + f" Type      " + Style.RESET_ALL + f"{m.get('job_type', '')} · {m.get('experience', '')}")
    print(Fore.GREEN   + f" Salary    " + Style.RESET_ALL + f"{m.get('salary', '')}  " + Fore.YELLOW + f"Equity {m.get('equity', '')}" + Style.RESET_ALL)
    print(Fore.WHITE   + f" Location  " + Style.RESET_ALL + f"{m.get('location', '')}  " + Fore.WHITE + f"Visa " + Style.RESET_ALL + f"{m.get('visa', '')}")
    if m.get("skills"):
        print(Fore.MAGENTA + f" Skills    " + Style.RESET_ALL + f"{m['skills']}")
    print(Fore.CYAN    + f" Why       " + Style.RESET_ALL + f"{m['reason']}")
    print(Fore.WHITE   + f" Apply     " + Fore.CYAN + f"{m['url']}" + Style.RESET_ALL)
    if m.get("founders"):
        seen = set()
        for f in m["founders"]:
            name = f.get("name", "")
            if name and name not in seen:
                seen.add(name)
                linkedin = f.get("linkedin", "")
                print(Fore.WHITE + f" Founder   " + Style.RESET_ALL + f"{name}  " + Fore.CYAN + f"{linkedin}" + Style.RESET_ALL)
    print()


def save_results(results: list):
    """
    Saves match results to both JSON and Excel files.

    Creates a job_matches/ folder if it doesn't exist.
    Files are timestamped so previous runs are never overwritten.

    Output files:
    - job_matches/matches_YYYYMMDD_HHMMSS.json  → raw data
    - job_matches/matches_YYYYMMDD_HHMMSS.xlsx  → formatted spreadsheet

    Excel columns:
    Rank, Score, Verdict, Company, Role, Job Type, Experience,
    Salary, Equity, Location, Visa, Skills, Why, Apply URL,
    Founders, LinkedIn Links

    Args:
        results: List of match dicts returned by match()
    """
    folder = "job_matches"
    os.makedirs(folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # save JSON
    json_path = os.path.join(folder, f"matches_{timestamp}.json")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f" JSON  saved → {json_path}")

    # save Excel
    try:
        import openpyxl
        from openpyxl.styles import Font

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Matches"

        headers = [
            "Rank", "Score", "Verdict", "Company", "Role", "Job Type",
            "Experience", "Salary", "Equity", "Location", "Visa", "Skills",
            "Why", "Apply", "Founders", "LinkedIn Links"
        ]
        ws.append(headers)

        for cell in ws[1]:
            cell.font = Font(bold=True)

        for rank, m in enumerate(results, 1):
            score = m.get("score", 0)
            verdict = "STRONG" if score >= 80 else "GOOD" if score >= 65 else "POSSIBLE"
            founders_names = ", ".join(f.get("name", "") for f in m.get("founders", []))
            founders_links = ", ".join(f.get("linkedin", "") for f in m.get("founders", []) if f.get("linkedin"))
            ws.append([
                rank,
                score,
                verdict,
                m.get("company", ""),
                m.get("title", ""),
                m.get("job_type", ""),
                m.get("experience", ""),
                m.get("salary", ""),
                m.get("equity", ""),
                m.get("location", ""),
                m.get("visa", ""),
                m.get("skills", ""),
                m.get("reason", ""),
                m.get("url", ""),
                founders_names,
                founders_links,
            ])

        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 50)

        xlsx_path = os.path.join(folder, f"matches_{timestamp}.xlsx")
        wb.save(xlsx_path)
        print(f" Excel saved → {xlsx_path}")

    except ImportError:
        print("openpyxl not installed. Run: pip install openpyxl")