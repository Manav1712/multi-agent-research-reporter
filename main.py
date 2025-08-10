#!/usr/bin/env python3
"""
Multi-Agent Research System
LLM Engineer Assessment
"""

import os
import time
import json
import random
import requests
from typing import Dict, List
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Debug: Check if API keys are loaded
groq_api_key = os.getenv('GROQ_API_KEY')
google_api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
google_search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')

if not groq_api_key:
    print("GROQ_API_KEY not found in environment variables")
    print("Please check your .env file contains: GROQ_API_KEY=your_actual_key")
    exit(1)
else:
    print(f"GROQ API key loaded successfully (length: {len(groq_api_key)})")

if not google_api_key or not google_search_engine_id:
    print("Google Search API credentials not found")
    print("Please add GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_ENGINE_ID to .env")
    print("Google Search functionality will be limited")
else:
    print(f"Google Search API credentials loaded successfully")

# Initialize Groq client
groq_client = Groq(api_key=groq_api_key)

def call_groq_llm(prompt, max_tokens=1000, retries=3):
    """Make Groq LLM calls with retry logic and exponential backoff"""
    for attempt in range(retries):
        try:
            print(f"    LLM Attempt {attempt + 1}/{retries}")
            response = groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            print(f"    Response length: {len(content)} characters")
            
            if not content or content.strip() == "":
                print(f"    Empty response from LLM")
                raise ValueError("Empty response from LLM")
                
            return content
            
        except Exception as e:
            print(f"    Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                print(f"    Retrying in {2 ** attempt} seconds...")
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                print(f"    All attempts failed")
                raise e

def agent1_query_processor(query):
    """
    Agent 1: Query Processor
    Decompose user query into 3-5 focused sub-queries
    """
    prompt = f"""You're a query decomposition agent. Your job is to explode a vague request into non-overlapping, actionable sub-queries that fully cover the intent.

DECOMPOSITION RULES:
- Split by aspects (who/what/where/when/why/how), facets (entities, time ranges, geos), and evidence types (stats, definitions, comparisons, examples)
- Make sub-queries atomic (answerable by a single retrieval call) and non-redundant
- Prefer breadth then depth: first enumerate facets, then drill down
- Add clarifying questions if the user's ask is underspecified

OUTPUT FORMAT:
Return exactly 3-5 sub-queries as a JSON array of strings. Each sub-query should be:
- Specific and focused
- Non-overlapping with others
- Relevant to the main query
- Actionable for web search

QUALITY BARS:
- No duplicates
- No action beyond decomposition
- No hallucinated specifics unless marked as assumption
- Prefer neutral wording; avoid leading premises

QUERY TO DECOMPOSE: "{query}"

Return only the JSON array of sub-queries, no other text. Example: ["sub-query 1", "sub-query 2", "sub-query 3"]"""

    try:
        response = call_groq_llm(prompt, max_tokens=500)
        
        # Clean and parse JSON response
        try:
            # Clean the response - remove any non-JSON text
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()
            
            sub_queries = json.loads(response)
            
            # Validate the response
            if isinstance(sub_queries, list) and len(sub_queries) >= 3:
                # Ensure all items are strings and meaningful
                valid_queries = []
                for q in sub_queries:
                    if isinstance(q, str) and len(q.strip()) > 10:  # Minimum meaningful length
                        valid_queries.append(q.strip())
                
                if len(valid_queries) >= 3:
                    print(f"Generated {len(valid_queries)} sub-queries")
                    return valid_queries[:5]  # Limit to 5
                else:
                    print(f"Insufficient valid sub-queries, using fallback")
                    return generate_fallback_sub_queries(query)
            else:
                print(f"Invalid response format, using fallback")
                return generate_fallback_sub_queries(query)
                
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}, using fallback")
            return generate_fallback_sub_queries(query)
            
    except Exception as e:
        print(f"Error in Agent 1: {e}")
        return generate_fallback_sub_queries(query)

def generate_fallback_sub_queries(query):
    """
    Fallback sub-queries if LLM fails
    """
    # Simple keyword-based fallback
    query_lower = query.lower()
    if "ai" in query_lower and "healthcare" in query_lower:
        return [
            "AI applications in medical diagnosis",
            "Machine learning in patient care",
            "Ethical considerations of healthcare AI"
        ]
    elif "renewable" in query_lower and "energy" in query_lower:
        return [
            "Solar energy benefits and efficiency",
            "Wind power technology and implementation",
            "Economic impact of renewable energy adoption"
        ]
    else:
        return [
            f"Current state of {query}",
            f"Benefits and advantages of {query}",
            f"Challenges and limitations of {query}"
        ]

def agent2_data_collector(sub_queries):
    """
    Agent 2: Data Collector
    Search and scrape 2-3 web sources per sub-query
    """
    def search_web(query, max_results=3):
        """
        Use Google Custom Search API to find relevant URLs
        Returns: List of search results with title, href, and body
        """
        api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
        search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        
        if not api_key or not search_engine_id:
            print("Google Search API credentials not found. Please add GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_ENGINE_ID to .env")
            return []
        
        try:
            # Google Custom Search API
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': api_key,
                'cx': search_engine_id,
                'q': query,
                'num': max_results
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            if 'items' in data:
                for item in data['items']:
                    results.append({
                        'title': item.get('title', ''),
                        'href': item.get('link', ''),
                        'body': item.get('snippet', '')
                    })
            
            print(f"Google Search found {len(results)} results for: '{query}'")
            return results
            
        except Exception as e:
            print(f"Google Search failed for '{query}': {e}")
            return []

    def scrape_page(url, retries=2):
        """Scrape and clean content from URL"""
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        
        for attempt in range(retries):
            try:
                print(f"Attempting to scrape: {url}")
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove noise
                for tag in ['script', 'style', 'nav', 'header', 'footer']:
                    for elem in soup.find_all(tag):
                        elem.decompose()
                
                # Extract main content
                paragraphs = [p.get_text().strip() for p in soup.find_all('p') if len(p.get_text().strip()) > 100]
                content = ' '.join(paragraphs)
                
                word_count = len(content.split())
                print(f"Scraped content: {word_count} words")
                
                return {
                    'url': url,
                    'title': soup.title.string if soup.title else url,
                    'date': datetime.now().isoformat(),
                    'word_count': word_count,
                    'content': content
                }
            except Exception as e:
                if attempt == retries - 1:
                    print(f"Failed to scrape {url}: {e}")
                time.sleep(1 + random.random())  # Backoff with jitter
        return None

    results = {}
    seen_domains = set()

    for query in sub_queries:
        print(f"\nProcessing sub-query: {query}")
        sources = []
        
        # Get search results for this specific sub-query
        search_results = search_web(query, max_results=5)
        
        for result in search_results:
            url = result.get('href', '')
            if not url:
                continue
                
            domain = urlparse(url).netloc
            if domain in seen_domains:
                continue
                
            # Use the body from search result as initial content
            body = result.get('body', '')
            if len(body.split()) >= 500:  # If search result body is long enough
                sources.append({
                    'url': url,
                    'title': result.get('title', url),
                    'date': datetime.now().isoformat(),
                    'word_count': len(body.split()),
                    'content': body
                })
                seen_domains.add(domain)
                print(f"Used search result body for: {url}")
            else:
                # Try to scrape the full page
                data = scrape_page(url)
                if data and data['word_count'] >= 500:  # Accept any content with 500+ words
                    sources.append(data)
                    seen_domains.add(domain)
                    print(f"Scraped full page for: {url}")
                
            if len(sources) >= 2:  # Stop when we have 2 good sources
                break
                
            time.sleep(1.5 + random.random())  # Rate limiting
        
        if sources:
            results[query] = sources
            print(f"Found {len(sources)} sources for: {query}")
        else:
            print(f"No valid sources found for: {query}")
            
        time.sleep(5 + random.random() * 3)  # 5-8 second delay between queries
    
    return results

def agent3_content_analyzer(scraped_data, original_query):
    """
    Agent 3: Content Analyzer
    Synthesize collected data into coherent summary
    """
    try:
        print(f"\nAgent 3: Analyzing content for '{original_query}'")
        
        if not scraped_data:
            return {
                "original_query": original_query,
                "sub_query_analyses": {},
                "overall_insights": ["No sources found for analysis"],
                "data_gaps": ["No data available to analyze"],
                "recommendations": ["Collect more data sources before analysis"]
            }
        
        sub_query_analyses = {}
        all_content = []
        
        # Analyze each sub-query
        for sub_query, sources in scraped_data.items():
            print(f"  Analyzing sub-query: {sub_query[:60]}...")
            
            if not sources:
                sub_query_analyses[sub_query] = {
                    "summary": "No sources available for this sub-query",
                    "key_findings": [],
                    "evidence": [],
                    "confidence": 0.0
                }
                continue
            
            # Prepare content for analysis (truncate to avoid token limits)
            content_text = ""
            total_chars = 0
            max_chars_per_source = 1500  # Limit each source to ~1500 chars to stay under token limits
            
            for source in sources:
                source_content = source.get('content', 'No content')
                if len(source_content) > max_chars_per_source:
                    source_content = source_content[:max_chars_per_source] + "..."
                
                content_text += f"Source: {source.get('title', 'No title')}\n"
                content_text += f"Content: {source_content}\n\n"
                all_content.append(source_content)
                total_chars += len(source_content)
            
            print(f"    Content prepared: {total_chars} characters (~{total_chars//4} tokens)")
            
            # Analyze this sub-query with LLM
            analysis_prompt = f"""Analyze the following content related to: "{sub_query}"

Content to analyze:
{content_text}

Provide a structured analysis in JSON format with:
{{
    "summary": "A concise summary of the key points",
    "key_findings": ["finding1", "finding2", "finding3"],
    "evidence": ["specific evidence or examples"],
    "confidence": 0.85
}}

Focus on extracting actionable insights and concrete evidence."""
            
            try:
                analysis_response = call_groq_llm(analysis_prompt, max_tokens=800)
                print(f"    LLM Response: {analysis_response[:200]}...")
                
                # Try to parse JSON response
                try:
                    # Clean the response - remove any non-JSON text
                    cleaned_response = analysis_response.strip()
                    if "{" in cleaned_response:
                        start_idx = cleaned_response.find("{")
                        end_idx = cleaned_response.rfind("}") + 1
                        cleaned_response = cleaned_response[start_idx:end_idx]
                    
                    analysis_data = json.loads(cleaned_response)
                    
                    sub_query_analyses[sub_query] = {
                        "summary": analysis_data.get("summary", "Analysis failed"),
                        "key_findings": analysis_data.get("key_findings", []),
                        "evidence": analysis_data.get("evidence", []),
                        "confidence": analysis_data.get("confidence", 0.5)
                    }
                    
                except json.JSONDecodeError as json_err:
                    print(f"    JSON parsing failed: {json_err}")
                    print(f"    Raw response: {analysis_response}")
                    
                    # Fallback: extract what we can from the text
                    sub_query_analyses[sub_query] = {
                        "summary": f"Analysis completed but format invalid: {analysis_response[:100]}...",
                        "key_findings": ["Format parsing failed"],
                        "evidence": ["LLM response not in expected JSON format"],
                        "confidence": 0.3
                    }
                
            except Exception as e:
                print(f"    LLM call failed for sub-query: {e}")
                sub_query_analyses[sub_query] = {
                    "summary": "Analysis failed due to LLM error",
                    "key_findings": [],
                    "evidence": [],
                    "confidence": 0.0
                }
        
        # Generate overall insights
        overall_prompt = f"""Based on the analysis of multiple sub-queries about "{original_query}", 
provide overall insights and recommendations.

Sub-query analyses completed: {len(sub_query_analyses)}

Provide a structured response in JSON format:
{{
    "insights": ["overall insight 1", "overall insight 2"],
    "gaps": ["identified data gaps"],
    "recommendations": ["actionable recommendation 1", "recommendation 2"]
}}

Focus on synthesizing patterns across all sub-queries."""
        
        try:
            overall_response = call_groq_llm(overall_prompt, max_tokens=600)
            print(f"  Overall LLM Response: {overall_response[:200]}...")
            
            try:
                # Clean the response - remove any non-JSON text
                cleaned_response = overall_response.strip()
                if "{" in cleaned_response:
                    start_idx = cleaned_response.find("{")
                    end_idx = cleaned_response.rfind("}") + 1
                    cleaned_response = cleaned_response[start_idx:end_idx]
                
                overall_data = json.loads(cleaned_response)
                
                overall_insights = overall_data.get("insights", ["Analysis completed successfully"])
                data_gaps = overall_data.get("gaps", ["No major gaps identified"])
                recommendations = overall_data.get("recommendations", ["Continue monitoring trends"])
                
            except json.JSONDecodeError as json_err:
                print(f"  Overall JSON parsing failed: {json_err}")
                print(f"  Raw response: {overall_response}")
                
                # Fallback: extract what we can
                overall_insights = ["Analysis completed but format parsing failed"]
                data_gaps = ["Unable to parse LLM response format"]
                recommendations = ["Check LLM response format and retry"]
            
        except Exception as e:
            print(f"  Overall LLM call failed: {e}")
            overall_insights = ["Analysis completed with some errors"]
            data_gaps = ["Unable to identify gaps due to analysis error"]
            recommendations = ["Review and retry analysis if needed"]
        
        result = {
            "original_query": original_query,
            "sub_query_analyses": sub_query_analyses,
            "overall_insights": overall_insights,
            "data_gaps": data_gaps,
            "recommendations": recommendations
        }
        
        print(f"  Analysis complete: {len(sub_query_analyses)} sub-queries analyzed")
        return result
        
    except Exception as e:
        print(f"Error in Agent 3: {e}")
        return {
            "original_query": original_query,
            "sub_query_analyses": {},
            "overall_insights": [f"Analysis failed: {str(e)}"],
            "data_gaps": ["Unable to analyze due to system error"],
            "recommendations": ["Check system logs and retry"]
        }

def agent4_report_generator(structured_content, original_query):
    """
    Agent 4: Report Generator
    Create professional PDF report
    """
    try:
        print(f"\nAgent 4: Generating report for '{original_query}'")
        
        if not structured_content:
            print("No structured content provided for report generation")
            return None
        
        # Extract data from structured content
        sub_query_analyses = structured_content.get("sub_query_analyses", {})
        overall_insights = structured_content.get("overall_insights", [])
        data_gaps = structured_content.get("data_gaps", [])
        recommendations = structured_content.get("recommendations", [])
        
        # Generate report filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_query = "".join(c for c in original_query if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_query = safe_query.replace(' ', '_')[:50]
        filename = f"research_report_{safe_query}_{timestamp}.pdf"
        
        # Create PDF report
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center
        )
        story.append(Paragraph(f"Research Report: {original_query}", title_style))
        story.append(Spacer(1, 20))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        if overall_insights:
            for insight in overall_insights:
                story.append(Paragraph(f"• {insight}", styles['Normal']))
                story.append(Spacer(1, 6))
        else:
            story.append(Paragraph("No overall insights available", styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # Sub-query Analysis
        story.append(Paragraph("Detailed Analysis by Sub-Query", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        for sub_query, analysis in sub_query_analyses.items():
            story.append(Paragraph(f"<b>{sub_query}</b>", styles['Heading3']))
            story.append(Spacer(1, 6))
            
            # Summary
            story.append(Paragraph(f"<b>Summary:</b> {analysis.get('summary', 'No summary available')}", styles['Normal']))
            story.append(Spacer(1, 6))
            
            # Key Findings
            key_findings = analysis.get('key_findings', [])
            if key_findings:
                story.append(Paragraph("<b>Key Findings:</b>", styles['Normal']))
                for finding in key_findings:
                    story.append(Paragraph(f"• {finding}", styles['Normal']))
                    story.append(Spacer(1, 3))
            
            # Evidence
            evidence = analysis.get('evidence', [])
            if evidence:
                story.append(Paragraph("<b>Evidence:</b>", styles['Normal']))
                for ev in evidence:
                    story.append(Paragraph(f"• {ev}", styles['Normal']))
                    story.append(Spacer(1, 3))
            
            # Confidence
            confidence = analysis.get('confidence', 0.0)
            story.append(Paragraph(f"<b>Confidence Level:</b> {confidence:.1%}", styles['Normal']))
            
            story.append(Spacer(1, 15))
        
        # Data Gaps
        if data_gaps:
            story.append(Paragraph("Identified Data Gaps", styles['Heading2']))
            story.append(Spacer(1, 12))
            for gap in data_gaps:
                story.append(Paragraph(f"• {gap}", styles['Normal']))
                story.append(Spacer(1, 6))
            story.append(Spacer(1, 15))
        
        # Recommendations
        if recommendations:
            story.append(Paragraph("Recommendations", styles['Heading2']))
            story.append(Spacer(1, 12))
            for rec in recommendations:
                story.append(Paragraph(f"• {rec}", styles['Normal']))
                story.append(Spacer(1, 6))
            story.append(Spacer(1, 15))
        
        # Metadata
        story.append(Paragraph("Report Metadata", styles['Heading2']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Paragraph(f"<b>Sub-queries Analyzed:</b> {len(sub_query_analyses)}", styles['Normal']))
        story.append(Paragraph(f"<b>Total Sources:</b> {sum(len(sources) for sources in sub_query_analyses.values())}", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        print(f"  Report generated successfully: {filename}")
        return filename
        
    except Exception as e:
        print(f"Error in Agent 4: {e}")
        return None

def run_pipeline(query):
    """
    Main pipeline function that orchestrates all agents
    """
    print(f"Starting research pipeline for query: '{query}'")
    print("=" * 50)
    
    try:
        # Agent 1: Query Processor
        sub_queries = agent1_query_processor(query)
        print(f"Generated {len(sub_queries)} sub-queries:")
        for i, sq in enumerate(sub_queries, 1):
            print(f"  {i}. {sq}")
        
        # Agent 2: Data Collector
        scraped_data = agent2_data_collector(sub_queries)
        total_sources = sum(len(sources) for sources in scraped_data.values())
        print(f"\nCollected data from {total_sources} sources across {len(scraped_data)} sub-queries")
        
        # Agent 3: Content Analyzer
        structured_content = agent3_content_analyzer(scraped_data, query)
        
        # Agent 4: Report Generator
        if structured_content:
            report_file = agent4_report_generator(structured_content, query)
            if report_file:
                print(f"Final report saved as: {report_file}")
            else:
                print("Report generation failed")
        else:
            print("Content analysis failed, skipping report generation")
        
        print("Pipeline completed successfully!")
        return structured_content
        
    except Exception as e:
        print(f"Error in pipeline: {e}")
        return None

if __name__ == "__main__":
    # Test the complete pipeline
    test_query = "Impact of AI in healthcare"
    print("\nTesting Complete Multi-Agent Research Pipeline")
    print("=" * 60)
    
    # Run the full pipeline
    result = run_pipeline(test_query)
    
    if result:
        print(f"\nPipeline completed successfully!")
        print(f"Final result type: {type(result).__name__}")
        if isinstance(result, dict):
            print(f"Keys: {list(result.keys())}")
    else:
        print("\nPipeline failed")