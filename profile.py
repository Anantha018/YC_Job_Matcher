# YC Job Matcher Agent
# github.com/Anantha018
# Licensed under MIT

import os
import sys
import json
from colorama import Fore, Style


def load_profile(path: str = "profile.json") -> dict:
    """
    Loads the user's profile from a JSON file.

    The profile.json file contains the user's background,
    preferences, LLM provider config, and matching settings.

    Required fields:
    - summary        → free text description of background
    - llm_provider   → one of: ollama, groq, openai, claude, gemini
    - api_key        → API key for chosen provider (not needed for ollama)

    Optional but recommended fields:
    - roles_looking_for  → list of target job titles
    - locations          → list of preferred locations
    - skills             → list of technical skills
    - industries         → list of preferred industries
    - not_interested_in  → list of topics to skip
    - deal_breakers      → list of hard no conditions
    - needs_visa         → bool, True if user needs sponsorship
    - years_experience   → int, years of experience
    - top_n              → int, number of results to show (default 10)
    - scan_limit         → int, max jobs to send to LLM (default all)

    Args:
        path: Path to profile.json file (default: profile.json)

    Returns:
        Profile dict loaded from JSON

    Exits:
        sys.exit(1) if file not found
    """
    if not os.path.exists(path):
        print(Fore.RED + "\n profile.json not found.")
        print(Fore.YELLOW + " Create one based on profile.sample.json")
        print(Fore.YELLOW + " Run: python match.py --validate to check your profile\n" + Style.RESET_ALL)
        sys.exit(1)
    with open(path) as f:
        return json.load(f)


def validate_profile(profile: dict):
    """
    Checks the profile for missing or weak fields and prints warnings.

    Designed to be run standalone before matching:
        python match.py --validate

    Does NOT run automatically during normal matching to avoid
    slowing down the main flow. User runs it once during setup
    or after updating their profile.

    Checks:
    - Summary word count (< 30 words is too short)
    - roles_looking_for is set
    - locations is set
    - skills is set
    - industries is set

    Args:
        profile: User profile dict loaded from profile.json

    Prints:
        Yellow warnings for weak fields
        Green success message if profile looks good
    """
    warnings = []

    summary = profile.get("summary", "")
    if len(summary.split()) < 30:
        warnings.append("Summary is too short — add more detail for better matches")

    if not profile.get("roles_looking_for"):
        warnings.append("No roles_looking_for set — add target roles")

    if not profile.get("locations"):
        warnings.append("No locations set — add preferred locations")

    if not profile.get("skills"):
        warnings.append("No skills set — add your tech stack")

    if not profile.get("industries"):
        warnings.append("No industries set — add preferred industries")

    if not profile.get("llm_provider"):
        warnings.append("No llm_provider set — add ollama, groq, openai, claude or gemini")

    if profile.get("llm_provider") != "ollama" and not profile.get("api_key"):
        warnings.append("No api_key set — add your API key for chosen provider")

    if warnings:
        print(Fore.YELLOW + "\n⚠  Profile warnings:")
        for w in warnings:
            print(Fore.YELLOW + f"   • {w}")
        print(Style.RESET_ALL)
    else:
        print(Fore.GREEN + "\n ✓ Profile looks good — ready to match\n" + Style.RESET_ALL)