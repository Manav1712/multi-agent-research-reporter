# Multi-Agent Research System

A Python-based automated research system that processes user queries and generates professional PDF reports using a 4-agent architecture.

## Overview

This system takes a research query as input and produces a structured PDF report by:
1. **Decomposing** the query into focused sub-queries
2. **Collecting** relevant data from web sources
3. **Analyzing** and synthesizing the information
4. **Generating** a professional PDF report

## Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd multi-agent-research-reporter
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Groq API**
   - Sign up at [Groq Console](https://console.groq.com/)
   - Create a `.env` file in the project root
   - Add your API key: `GROQ_API_KEY=your_api_key_here`

## Usage

Run the system with a research query:

```bash
python main.py "Impact of AI in healthcare"
```

## Project Structure

```
multi-agent-research-reporter/
├── main.py                 # Main pipeline and agent functions
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore rules
├── README.md              # This file
├── .env                   # Environment variables (not in repo)
└── sample_outputs/        # Generated PDF reports
```

## Agent Architecture

- **Agent 1: Query Processor** - Decomposes queries into sub-queries
- **Agent 2: Data Collector** - Scrapes web sources for relevant data
- **Agent 3: Content Analyzer** - Synthesizes data into structured content
- **Agent 4: Report Generator** - Creates professional PDF reports

## Example Output

The system generates PDF reports with:
- Title page with query and date
- 3-4 structured sections
- Key findings and insights
- Professional formatting

## Dependencies

- `groq` - Groq LLM API client
- `requests` - HTTP requests for web scraping
- `beautifulsoup4` - HTML parsing
- `reportlab` - PDF generation
- `python-dotenv` - Environment variable management 