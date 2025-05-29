#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for AI insights functionality.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.analyzers.ai_insights_analyzer_lightweight import AIInsightsAnalyzer
from src.utils.config import ConfigManager
from src.utils.logger import get_logger

logger = get_logger()

def test_ai_insights():
    """Test AI insights generation."""
    project_path = "/mnt/h/Projects/project-prompt"
    
    # Initialize the analyzer
    config = ConfigManager()
    analyzer = AIInsightsAnalyzer(project_path, config)
    
    print("🤖 Testing AI Insights Analyzer...")
    print("=" * 50)
    
    # Test project data gathering
    print("\n📊 Testing project data gathering...")
    try:
        project_data = analyzer._gather_project_data()
        print(f"✅ Project data gathered successfully")
        print(f"   - Total files: {project_data['project_info']['total_files']}")
        print(f"   - Lines of code: {project_data['project_info']['lines_of_code']}")
        print(f"   - Main functionalities: {len(project_data['functionality']['main_functionalities'])}")
        for func in project_data['functionality']['main_functionalities']:
            print(f"     • {func}")
    except Exception as e:
        print(f"❌ Error gathering project data: {e}")
        return False
    
    # Test AI insights generation
    print("\n🧠 Testing AI insights generation...")
    try:
        insights = analyzer.generate_ai_insights()
        print(f"✅ Generated {len(insights)} insights")
        for i, insight in enumerate(insights, 1):
            print(f"   {i}. [{insight.category}] {insight.title}")
            print(f"      Impact: {insight.impact}, Effort: {insight.effort}, Priority: {insight.priority}")
    except Exception as e:
        print(f"❌ Error generating AI insights: {e}")
    
    # Test AI recommendations generation
    print("\n📋 Testing AI recommendations generation...")
    try:
        recommendations = analyzer.generate_ai_recommendations()
        print(f"✅ Generated {len(recommendations)} recommendations")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec.title}")
            print(f"      Priority: {rec.priority}, Effort: {rec.estimated_effort}")
            print(f"      Action items: {len(rec.action_items)}")
    except Exception as e:
        print(f"❌ Error generating AI recommendations: {e}")
    
    # Test development priorities
    print("\n🎯 Testing development priorities generation...")
    try:
        priorities = analyzer.get_development_priorities()
        print(f"✅ Generated {len(priorities)} development priorities")
        for i, priority in enumerate(priorities, 1):
            print(f"   {i}. {priority['title']} (Priority: {priority['priority']}, Effort: {priority['effort']})")
    except Exception as e:
        print(f"❌ Error generating development priorities: {e}")
    
    print("\n🎉 AI Insights test completed!")
    return True

if __name__ == "__main__":
    test_ai_insights()
