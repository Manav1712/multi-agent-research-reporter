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

# Debug: Check if API key is loaded
api_key = os.getenv('GROQ_API_KEY')
if not api_key:
    print("❌ GROQ_API_KEY not found in environment variables")
    print("Please check your .env file contains: GROQ_API_KEY=your_actual_key")
    exit(1)
else:
    print(f"✅ API key loaded successfully (length: {len(api_key)})")

# Initialize Groq client
groq_client = Groq(api_key=api_key)

def call_groq_llm(prompt, max_tokens=1000, retries=3):
    """
    Helper function to make Groq LLM calls with retry logic
    """
    for attempt in range(retries):
        try:
            response = groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
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

Return only the JSON array of sub-queries, no other text."""

    try:
        response = call_groq_llm(prompt, max_tokens=500)
        
        # Parse JSON response
        try:
            sub_queries = json.loads(response)
            if isinstance(sub_queries, list) and 3 <= len(sub_queries) <= 5:
                print(f"✅ Generated {len(sub_queries)} sub-queries")
                return sub_queries
            else:
                print(f"⚠️ Invalid response format, using fallback")
                return generate_fallback_sub_queries(query)
        except json.JSONDecodeError:
            print(f"⚠️ Failed to parse JSON, using fallback")
            return generate_fallback_sub_queries(query)
            
    except Exception as e:
        print(f"❌ Error in Agent 1: {e}")
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
    def search_web(query):
        """Test function with real URLs"""
        return [
            "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11582508/",
            "https://www.mdpi.com/2075-1729/14/5/557",
            "https://www.scirp.org/journal/paperinformation?paperid=130372"
        ]

    def scrape_url(url, retries=2):
        """Scrape and clean content from URL"""
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        
        for attempt in range(retries):
            try:
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
                
                return {
                    'url': url,
                    'title': soup.title.string if soup.title else url,
                    'date': datetime.now().isoformat(),
                    'word_count': len(content.split()),
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
        print(f"\nProcessing: {query}")
        sources = []
        
        for url in search_web(query):
            domain = urlparse(url).netloc
            if domain in seen_domains:
                continue
                
            data = scrape_url(url)
            if data and 500 <= data['word_count'] <= 1000:
                sources.append(data)
                seen_domains.add(domain)
                
                if len(sources) >= 2:
                    break
                    
            time.sleep(1.5 + random.random())  # Rate limiting
        
        if sources:
            results[query] = sources
            print(f"✅ Found {len(sources)} sources")
        else:
            print(f"⚠️ No valid sources found")
            
        time.sleep(2)  # Delay between queries
    
    return results

def agent3_content_analyzer(scraped_data, original_query):
    """
    Agent 3: Content Analyzer
    Synthesize collected data into coherent summary
    """
    # TODO: Implement
    pass

def agent4_report_generator(structured_content, original_query):
    """
    Agent 4: Report Generator
    Create professional PDF report
    """
    # TODO: Implement
    pass

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
        
        # TODO: Implement remaining agents
        print("Pipeline completed successfully!")
        return scraped_data
        
    except Exception as e:
        print(f"Error in pipeline: {e}")
        return None

if __name__ == "__main__":
    # Test Agent 2 with healthcare query
    test_query = "Impact of AI in healthcare"
    print("\nTesting with query:", test_query)
    
    # First get sub-queries from Agent 1
    sub_queries = agent1_query_processor(test_query)
    print("\nGenerated sub-queries:")
    for i, sq in enumerate(sub_queries, 1):
        print(f"{i}. {sq}")
    
    # Then test Agent 2
    print("\nTesting Agent 2 - Data Collection:")
    scraped_data = agent2_data_collector(sub_queries)
    
    # Display results
    print("\nResults Summary:")
    for query, sources in scraped_data.items():
        print(f"\nQuery: {query}")
        for i, source in enumerate(sources, 1):
            print(f"Source {i}:")
            print(f"  URL: {source['url']}")
            print(f"  Title: {source['title']}")
            print(f"  Word Count: {source['word_count']}")
            print(f"  Content Preview: {source['content'][:150]}...")