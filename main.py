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
    print("❌ GROQ_API_KEY not found in environment variables")
    print("Please check your .env file contains: GROQ_API_KEY=your_actual_key")
    exit(1)
else:
    print(f"✅ GROQ API key loaded successfully (length: {len(groq_api_key)})")

if not google_api_key or not google_search_engine_id:
    print("⚠️ Google Search API credentials not found")
    print("Please add GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_ENGINE_ID to .env")
    print("Google Search functionality will be limited")
else:
    print(f"✅ Google Search API credentials loaded successfully")

# Initialize Groq client
groq_client = Groq(api_key=groq_api_key)

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
    def search_web(query, max_results=3):
        """
        Use Google Custom Search API to find relevant URLs
        Returns: List of search results with title, href, and body
        """
        api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
        search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        
        if not api_key or not search_engine_id:
            print("⚠️ Google Search API credentials not found. Please add GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_ENGINE_ID to .env")
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
                print(f"✅ Used search result body for: {url}")
            else:
                # Try to scrape the full page
                data = scrape_page(url)
                if data and 500 <= data['word_count'] <= 1000:
                    sources.append(data)
                    seen_domains.add(domain)
                    print(f"✅ Scraped full page for: {url}")
                
            if len(sources) >= 2:  # Stop when we have 2 good sources
                break
                
            time.sleep(1.5 + random.random())  # Rate limiting
        
        if sources:
            results[query] = sources
            print(f"✅ Found {len(sources)} sources for: {query}")
        else:
            print(f"⚠️ No valid sources found for: {query}")
            
        time.sleep(5 + random.random() * 3)  # 5-8 second delay between queries
    
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