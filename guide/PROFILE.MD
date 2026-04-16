# Profile Setup Guide

Your `profile.json` tells the matcher who you are and what you're looking for.
The more detail you give, the better your matches will be.

---

## Quick start

Copy the sample and edit it:

```bash
cp profile.sample.json profile.json
```

Then validate:

```bash
python job_matcher.py --validate
```

---

## Full field reference

### `name`
**Type:** string
**Required:** no

Your name. Only used for display in the terminal header.

```json
"name": "Anantha"
```

---

### `summary` ⭐ most important field
**Type:** string
**Required:** yes

Free text description of your background. This is what the LLM reads to understand who you are and match you to jobs. Write at least 30 words. Be specific.

**What to include:**
- Years of experience
- Your tech stack
- What kind of products you have built
- What roles you are targeting
- What type of company you want
- Location preferences
- Visa status

**Bad summary — too vague:**
```json
"summary": "Software engineer looking for jobs at startups"
```

**Good summary — specific and rich:**
```json
"summary": "3 years experience as a full stack engineer. Strong in Python, React, FastAPI, PostgreSQL. Built B2B SaaS products from scratch at seed stage startups. Looking for founding engineer or early engineer roles at seed stage AI or B2B startups. Open to San Francisco or remote. No visa sponsorship needed."
```

The more specific your summary, the more accurate the LLM matching will be.

---

### `years_experience`
**Type:** integer
**Required:** no

Your years of professional experience. Used for display only — the LLM decides seniority match semantically from your summary.

```json
"years_experience": 3
```

---

### `skills`
**Type:** array of strings
**Required:** recommended

Your technical skills. Used by the LLM to score skill overlap with job requirements.

```json
"skills": ["Python", "React", "FastAPI", "PostgreSQL", "Docker", "REST APIs"]
```

Be specific — include languages, frameworks, databases, and tools you actually know.

---

### `roles_looking_for`
**Type:** array of strings
**Required:** recommended

Job titles you are targeting. Passed to the LLM to improve matching accuracy.

```json
"roles_looking_for": ["Founding Engineer", "Early Engineer", "Full Stack Engineer"]
```

Common YC job titles:
```
Founding Engineer
Founding Full Stack Engineer
Founding AI Engineer
Early Engineer
Software Engineer
Full Stack Engineer
Backend Engineer
Frontend Engineer
ML Engineer
```

---

### `locations`
**Type:** array of strings
**Required:** recommended

Locations you are open to working in. Use the exact region names from YC's filter system below.

```json
"locations": ["America / Canada", "Remote"]
```

**Available location options — use exactly as written:**

| Value | What it covers |
|-------|---------------|
| `America / Canada` | US and Canada based jobs |
| `Remote` | Remote jobs |
| `Partly Remote` | Hybrid remote jobs |
| `Fully Remote` | 100% remote jobs |
| `Europe` | UK, France, Germany, Spain, Netherlands, Sweden, Switzerland and all European countries |
| `South Asia` | India, Pakistan, Bangladesh, Nepal |
| `Southeast Asia` | Singapore, Indonesia, Philippines, Malaysia, Vietnam, Thailand |
| `Latin America` | Mexico, Brazil, Colombia, Argentina, Chile and more |
| `Africa` | Nigeria, Kenya, Ghana, South Africa and more |
| `Middle East and North Africa` | Israel, Egypt, UAE, Saudi Arabia, Turkey and more |
| `East Asia` | Hong Kong, China, South Korea, Japan |
| `Oceania` | Australia, New Zealand |

**Examples:**
```json
"locations": ["America / Canada", "Remote"]
"locations": ["Fully Remote"]
"locations": ["Europe", "Remote"]
"locations": ["South Asia", "Remote"]
"locations": ["America / Canada", "Europe", "Fully Remote"]
```

---

### `industries`
**Type:** array of strings
**Required:** recommended

Industries you are interested in. Use the exact values from YC's industry filter below.

```json
"industries": ["B2B", "Fintech", "Healthcare"]
```

**Available industry options — use exactly as written:**

| Value | Description |
|-------|-------------|
| `B2B` | Business to business software and services |
| `Consumer` | Consumer products and apps |
| `Fintech` | Financial technology |
| `Healthcare` | Health and medical technology |
| `Education` | EdTech and learning |
| `Industrials` | Manufacturing, logistics, supply chain |
| `Real Estate and Construction` | PropTech and construction tech |
| `Government` | GovTech and civic tech |

---

### `not_interested_in`
**Type:** array of strings
**Required:** no

Topics you want to hard filter out before the LLM sees them. Jobs mentioning these keywords anywhere in their title, description, or skills get removed automatically — saving API calls and improving result quality.

```json
"not_interested_in": ["Web3", "Gaming", "Defense", "Crypto", "Enterprise", "Sales"]
```

These are case-insensitive substring matches:
```
"Web3"    → removes any job where "web3" appears anywhere
"Gaming"  → removes any job where "gaming" appears anywhere
"Defense" → removes any job where "defense" appears anywhere
```

Use this for topics you absolutely do not want. For softer preferences use `deal_breakers` instead which lets the LLM decide.

---

### `deal_breakers`
**Type:** array of strings
**Required:** no

Hard conditions that are absolute nos. These get added to the LLM prompt as:
```
HARD NO — skip if any apply: no equity, no remote, below $100K
```

The LLM will skip jobs where these conditions apply.

```json
"deal_breakers": ["no equity", "no remote", "below $100K"]
```

Examples:
```
"no equity"
"no remote"
"below $80K salary"
"India only"
"requires 6+ years"
"no sponsorship"
```

---

### `needs_visa`
**Type:** boolean
**Required:** yes

Whether you need visa sponsorship to work in the US.

```json
"needs_visa": false
```

- `false` — you are a US citizen or resident, do not need sponsorship
- `true` — you need the company to sponsor your visa

When `true`, jobs that say "US citizen only" and do not mention sponsorship get filtered out automatically before the LLM.

---

### `llm_provider`
**Type:** string
**Required:** yes

Which LLM provider to use for matching.

```json
"llm_provider": "groq"
```

**Available options:**

| Provider | Cost | Speed | Quality | Notes |
|----------|------|-------|---------|-------|
| `ollama` | Free | Medium | Good | Runs locally, needs Ollama installed |
| `groq` | Free tier | Fast | Great | Recommended for most users |
| `openai` | Paid | Fast | Great | GPT models |
| `claude` | Paid | Fast | Great | Anthropic models |
| `gemini` | Free tier | Fast | Great | Google models |

**Recommendation:** Start with `groq` — free tier, fast, and high quality. Get a key at [console.groq.com](https://console.groq.com).

---

### `model`
**Type:** string
**Required:** no (uses provider default if empty)

Specific model name to use. Leave empty `""` to use the provider default.

```json
"model": "llama-3.3-70b-versatile"
```

**Default models per provider:**

| Provider | Default model |
|----------|--------------|
| `ollama` | `llama3.1:8b` |
| `groq` | `llama-3.3-70b-versatile` |
| `openai` | `gpt-4o-mini` |
| `claude` | `claude-haiku-4-5-20251001` |
| `gemini` | `gemini-2.5-flash` |

**Other good options:**

Ollama (local, check your RAM):
```
llama3.2:3b     → needs 2GB RAM, fast
llama3.1:8b     → needs 5GB RAM, better quality
```

Groq (free, runs on their servers — no RAM needed):
```
llama-3.3-70b-versatile   → best quality, recommended
llama3.1-8b-instant       → faster, lighter
```

OpenAI:
```
gpt-4o-mini   → cheap and fast
gpt-4o        → best quality, more expensive
```

Gemini:
```
gemini-2.5-flash       → fast, good quality
gemini-2.5-flash-lite  → faster, lighter
```

---

### `api_key`
**Type:** string
**Required:** yes (except for ollama)

Your API key for the chosen provider. Not needed if using `ollama`.

```json
"api_key": "gsk_your_groq_key_here"
```

Where to get your key:
- Groq: [console.groq.com](https://console.groq.com) → API Keys
- OpenAI: [platform.openai.com](https://platform.openai.com) → API Keys
- Anthropic: [console.anthropic.com](https://console.anthropic.com) → API Keys
- Gemini: [aistudio.google.com](https://aistudio.google.com) → Get API Key

---

### `top_n`
**Type:** integer
**Required:** no (default: 10)

How many final matches to show in terminal and save to files.

```json
"top_n": 10
```

| Value | Best for |
|-------|---------|
| `10` | Focused, high quality shortlist |
| `20` | Broader view |
| `30` | Maximum coverage |

Note: `top_n` must be less than `scan_limit`. If you scan 50 jobs and ask for 30 results, you will get fewer than 30 because not all 50 jobs will score above the match threshold.

---

### `scan_limit`
**Type:** integer or null
**Required:** no (default: null = scan all)

How many jobs to send to the LLM after hard filtering. Controls the tradeoff between speed, cost, and coverage.

Jobs are shuffled randomly before the limit is applied — so each run sees a different subset, giving better coverage over multiple runs.

```json
"scan_limit": 100
```

| Value | Jobs scanned | Speed | API calls | Best for |
|-------|-------------|-------|-----------|---------|
| `30` | 30 | Very fast | ~6 | Quick test run |
| `100` | 100 | Fast | ~20 | Daily use |
| `200` | 200 | Medium | ~40 | Thorough search |
| `null` | All 500+ | Slow | ~100+ | Maximum coverage |

**Good combinations:**
```json
"scan_limit": 100, "top_n": 10    ← recommended daily use
"scan_limit": 200, "top_n": 20    ← thorough search
"scan_limit": 50,  "top_n": 10    ← quick run
"scan_limit": null, "top_n": 30   ← scan everything
```

---

## Complete example

```json
{
  "name": "Anantha",
  "summary": "3 years experience as a full stack engineer. Strong in Python, React, FastAPI, PostgreSQL. Built B2B SaaS products from scratch at seed stage startups. Looking for founding engineer or early engineer roles at seed stage AI or B2B startups. Open to San Francisco or remote. No visa sponsorship needed.",
  "years_experience": 3,
  "skills": ["Python", "React", "FastAPI", "PostgreSQL", "REST APIs", "Docker"],
  "roles_looking_for": ["Founding Engineer", "Early Engineer", "Full Stack Engineer"],
  "locations": ["America / Canada", "Remote"],
  "industries": ["B2B", "Healthcare", "Fintech"],
  "not_interested_in": ["Web3", "Gaming", "Defense", "Crypto"],
  "deal_breakers": ["no equity", "no remote"],
  "needs_visa": false,
  "llm_provider": "groq",
  "model": "llama-3.3-70b-versatile",
  "api_key": "gsk_your_key_here",
  "top_n": 10,
  "scan_limit": 100
}
```

---

## Minimal example (only required fields)

```json
{
  "name": "Your Name",
  "summary": "3 years full stack engineer. Python, React, FastAPI. Looking for founding engineer roles at AI startups. Open to San Francisco or remote. No visa needed.",
  "needs_visa": false,
  "llm_provider": "ollama",
  "model": "llama3.1:8b",
  "api_key": ""
}
```

---

## Tips for better results

**Write a detailed summary**
The summary is the single most important field. The LLM reads it and decides what is a match. More detail means better matches.

**Use `not_interested_in` aggressively**
Add entire topics or industries you never want. It saves API calls and removes noise before the LLM ever sees those jobs.

**Increase `scan_limit` for better coverage**
With `scan_limit: 50` you only see 50 random jobs per run. Run multiple times across a few days to cover the full dataset.

**Start with Groq**
Free tier, fast, uses a 70B model. Best quality at zero cost. Get a free key at [console.groq.com](https://console.groq.com).

**Validate before first run**
```bash
python job_matcher.py --validate
```

---

## Validate your profile

```bash
python job_matcher.py --validate
```

Output when good:
```
✓ Profile looks good — ready to match
```

Output with warnings:
```
⚠ Profile warnings:
  • Summary is too short — add more detail for better matches
  • No industries set — add preferred industries
```