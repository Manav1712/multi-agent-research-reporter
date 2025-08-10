#!/usr/bin/env python3
"""
Demo script to test Agent 3 with real data collection
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import agent2_data_collector, agent3_content_analyzer

def test_agent3_with_real_data():
    """Test Agent 3 with real data collection from Agent 2"""
    
    # Test query
    test_query = "AI in healthcare benefits and challenges"
    
    print(f"🔍 Testing Agent 3 with query: {test_query}")
    print("=" * 60)
    
    # Step 1: Collect data using Agent 2
    print("\n📊 Step 1: Agent 2 - Data Collection")
    print("-" * 40)
    
    scraped_data = agent2_data_collector(test_query)
    
    if not scraped_data:
        print("❌ No data collected by Agent 2")
        return
    
    print(f"✅ Agent 2 collected data for {len(scraped_data)} sub-queries")
    
    # Step 2: Analyze content using Agent 3
    print("\n🧠 Step 2: Agent 3 - Content Analysis")
    print("-" * 40)
    
    analysis_result = agent3_content_analyzer(scraped_data, test_query)
    
    # Display results
    print("\n📋 Analysis Results:")
    print("=" * 60)
    
    print(f"Original Query: {analysis_result['original_query']}")
    print(f"Sub-queries Analyzed: {len(analysis_result['sub_query_analyses'])}")
    
    print("\n🔍 Sub-query Analyses:")
    for sub_query, analysis in analysis_result['sub_query_analyses'].items():
        print(f"\n  Sub-query: {sub_query[:80]}...")
        print(f"    Summary: {analysis['summary'][:100]}...")
        print(f"    Key Findings: {len(analysis['key_findings'])} findings")
        print(f"    Evidence: {len(analysis['evidence'])} pieces")
        print(f"    Confidence: {analysis['confidence']:.2f}")
    
    print(f"\n💡 Overall Insights ({len(analysis_result['overall_insights'])}):")
    for i, insight in enumerate(analysis_result['overall_insights'], 1):
        print(f"  {i}. {insight}")
    
    print(f"\n⚠️ Data Gaps ({len(analysis_result['data_gaps'])}):")
    for i, gap in enumerate(analysis_result['data_gaps'], 1):
        print(f"  {i}. {gap}")
    
    print(f"\n🎯 Recommendations ({len(analysis_result['recommendations'])}):")
    for i, rec in enumerate(analysis_result['recommendations'], 1):
        print(f"  {i}. {rec}")

if __name__ == "__main__":
    test_agent3_with_real_data()
