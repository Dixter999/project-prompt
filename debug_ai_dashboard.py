#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Debug script for AI insights dashboard generation.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ui.markdown_dashboard import MarkdownDashboardGenerator
from src.utils.config import ConfigManager
from src.utils.subscription import get_subscription_manager

def debug_ai_dashboard():
    """Debug AI dashboard generation."""
    project_path = "/mnt/h/Projects/project-prompt"
    
    # Setup config
    config = ConfigManager()
    config.set('user.premium', True)
    config.set('api.anthropic.api_key', 'test-key')  # Set a test key
    
    print("🔧 Debugging AI Dashboard Generation...")
    print("=" * 50)
    
    # Check subscription
    subscription = get_subscription_manager()
    premium_available = subscription.is_premium_feature_available('project_dashboard')
    print(f"Premium access available: {premium_available}")
    
    # Initialize generator
    generator = MarkdownDashboardGenerator(project_path, config)
    print(f"AI analyzer initialized: {generator.ai_analyzer is not None}")
    
    if generator.ai_analyzer:
        print(f"AI analyzer configured: {generator.ai_analyzer.anthropic.is_configured}")
        
        # Test AI insights generation
        try:
            print("\n🧠 Testing AI insights...")
            insights = generator.ai_analyzer.generate_ai_insights()
            print(f"Generated {len(insights)} insights")
        except Exception as e:
            print(f"Error generating insights: {e}")
        
        try:
            print("\n📋 Testing AI recommendations...")
            recommendations = generator.ai_analyzer.generate_ai_recommendations()
            print(f"Generated {len(recommendations)} recommendations")
        except Exception as e:
            print(f"Error generating recommendations: {e}")
    
    print("\n📊 Generating dashboard with AI features...")
    try:
        output_path = generator.generate_markdown_dashboard(
            output_path="project-output/analyses/test_ai_dashboard.md",
            premium_mode=True,
            detailed=True
        )
        print(f"✅ Dashboard generated: {output_path}")
        
        # Check if AI sections were included
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            has_ai_insights = "🤖 AI-Powered Insights" in content
            has_ai_recommendations = "📋 Actionable Recommendations" in content
            has_ai_priorities = "🎯 Development Priorities" in content
            
            print(f"AI Insights section: {'✅' if has_ai_insights else '❌'}")
            print(f"AI Recommendations section: {'✅' if has_ai_recommendations else '❌'}")
            print(f"AI Priorities section: {'✅' if has_ai_priorities else '❌'}")
            
    except Exception as e:
        print(f"❌ Error generating dashboard: {e}")

if __name__ == "__main__":
    debug_ai_dashboard()
