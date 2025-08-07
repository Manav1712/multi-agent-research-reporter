Design and implement an automated research system that processes user queries and
generates professional PDF reports. This assessment evaluates your ability to work with
LLMs, design agent-based systems, and handle real-world data processing challenges.
Responsibilities:
Implementation Requirements:
Example:
LLM Engineer Assessment
Multi-Agent Research System with PDF Report Generation
Overview
Core Requirements
Input/Output
Input: Research query string (e.g., "Impact of AI in healthcare")
Output: PDF report (300-500 words) with structured findings
Processing: All data handled in-memory (no persistent storage)
Technical Stack
LLM Provider: Groq API (free tier available)
Web Scraping: Any suitable library (BeautifulSoup, Scrapy, or APIs)
PDF Generation: Any library (ReportLab, PyPDF2, etc.)
Language: Python preferred, but open to alternatives
System Architecture
Agent 1: Query Processor
Decompose user query into 3-5 focused sub-queries
Validate sub-queries for relevance and specificity
Use Groq LLM to generate sub-queries
Implement basic validation (no duplicates, relevant to main query)
Handle edge cases (vague queries, single-word inputs)

Responsibilities:
Implementation Requirements:
Responsibilities:
Implementation Requirements:
Responsibilities:
Implementation Requirements:
Input: "Impact of AI in healthcare"
Output: [
  "AI applications in medical diagnosis",
  "Machine learning in patient care",
  "Ethical considerations of healthcare AI"
]
Agent 2: Data Collector
Search and scrape 2-3 web sources per sub-query
Extract relevant content (aim for 500-1000 words per source)
Handle scraping failures gracefully
Implement rate limiting and error handling
Extract clean text (remove ads, navigation, etc.)
Return structured data with source URLs
Agent 3: Content Analyzer
Synthesize collected data into coherent summary
Structure content with clear sections
Ensure relevance to original query
Handle Groq's context limits (truncate to ~4000 chars if needed)
Generate structured output with 3-4 main sections
Include key findings and insights
Agent 4: Report Generator
Create professional PDF report
Review content for quality and completeness
Format with proper styling

Include title page with query and date
Format with headers, paragraphs, and consistent styling
Basic quality check (word count, section presence)
Requirements
Must Have
1. Basic agent communication (simple function calls or message passing)
2. Error handling for API failures and timeouts
3. Working PDF generation with basic formatting
4. At least one iteration of quality improvement
Nice to Have
1. Parallel processing of sub-queries
2. Advanced formatting (tables, bullet points)
3. Citation of sources in the report
4. Comprehensive error recovery strategies
Deliverables
1. Source Code
Well-organized code with clear separation of agents
Basic comments explaining key functions
Requirements.txt or equivalent dependency list
2. Documentation
README with setup instructions
Brief explanation of each agent's role
Example usage with sample query
3. Demo
Working system processing at least one query
Sample PDF output included
Evaluation Criteria
Technical Implementation (40%)
Code organization and readability
Proper use of Groq API
Error handling implementation
PDF generation quality

System Design (30%)
Clear agent separation and responsibilities
Data flow between agents
Handling of edge cases
Output Quality (20%)
Relevance of generated report to query
Report structure and readability
Professional presentation
Documentation (10%)
Clear setup instructions
Code comments
Usage examples
Time Expectation
Estimated completion: 4-6 hours
Focus on working implementation over perfect optimization
Hints and Guidelines
1. Start Simple: Get a basic pipeline working before adding complexity
2. API Limits: Groq free tier has rate limits - implement basic retry logic
3. Context Management: If content exceeds limits, prioritize most relevant sections
4. Testing: Test with queries like:
"Benefits of renewable energy"
"Remote work productivity tips"
"Python vs JavaScript for web development"
Common Pitfalls to Avoid
Over-engineering the agent communication
Spending too much time on perfect PDF formatting
Not handling API failures gracefully
Forgetting to include source attributions
Resources
Groq API Documentation: https://console.groq.com/docs

Note: This assessment is designed to evaluate practical skills in working with LLMs and
building modular systems. Perfect implementation is not expected - we're looking for clear
thinking, practical problem-solving, and the ability to deliver a working solution within
reasonable constraints.
Submission Instructions
1. Create a GitHub repository with your solution
2. Include all source code and documentation
3. Add a sample_outputs/ folder with generated PDFs
4. Share the repository link

