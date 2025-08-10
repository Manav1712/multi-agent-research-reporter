# Multi-Agent Research Reporter

A Python system that automatically generates research reports using a 4-agent pipeline architecture.

## Overview

This system takes a research query and produces a structured PDF report by:
1. **Query Processing** - Breaks down queries into focused sub-queries
2. **Data Collection** - Gathers information from web sources
3. **Content Analysis** - Synthesizes data into insights
4. **Report Generation** - Creates professional PDF reports

## Quick Start

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up API keys**
   ```bash
   # Create .env file
   GROQ_API_KEY=your_groq_api_key
   GOOGLE_SEARCH_API_KEY=your_google_api_key
   GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
   ```

3. **Run the system**
   ```bash
   python main.py
   ```

## Architecture

- **Agent 1**: Query decomposition using LLM
- **Agent 2**: Web search and content scraping
- **Agent 3**: Content analysis and synthesis
- **Agent 4**: PDF report generation

## Dependencies

- `groq` - LLM API client
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `reportlab` - PDF generation
- `python-dotenv` - Environment management

## Testing

```bash
# Run unit tests
python -m unittest test_agent3.py

# Test specific components
python test_agent3_demo.py
python test_google_api.py
```

## Output

Generates timestamped PDF reports with structured analysis, key findings, and recommendations. 