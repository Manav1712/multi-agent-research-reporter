#!/usr/bin/env python3
"""
Tests for Agent 3: Content Analyzer
Tests the content analysis and synthesis functionality
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add the current directory to Python path to import main
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import agent3_content_analyzer

class TestAgent3ContentAnalyzer(unittest.TestCase):
    """Test cases for Agent 3 Content Analyzer"""
    
    def setUp(self):
        """Set up test data"""
        self.sample_scraped_data = {
            "What are the definitions of AI and its applications in the healthcare industry?": [
                {
                    'url': 'https://example1.com',
                    'title': 'AI in Healthcare: Definitions and Applications',
                    'date': '2025-08-09T23:00:00',
                    'word_count': 738,
                    'content': 'Artificial Intelligence (AI) in healthcare refers to the use of machine learning algorithms and software to analyze complex medical data. AI applications include medical imaging analysis, drug discovery, and patient care optimization.'
                }
            ],
            "What are the benefits and drawbacks of implementing AI in healthcare systems?": [
                {
                    'url': 'https://example2.com',
                    'title': 'AI Healthcare Pros and Cons',
                    'date': '2025-08-09T23:00:00',
                    'word_count': 940,
                    'content': 'Benefits of AI in healthcare include improved diagnostic accuracy, reduced medical errors, and increased efficiency. However, challenges include data privacy concerns, high implementation costs, and potential job displacement.'
                },
                {
                    'url': 'https://example3.com',
                    'title': 'AI Healthcare Challenges',
                    'date': '2025-08-09T23:00:00',
                    'word_count': 792,
                    'content': 'The main drawbacks of AI in healthcare are ethical concerns about patient data, regulatory compliance issues, and the need for extensive training of medical staff to use AI systems effectively.'
                }
            ]
        }
        
        self.original_query = "Impact of AI in healthcare"
        
        self.expected_output_structure = {
            "original_query": str,
            "sub_query_analyses": dict,
            "overall_insights": list,
            "data_gaps": list,
            "recommendations": list
        }

    def test_agent3_returns_correct_structure(self):
        """Test that Agent 3 returns the expected output structure"""
        with patch('main.call_groq_llm') as mock_llm:
            # Mock LLM responses for different analysis steps
            mock_llm.side_effect = [
                # Mock response for content synthesis
                json.dumps({
                    "summary": "AI in healthcare involves machine learning for medical data analysis",
                }),
                # Mock response for key findings
                json.dumps({
                    "key_findings": ["AI improves diagnostic accuracy", "Data privacy concerns exist"]
                }),
                # Mock response for overall insights
                json.dumps({
                    "insights": ["AI is transforming healthcare", "Implementation challenges remain"]
                })
            ]
            
            result = agent3_content_analyzer(self.sample_scraped_data, self.original_query)
            
            # Check basic structure
            self.assertIsInstance(result, dict)
            self.assertIn("original_query", result)
            self.assertIn("sub_query_analyses", result)
            self.assertIn("overall_insights", result)
            self.assertIn("data_gaps", result)
            self.assertIn("recommendations", result)

    def test_agent3_handles_empty_data(self):
        """Test that Agent 3 handles empty scraped data gracefully"""
        empty_data = {}
        
        with patch('main.call_groq_llm') as mock_llm:
            mock_llm.return_value = json.dumps({
                "summary": "No data available",
                "key_findings": [],
                "insights": ["No sources found for analysis"]
            })
            
            result = agent3_content_analyzer(empty_data, self.original_query)
            
            self.assertEqual(result["original_query"], self.original_query)
            self.assertEqual(result["sub_query_analyses"], {})
            self.assertIn("No sources found", str(result["overall_insights"]))

    def test_agent3_handles_single_source(self):
        """Test that Agent 3 works with single source per sub-query"""
        single_source_data = {
            "What is AI?": [
                {
                    'url': 'https://example.com',
                    'title': 'AI Definition',
                    'date': '2025-08-09T23:00:00',
                    'word_count': 500,
                    'content': 'Artificial Intelligence is the simulation of human intelligence in machines.'
                }
            ]
        }
        
        with patch('main.call_groq_llm') as mock_llm:
            mock_llm.return_value = json.dumps({
                "summary": "AI is machine simulation of human intelligence",
                "key_findings": ["AI mimics human thinking"]
            })
            
            result = agent3_content_analyzer(single_source_data, "What is AI?")
            
            self.assertIn("What is AI?", result["sub_query_analyses"])
            self.assertIsInstance(result["sub_query_analyses"]["What is AI?"], dict)

    def test_agent3_handles_multiple_sources(self):
        """Test that Agent 3 properly synthesizes multiple sources"""
        multi_source_data = {
            "AI benefits": [
                {
                    'url': 'https://source1.com',
                    'title': 'AI Benefits Source 1',
                    'content': 'AI improves efficiency by 30%'
                },
                {
                    'url': 'https://source2.com', 
                    'title': 'AI Benefits Source 2',
                    'content': 'AI reduces costs by 25%'
                }
            ]
        }
        
        with patch('main.call_groq_llm') as mock_llm:
            mock_llm.return_value = json.dumps({
                "summary": "AI provides efficiency and cost benefits",
                "key_findings": ["30% efficiency improvement", "25% cost reduction"]
            })
            
            result = agent3_content_analyzer(multi_source_data, "AI benefits")
            
            analysis = result["sub_query_analyses"]["AI benefits"]
            self.assertIn("summary", analysis)
            self.assertIn("key_findings", analysis)

    def test_agent3_handles_llm_failures(self):
        """Test that Agent 3 handles LLM call failures gracefully"""
        with patch('main.call_groq_llm') as mock_llm:
            mock_llm.side_effect = Exception("LLM service unavailable")
            
            result = agent3_content_analyzer(self.sample_scraped_data, self.original_query)
            
            # Should return fallback analysis
            self.assertIsInstance(result, dict)
            self.assertIn("error", str(result).lower() or "fallback" in str(result).lower())

    def test_agent3_output_data_types(self):
        """Test that Agent 3 returns correct data types"""
        with patch('main.call_groq_llm') as mock_llm:
            mock_llm.side_effect = [
                json.dumps({"summary": "Test summary"}),
                json.dumps({"key_findings": ["finding1", "finding2"]}),
                json.dumps({"insights": ["insight1"]})
            ]
            
            result = agent3_content_analyzer(self.sample_scraped_data, self.original_query)
            
            # Check data types
            self.assertIsInstance(result["original_query"], str)
            self.assertIsInstance(result["sub_query_analyses"], dict)
            self.assertIsInstance(result["overall_insights"], list)
            self.assertIsInstance(result["data_gaps"], list)
            self.assertIsInstance(result["recommendations"], list)

    def test_agent3_preserves_original_query(self):
        """Test that Agent 3 preserves the original query"""
        with patch('main.call_groq_llm') as mock_llm:
            mock_llm.return_value = json.dumps({
                "summary": "Test summary",
                "key_findings": ["Test finding"]
            })
            
            result = agent3_content_analyzer(self.sample_scraped_data, self.original_query)
            
            self.assertEqual(result["original_query"], self.original_query)

if __name__ == "__main__":
    unittest.main()
