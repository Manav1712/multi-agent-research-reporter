Here’s the execution plan in Markdown format:

````markdown
# Execution Plan for LLM Engineer Assessment

## Phase 1 — Setup & Foundations
**Goal:** Get the development environment ready and the basic pipeline running.

1. **Project Setup**
   - Create a new GitHub repo (`multi-agent-research-reporter`).
   - Set up a Python virtual environment and install dependencies:
     ```bash
     pip install groq requests beautifulsoup4 reportlab PyPDF2
     ```
   - Add `requirements.txt`.

2. **API Access**
   - Sign up for Groq API.
   - Store API key securely in `.env` file.
   - Write a helper function for making Groq LLM calls with retry logic.

3. **Skeleton Pipeline**
   - Create `main.py` with placeholders for **Agent 1–4**.
   - Define a central `run_pipeline(query)` function that calls agents sequentially.

---

## Phase 2 — Build Core Agents
**Goal:** Implement a minimal working version of all four agents.

1. **Agent 1 – Query Processor**
   - Input: User query string.
   - Use Groq LLM to generate 3–5 sub-queries.
   - Validate: Remove duplicates, enforce relevance.

2. **Agent 2 – Data Collector**
   - For each sub-query, fetch top 2–3 URLs via a search API or scraping.
   - Use `BeautifulSoup` to extract clean text.
   - Handle failures and skip problematic sites.

3. **Agent 3 – Content Analyzer**
   - Combine scraped text for each sub-query.
   - Truncate to fit Groq context (~4k chars).
   - Use LLM to produce 3–4 structured sections with summaries.

4. **Agent 4 – Report Generator**
   - Take structured content and format it into a PDF (ReportLab).
   - Include:
     - Title page (query + date)
     - Section headings
     - Page numbers
   - Save to `/sample_outputs`.

---

## Phase 3 — Error Handling & Edge Cases
**Goal:** Make the MVP robust enough to handle real-world queries.

1. **API Failure Recovery**
   - Retry with exponential backoff for Groq API.
   - Skip failed sub-queries gracefully.

2. **Content Quality**
   - Remove irrelevant/duplicate sections.
   - Ensure word count ~300–500.

3. **Data Limits**
   - If scraped content is huge, prioritize most relevant sections.

---

## Phase 4 — Nice-to-Haves (Optional if Time)
**Goal:** Impress with polish, but only after MVP works.

1. **Parallel Processing**
   - Use `asyncio` or `concurrent.futures` to fetch web data in parallel.

2. **Advanced Formatting**
   - Add tables, bullet points, or side-by-side comparisons.
   - Include clickable hyperlinks for sources.

3. **Source Citations**
   - Add a “References” section in the PDF with URLs.

4. **Comprehensive README**
   - Setup instructions.
   - Agent roles & flow diagram.
   - Example usage + sample PDFs.

---

## Phase 5 — Final Checks & Submission
**Goal:** Ensure your deliverable is production-ready.

1. **Testing**
   - Run with at least 3 diverse queries.
   - Confirm each generates a clean, readable PDF.

2. **Repo Cleanup**
   - Remove unused code/files.
   - Commit final changes.

3. **Submission**
   - Push repo to GitHub.
   - Include `/sample_outputs` folder with PDFs.
   - Share link.
````

Do you want me to also prepare the **recommended GitHub folder structure** for this so it’s immediately ready for you to code? That would make this plan instantly actionable.
