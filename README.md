# ⚡ YC Job Matcher Agent

> Match your profile against every hiring YC company — daily fresh data, runs on your machine, uses your own LLM.

Built by [@Anantha018](https://github.com/Anantha018)

---

## What is this?

YC Job Matcher Agent is a CLI tool that:

- Fetches fresh job listings from all hiring YC companies daily
- Matches them against your profile using an LLM of your choice
- Saves ranked results to Excel and JSON
- Runs entirely on your machine — no account needed, no data sent anywhere except to your chosen LLM

The backend scrapes ycombinator.com every day and stores jobs in a hosted database. You run `job_matcher.py` locally, it fetches the latest jobs, your LLM scores them against your profile, and you get ranked results.

---

## How it works

```
Your machine                    Hosted server
─────────────                   ─────────────
job_matcher.py
  reads profile.json
  calls GET /jobs   ──────────►  API
                                  reads from DB
                   ◄──────────── returns jobs JSON
  runs LLM locally
  scores each job
  prints results
  saves to Excel + JSON
```

Your API keys and profile never leave your machine. The server only serves job data.

---

## Prerequisites

Before you start, make sure you have:

- **Python 3.10 or higher** — [download here](https://python.org)
- **Git** — [download here](https://git-scm.com)
- **An LLM** — pick one:
  - [Ollama](https://ollama.com) — free, runs locally, no API key needed
  - [Groq](https://console.groq.com) — free tier, fast, needs free API key
  - [OpenAI](https://platform.openai.com) — GPT models, needs paid API key
  - [Anthropic](https://console.anthropic.com) — Claude models, needs paid API key
  - [Google AI Studio](https://aistudio.google.com) — Gemini models, free tier available

---

## Installation

### Step 1 — Clone the repo

```bash
git clone https://github.com/Anantha018/YC_Job_Matcher
cd YC_Job_Matcher
```

### Step 2 — Create a virtual environment (recommended)

```bash
# Mac/Linux
python -m venv myenv
source myenv/bin/activate

# Windows
python -m venv myenv
myenv\Scripts\activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — If using Ollama (free local option)

Download and install Ollama from [ollama.com](https://ollama.com), then pull a model:

```bash
ollama pull llama3.1:8b
```

Make sure Ollama is running before you use the matcher.

---

## Setup

### Step 1 — Create your profile

Copy the sample profile and fill in your details:

```bash
cp profile.sample.json profile.json
```

Open `profile.json` and edit it. See [PROFILE.md](PROFILE.md) for a detailed explanation of every field.

### Step 2 — Validate your profile

```bash
python job_matcher.py --validate
```

This checks your profile for missing or weak fields without running the full matcher.

---

## Usage

### Run the matcher

```bash
python job_matcher.py
```

That's it. Results stream to your terminal as batches finish and get saved to `job_matches/`.

### Validate profile only

```bash
python job_matcher.py --validate
```

---

## Output

Results are saved to `job_matches/` folder after every run:

```
job_matches/
  matches_20260415_093000.json   ← raw data
  matches_20260415_093000.xlsx   ← formatted spreadsheet
```

Excel columns:
```
Rank | Score | Verdict | Company | Role | Job Type | Experience |
Salary | Equity | Location | Visa | Skills | Why | Apply URL |
Founders | LinkedIn Links
```

Terminal output shows:
```
────────────────────────────────────────────────────
 #1 [92/100] STRONG
────────────────────────────────────────────────────
 Company   Kinro
 Role      Founding AI Engineer
 Type      Full-time · 3+ years
 Salary    $120K - $300K  |  Equity 0.75% - 2.00%
 Location  San Francisco, CA, US  |  Visa Will sponsor
 Skills    Python, FastAPI, React
 Why       Python/FastAPI background maps directly to their AI agent stack
 Apply     https://ycombinator.com/companies/kinro/jobs/...
 Founder   Parth Ainampudi
 Founder   Corentin Hugot  https://linkedin.com/in/corentin-hugot
```

---

## LLM Provider Setup

### Ollama (free, local)

1. Install from [ollama.com](https://ollama.com)
2. Pull a model: `ollama pull llama3.1:8b`
3. In `profile.json`:
```json
"llm_provider": "ollama",
"model": "llama3.1:8b",
"api_key": ""
```

### Groq (free tier, recommended)

1. Sign up at [console.groq.com](https://console.groq.com)
2. Create an API key
3. In `profile.json`:
```json
"llm_provider": "groq",
"model": "llama-3.3-70b-versatile",
"api_key": "gsk_your_key_here"
```

### OpenAI

1. Sign up at [platform.openai.com](https://platform.openai.com)
2. Create an API key
3. In `profile.json`:
```json
"llm_provider": "openai",
"model": "gpt-4o-mini",
"api_key": "sk-your_key_here"
```

### Anthropic (Claude)

1. Sign up at [console.anthropic.com](https://console.anthropic.com)
2. Create an API key
3. In `profile.json`:
```json
"llm_provider": "claude",
"model": "claude-haiku-4-5-20251001",
"api_key": "sk-ant-your_key_here"
```

### Gemini

1. Get a free API key at [aistudio.google.com](https://aistudio.google.com)
2. In `profile.json`:
```json
"llm_provider": "gemini",
"model": "gemini-2.5-flash",
"api_key": "AIza_your_key_here"
```

---

## Tuning results

### Get more results

```json
"top_n": 20,
"scan_limit": 200
```

### Get faster results

```json
"scan_limit": 50
```

Lower `scan_limit` = fewer LLM calls = faster but less coverage.

### Get best coverage

```json
"scan_limit": null
```

Scans all jobs. Takes longer but most thorough.

---

## File structure

```
yc-jobmatcher-agent-cli/
├── job_matcher.py      ← entry point, run this
├── filters.py          ← hard filter logic
├── llm.py              ← LLM provider calls
├── display.py          ← terminal output and file saving
├── profile.py          ← profile loading and validation
├── profile.sample.json ← template to copy
├── requirements.txt    ← dependencies
├── PROFILE.md          ← detailed profile field guide
└── README.md           ← this file
```

---

## Troubleshooting

**Cannot reach API**
```
Check your internet connection.
The server might be temporarily down — try again in a few minutes.
```

**Rate limit hit**
```
The matcher automatically retries after 60 seconds.
Or reduce scan_limit in profile.json to make fewer API calls.
```

**profile.json not found**
```
Run: cp profile.sample.json profile.json
Then fill in your details.
```

**Ollama not working**
```
Make sure Ollama is running: ollama serve
Make sure you pulled the model: ollama pull llama3.1:8b
```

**No matches found**
```
Try increasing scan_limit to scan more jobs.
Check profile.json has enough detail in the summary field.
Run: python job_matcher.py --validate
```

---

## Requirements

```
httpx==0.28.1
colorama==0.4.6
tqdm==4.67.1
openpyxl==3.1.5
ollama==0.6.1
groq==0.37.1
openai==1.109.1
anthropic==0.76.0
google-genai==1.65.0
```

Install only the LLM packages you need. For example if using Groq only:

```bash
pip install httpx colorama tqdm openpyxl groq
```

---

## Roadmap

Currently stable and working. Future features depend on community usage and feedback.

### Planned if people use it

**Outreach message generator**
After matching, generate personalized cold outreach templates for each job:
- YC application message
- LinkedIn connection request note
- LinkedIn cold message to founder
- Email outreach template

All pre-customized based on your profile and the specific job and founder — not generic copy-paste templates.

**Chatbot setup interface**
Instead of manually editing `profile.json`, a conversational flow:
```
> What's your background?
> What roles are you targeting?
> What industries excite you?
> Any deal breakers?
```
Builds and refines your profile through chat.

**Company size filter**
Filter jobs by team size — useful if you only want very early stage companies (1-10 people) or want to avoid large teams.

**More filters based on user feedback**
As people use it and share what's missing — funding stage, company age, revenue, tech stack overlap score, and more. Built based on what actually matters to users, not assumptions.

---

## Feedback and contributions

If you use this and find it useful — star the repo, open an issue, or reach out.

Feature requests and PRs welcome.

[@Anantha018](https://github.com/Anantha018)

---

## License

MIT License — see [LICENSE](LICENSE)

Built by [@Anantha018](https://github.com/Anantha018)