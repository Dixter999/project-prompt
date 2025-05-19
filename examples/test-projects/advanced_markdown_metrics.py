#!/usr/bin/env python3
"""
Advanced Markdown Quality Metrics Analyzer

This script provides more detailed metrics for evaluating the quality of generated markdown
from Anthropic. It analyzes structure, content richness, coherence, and technical accuracy.
"""

import os
import sys
import re
import json
import argparse
import logging
from pathlib import Path
import numpy as np
from collections import Counter

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Terminal colors
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
RED = "\033[0;31m"
NC = "\033[0m"  # No Color
BOLD = "\033[1m"

class MarkdownMetricsAnalyzer:
    """Advanced analyzer for markdown quality metrics"""
    
    def __init__(self, markdown_file):
        """Initialize with a markdown file"""
        self.markdown_file = markdown_file
        self.content = self._read_file()
        self.metrics = {}
        self.analyze()
    
    def _read_file(self):
        """Read the markdown file content"""
        try:
            with open(self.markdown_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return ""
    
    def analyze(self):
        """Run all analysis metrics"""
        if not self.content:
            self.metrics = {"error": "Empty file or file could not be read"}
            return self.metrics
        
        # Basic metrics
        self._analyze_basic_metrics()
        
        # Structure metrics
        self._analyze_structure()
        
        # Content richness metrics
        self._analyze_content_richness()
        
        # Technical accuracy metrics
        self._analyze_technical_content()
        
        # Anthropic analysis markers
        self._check_anthropic_content()
        
        # Coherence analysis
        self._analyze_coherence()
        
        # Calculate overall quality score
        self._calculate_quality_score()
        
        return self.metrics
    
    def _analyze_basic_metrics(self):
        """Analyze basic metrics like length, word count, etc."""
        self.metrics["basic"] = {
            "char_count": len(self.content),
            "word_count": len(self.content.split()),
            "line_count": len(self.content.splitlines()),
            "paragraph_count": len(re.split(r'\n\s*\n', self.content)),
        }
    
    def _analyze_structure(self):
        """Analyze the document structure (headings, sections, etc.)"""
        # Extract all headings with their levels
        headings = re.findall(r'^(#+)\s+(.+)$', self.content, re.MULTILINE)
        
        # Count headings by level
        heading_levels = Counter([len(h[0]) for h in headings])
        
        # Extract heading text
        heading_texts = [h[1] for h in headings]
        
        # Check if headings follow a hierarchical structure
        hierarchical = True
        prev_level = 0
        for match in re.finditer(r'^(#+)\s+(.+)$', self.content, re.MULTILINE):
            level = len(match.group(1))
            if prev_level > 0 and level > prev_level + 1:
                hierarchical = False
                break
            prev_level = level
        
        self.metrics["structure"] = {
            "heading_count": len(headings),
            "heading_levels": dict(heading_levels),
            "heading_texts": heading_texts,
            "hierarchical_structure": hierarchical,
            "has_title": bool(re.search(r'^#\s+.+$', self.content, re.MULTILINE)),
        }
        
        # Check for main sections expected in a good analysis
        expected_sections = [
            "resumen|propósito|estructura|introducción",
            "fortalezas|puntos fuertes",
            "debilidades|áreas de mejora",
            "recomendaciones|sugerencias"
        ]
        
        found_sections = []
        for pattern in expected_sections:
            if re.search(r'#+\s+.*(' + pattern + ')', self.content, re.IGNORECASE | re.MULTILINE):
                found_sections.append(pattern.split('|')[0])
        
        self.metrics["structure"]["found_sections"] = found_sections
        self.metrics["structure"]["missing_sections"] = [
            pattern.split('|')[0] for pattern in expected_sections 
            if not re.search(r'#+\s+.*(' + pattern + ')', self.content, re.IGNORECASE | re.MULTILINE)
        ]
    
    def _analyze_content_richness(self):
        """Analyze content richness (code blocks, lists, tables, etc.)"""
        # Code blocks
        code_blocks = re.findall(r'```[\w]*\n[\s\S]*?\n```', self.content)
        code_languages = [
            match.group(1) if match.group(1) else "none" 
            for match in re.finditer(r'```([\w]*)\n', self.content)
        ]
        
        # Lists
        bullet_list_items = re.findall(r'^\s*[*-]\s+.+$', self.content, re.MULTILINE)
        numbered_list_items = re.findall(r'^\s*\d+\.\s+.+$', self.content, re.MULTILINE)
        
        # Tables
        tables = re.findall(r'^\|.+\|$\n^\|[-:| ]+\|$\n(?:^\|.+\|$\n)+', self.content, re.MULTILINE)
        
        # Links
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', self.content)
        
        # Images
        images = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', self.content)
        
        # Blockquotes
        blockquotes = re.findall(r'^>\s+.+$', self.content, re.MULTILINE)
        
        # Bold text
        bold_text = re.findall(r'\*\*([^*]+)\*\*|\b__([^_]+)__\b', self.content)
        
        self.metrics["content_richness"] = {
            "code_blocks": {
                "count": len(code_blocks),
                "languages": Counter(code_languages)
            },
            "lists": {
                "bullet_items": len(bullet_list_items),
                "numbered_items": len(numbered_list_items),
                "total_items": len(bullet_list_items) + len(numbered_list_items)
            },
            "tables": len(tables),
            "links": len(links),
            "images": len(images),
            "blockquotes": len(blockquotes),
            "emphasized_text": len(bold_text)
        }
    
    def _analyze_technical_content(self):
        """Analyze technical content accuracy"""
        # Extract code blocks for analysis
        code_blocks = re.findall(r'```([\w]*)\n([\s\S]*?)\n```', self.content)
        
        tech_terms = [
            "api", "function", "class", "method", "database", "schema",
            "model", "controller", "view", "service", "component", "module",
            "interface", "type", "algorithm", "optimization", "structure",
            "pattern", "architecture", "framework", "library", "dependency",
            "injection", "test", "validation", "authentication", "authorization"
        ]
        
        # Count technical terms
        term_count = {}
        for term in tech_terms:
            pattern = r'\b' + term + r'\b'
            matches = re.findall(pattern, self.content, re.IGNORECASE)
            if matches:
                term_count[term] = len(matches)
        
        # Check for code quality comments
        code_quality_terms = [
            "refactor", "optimize", "simplify", "improve", "clean",
            "maintainable", "readable", "performance", "efficiency", 
            "security", "vulnerability", "bug", "fix", "issue"
        ]
        
        quality_comments = {}
        for term in code_quality_terms:
            pattern = r'\b' + term + r'\b'
            matches = re.findall(pattern, self.content, re.IGNORECASE)
            if matches:
                quality_comments[term] = len(matches)
        
        self.metrics["technical_content"] = {
            "code_blocks": [{
                "language": lang.lower() if lang else "none",
                "content": code,
                "line_count": len(code.splitlines())
            } for lang, code in code_blocks],
            "technical_terms": term_count,
            "code_quality_terms": quality_comments,
            "tech_term_density": sum(term_count.values()) / self.metrics["basic"]["word_count"] if self.metrics["basic"]["word_count"] > 0 else 0
        }
    
    def _check_anthropic_content(self):
        """Check for Anthropic analysis marker"""
        has_anthropic_marker = "Sugerencias de Mejora (Generado por Anthropic Claude)" in self.content
        self.metrics["anthropic"] = {
            "has_marker": has_anthropic_marker,
            "marker_position": self.content.find("Sugerencias de Mejora (Generado por Anthropic Claude)") if has_anthropic_marker else -1
        }
    
    def _analyze_coherence(self):
        """Analyze text coherence and flow"""
        # Simple coherence metrics
        paragraphs = re.split(r'\n\s*\n', self.content)
        paragraph_lengths = [len(p.split()) for p in paragraphs]
        
        # Get sentence lengths as a measure of variability
        sentences = re.split(r'[.!?]+', self.content)
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
        
        # Calculate variance/std deviation of paragraph and sentence length as a proxy for rhythm
        self.metrics["coherence"] = {
            "paragraph_count": len(paragraphs),
            "paragraph_length": {
                "mean": np.mean(paragraph_lengths) if paragraph_lengths else 0,
                "std_dev": np.std(paragraph_lengths) if paragraph_lengths else 0,
                "min": min(paragraph_lengths) if paragraph_lengths else 0,
                "max": max(paragraph_lengths) if paragraph_lengths else 0
            },
            "sentence_count": len(sentence_lengths),
            "sentence_length": {
                "mean": np.mean(sentence_lengths) if sentence_lengths else 0,
                "std_dev": np.std(sentence_lengths) if sentence_lengths else 0,
                "min": min(sentence_lengths) if sentence_lengths else 0,
                "max": max(sentence_lengths) if sentence_lengths else 0
            }
        }
    
    def _calculate_quality_score(self):
        """Calculate an overall quality score"""
        score = 0
        max_score = 100
        
        # Structure score (max 25)
        structure_score = 0
        if self.metrics["structure"]["has_title"]:
            structure_score += 5
        
        # Award points for each expected section found
        structure_score += min(15, len(self.metrics["structure"]["found_sections"]) * 4)
        
        # Award points for hierarchical structure
        if self.metrics["structure"]["hierarchical_structure"]:
            structure_score += 5
        
        # Content richness score (max 30)
        richness_score = 0
        
        # Code blocks
        richness_score += min(10, self.metrics["content_richness"]["code_blocks"]["count"] * 3)
        
        # Lists
        richness_score += min(8, self.metrics["content_richness"]["lists"]["total_items"] * 0.5)
        
        # Tables
        richness_score += min(5, self.metrics["content_richness"]["tables"] * 2)
        
        # Links
        richness_score += min(3, self.metrics["content_richness"]["links"])
        
        # Emphasized text
        richness_score += min(4, self.metrics["content_richness"]["emphasized_text"] * 0.5)
        
        # Technical content score (max 25)
        tech_score = 0
        
        # Code quality terms
        tech_score += min(10, sum(self.metrics["technical_content"]["code_quality_terms"].values()) * 0.8)
        
        # Technical term density
        tech_density = self.metrics["technical_content"]["tech_term_density"]
        if tech_density > 0.05:
            tech_score += 15
        elif tech_density > 0.03:
            tech_score += 10
        elif tech_density > 0.01:
            tech_score += 5
        
        # Anthropic content score (max 10)
        anthropic_score = 10 if self.metrics["anthropic"]["has_marker"] else 0
        
        # Coherence score (max 10)
        coherence_score = 0
        
        # Sentence length variation (good for readability)
        sent_std_dev = self.metrics["coherence"]["sentence_length"]["std_dev"]
        if sent_std_dev > 3 and sent_std_dev < 10:
            coherence_score += 5
        else:
            coherence_score += 2
        
        # Paragraph length
        para_mean = self.metrics["coherence"]["paragraph_length"]["mean"]
        if 30 > para_mean > 10:
            coherence_score += 5
        else:
            coherence_score += 2
        
        # Final score
        total_score = structure_score + richness_score + tech_score + anthropic_score + coherence_score
        
        self.metrics["quality_score"] = {
            "total": min(total_score, max_score),  # Cap at max
            "max_possible": max_score,
            "percentage": (min(total_score, max_score) / max_score) * 100,
            "components": {
                "structure": structure_score,
                "content_richness": richness_score,
                "technical_content": tech_score,
                "anthropic": anthropic_score,
                "coherence": coherence_score
            },
            "rating": self._get_rating(min(total_score, max_score) / max_score)
        }
    
    def _get_rating(self, score_percentage):
        """Convert numeric score to qualitative rating"""
        if score_percentage >= 0.9:
            return "Excellent"
        elif score_percentage >= 0.8:
            return "Very Good"
        elif score_percentage >= 0.7:
            return "Good"
        elif score_percentage >= 0.6:
            return "Satisfactory"
        elif score_percentage >= 0.5:
            return "Adequate"
        else:
            return "Poor"
    
    def print_summary(self):
        """Print a summary of the analysis results"""
        if "error" in self.metrics:
            print(f"{RED}Error: {self.metrics['error']}{NC}")
            return
        
        print(f"\n{BOLD}{'=' * 60}{NC}")
        print(f"{BOLD}MARKDOWN QUALITY ANALYSIS: {Path(self.markdown_file).name}{NC}")
        print(f"{BOLD}{'=' * 60}{NC}\n")
        
        # Basic metrics
        print(f"{BOLD}Basic Metrics{NC}")
        print(f"Word count: {self.metrics['basic']['word_count']}")
        print(f"Line count: {self.metrics['basic']['line_count']}")
        print(f"Paragraph count: {self.metrics['basic']['paragraph_count']}")
        
        # Structure
        print(f"\n{BOLD}Structure{NC}")
        print(f"Headings: {self.metrics['structure']['heading_count']}")
        print(f"Has title: {'✅' if self.metrics['structure']['has_title'] else '❌'}")
        print(f"Hierarchical structure: {'✅' if self.metrics['structure']['hierarchical_structure'] else '❌'}")
        
        print("\nFound sections:")
        for section in self.metrics['structure']['found_sections']:
            print(f"  ✅ {section.capitalize()}")
        
        print("\nMissing sections:")
        if self.metrics['structure']['missing_sections']:
            for section in self.metrics['structure']['missing_sections']:
                print(f"  ❌ {section.capitalize()}")
        else:
            print("  None - All expected sections found")
        
        # Content richness
        print(f"\n{BOLD}Content Richness{NC}")
        print(f"Code blocks: {self.metrics['content_richness']['code_blocks']['count']}")
        print(f"List items: {self.metrics['content_richness']['lists']['total_items']}")
        print(f"Tables: {self.metrics['content_richness']['tables']}")
        print(f"Links: {self.metrics['content_richness']['links']}")
        
        # Technical content
        print(f"\n{BOLD}Technical Content{NC}")
        print(f"Technical term density: {self.metrics['technical_content']['tech_term_density']:.2%}")
        if self.metrics['technical_content']['code_blocks']:
            print("\nCode blocks:")
            for i, block in enumerate(self.metrics['technical_content']['code_blocks'][:3]):
                print(f"  {i+1}. {block['language']} ({block['line_count']} lines)")
            if len(self.metrics['technical_content']['code_blocks']) > 3:
                print(f"  ... and {len(self.metrics['technical_content']['code_blocks'])-3} more")
        
        # Anthropic marker
        print(f"\n{BOLD}Anthropic Content{NC}")
        if self.metrics['anthropic']['has_marker']:
            print(f"{GREEN}✅ Anthropic marker found{NC}")
        else:
            print(f"{RED}❌ No Anthropic marker found{NC}")
        
        # Quality score
        score = self.metrics['quality_score']
        score_color = GREEN if score['percentage'] >= 70 else (YELLOW if score['percentage'] >= 50 else RED)
        
        print(f"\n{BOLD}Quality Score{NC}")
        print(f"Overall: {score_color}{score['total']}/{score['max_possible']} ({score['percentage']:.1f}%){NC}")
        print(f"Rating: {score_color}{score['rating']}{NC}")
        
        print("\nScore components:")
        print(f"  Structure: {score['components']['structure']}/25")
        print(f"  Content richness: {score['components']['content_richness']}/30")
        print(f"  Technical content: {score['components']['technical_content']}/25")
        print(f"  Anthropic marker: {score['components']['anthropic']}/10")
        print(f"  Coherence: {score['components']['coherence']}/10")
        
        print(f"\n{BOLD}{'=' * 60}{NC}")
        
        # Final recommendation
        if score['percentage'] >= 70:
            print(f"{GREEN}✅ This markdown meets the quality standards for Anthropic generation.{NC}")
        elif score['percentage'] >= 50:
            print(f"{YELLOW}⚠️ This markdown partially meets the quality standards but could be improved.{NC}")
        else:
            print(f"{RED}❌ This markdown does not meet the minimum quality standards.{NC}")
        
        print(f"{BOLD}{'=' * 60}{NC}\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Analyze markdown quality with detailed metrics')
    parser.add_argument('file', help='Markdown file to analyze')
    parser.add_argument('-o', '--output', help='Output JSON file for metrics')
    parser.add_argument('--html', help='Output HTML report')
    parser.add_argument('-q', '--quiet', action='store_true', help='Suppress console output')
    
    args = parser.parse_args()
    
    # Check if file exists
    if not os.path.exists(args.file):
        print(f"{RED}Error: File not found: {args.file}{NC}")
        return 1
    
    # Analyze the file
    analyzer = MarkdownMetricsAnalyzer(args.file)
    
    # Print summary unless quiet mode
    if not args.quiet:
        analyzer.print_summary()
    
    # Save metrics to JSON file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(analyzer.metrics, f, indent=2)
        if not args.quiet:
            print(f"Metrics saved to: {args.output}")
    
    # Generate HTML report if requested
    if args.html:
        try:
            from jinja2 import Template
            # This would generate an HTML report using the metrics
            # Implementation skipped for brevity but would use Jinja2 templates
            print(f"HTML report would be saved to: {args.html}")
        except ImportError:
            print(f"{RED}Error: Jinja2 is required for HTML reports. Install with 'pip install jinja2'{NC}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
