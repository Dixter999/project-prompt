#!/usr/bin/env python3
"""
Rules Report Generator for ProjectPrompt

This module provides comprehensive reporting capabilities for project rules
compliance, violations, and overall project health metrics.
"""

import os
import json
import html
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass

from src.models.rule_models import RuleItem, RuleCategory, RulePriority
from src.utils.enhanced_rules_manager import EnhancedRulesManager
from src.utils.logger import get_logger

logger = get_logger()


@dataclass
class RuleViolation:
    """Represents a rule violation"""
    rule_name: str
    rule_priority: str
    rule_category: str
    violation_type: str
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    suggestion: Optional[str] = None
    severity: str = "medium"


@dataclass
class ComplianceScore:
    """Represents compliance scoring"""
    total_rules: int
    passed_rules: int
    failed_rules: int
    warnings: int
    score_percentage: float
    grade: str


class RulesReportGenerator:
    """Generates comprehensive reports for rules compliance"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.rules_manager = EnhancedRulesManager(project_root)
        self.violations: List[RuleViolation] = []
        self.compliance_score: Optional[ComplianceScore] = None
        
    def generate_report(self, output_format: str = "markdown", output_file: Optional[str] = None) -> str:
        """Generate a comprehensive rules compliance report"""
        try:
            # Analyze project compliance
            self._analyze_compliance()
            
            # Generate report content
            if output_format.lower() == "json":
                content = self._generate_json_report()
            elif output_format.lower() == "html":
                content = self._generate_html_report()
            else:  # Default to markdown
                content = self._generate_markdown_report()
            
            # Save to file if specified
            if output_file:
                output_path = Path(self.project_root) / output_file
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Report saved to: {output_path}")
            
            return content
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            raise
    
    def _analyze_compliance(self):
        """Analyze project compliance with rules"""
        try:
            # Load rules
            rules = self.rules_manager.load_rules()
            if not rules:
                logger.warning("No rules found for compliance analysis")
                return
            
            # Reset violations
            self.violations = []
            
            # Check each rule
            passed_count = 0
            warning_count = 0
            
            for rule in rules:
                violations = self._check_rule_compliance(rule)
                
                if violations:
                    self.violations.extend(violations)
                    if rule.priority == RulePriority.MANDATORY:
                        # Mandatory rule failed
                        pass
                    else:
                        warning_count += len(violations)
                else:
                    passed_count += 1
            
            # Calculate compliance score
            total_rules = len(rules)
            failed_rules = len([v for v in self.violations if v.severity == "high"])
            warnings = len([v for v in self.violations if v.severity == "medium"])
            
            # Calculate percentage (mandatory failures count more)
            score = (passed_count / total_rules) * 100 if total_rules > 0 else 100
            
            # Adjust score based on violations
            mandatory_penalty = len([v for v in self.violations if v.rule_priority == "MANDATORY"]) * 10
            recommended_penalty = len([v for v in self.violations if v.rule_priority == "RECOMMENDED"]) * 5
            
            adjusted_score = max(0, score - mandatory_penalty - recommended_penalty)
            
            # Determine grade
            if adjusted_score >= 90:
                grade = "A"
            elif adjusted_score >= 80:
                grade = "B"
            elif adjusted_score >= 70:
                grade = "C"
            elif adjusted_score >= 60:
                grade = "D"
            else:
                grade = "F"
            
            self.compliance_score = ComplianceScore(
                total_rules=total_rules,
                passed_rules=passed_count,
                failed_rules=failed_rules,
                warnings=warnings,
                score_percentage=adjusted_score,
                grade=grade
            )
            
        except Exception as e:
            logger.error(f"Error in compliance analysis: {e}")
            raise
    
    def _check_rule_compliance(self, rule: RuleItem) -> List[RuleViolation]:
        """Check compliance for a specific rule"""
        violations = []
        
        try:
            # This is a simplified compliance check
            # In a real implementation, this would use specific analyzers
            # based on rule type and content
            
            # Since RuleItem doesn't have rule_type, we'll infer from category and content
            category = rule.category.value.lower()
            content_lower = rule.content.lower()
            
            if 'file' in content_lower or 'directory' in content_lower:
                violations.extend(self._check_file_structure_rule(rule))
            elif category == 'technology' or 'dependency' in content_lower:
                violations.extend(self._check_technology_rule(rule))
            elif category == 'code_style' or 'style' in content_lower:
                violations.extend(self._check_code_style_rule(rule))
            elif category == 'testing' or 'test' in content_lower:
                violations.extend(self._check_testing_rule(rule))
            elif category == 'documentation' or 'doc' in content_lower:
                violations.extend(self._check_documentation_rule(rule))
            elif 'security' in content_lower or 'secure' in content_lower:
                violations.extend(self._check_security_rule(rule))
            
        except Exception as e:
            logger.error(f"Error checking rule {rule.description or rule.content[:50]}: {e}")
            # Create a violation for the error
            violations.append(RuleViolation(
                rule_name=rule.description or rule.content[:50] + "...",
                rule_priority=rule.priority.value,
                rule_category=rule.category.value,
                violation_type="analysis_error",
                description=f"Error analyzing rule: {str(e)}",
                severity="low"
            ))
        
        return violations
    
    def _check_file_structure_rule(self, rule: RuleItem) -> List[RuleViolation]:
        """Check file structure rules"""
        violations = []
        
        # Example: Check for required files/directories
        if "must have" in rule.content.lower():
            # Extract required files from rule content
            required_items = self._extract_required_items(rule.content)
            
            for item in required_items:
                item_path = Path(self.project_root) / item
                if not item_path.exists():
                    violations.append(RuleViolation(
                        rule_name=rule.description or rule.content[:50] + "...",
                        rule_priority=rule.priority.value,
                        rule_category=rule.category.value,
                        violation_type="missing_file",
                        description=f"Required file/directory '{item}' is missing",
                        file_path=str(item_path),
                        severity="high" if rule.priority == RulePriority.MANDATORY else "medium",
                        suggestion=f"Create the required file/directory: {item}"
                    ))
        
        return violations
    
    def _check_technology_rule(self, rule: RuleItem) -> List[RuleViolation]:
        """Check technology stack rules"""
        violations = []
        
        # Example: Check for package.json dependencies
        if "package.json" in rule.content and "dependencies" in rule.content:
            package_json = Path(self.project_root) / "package.json"
            if package_json.exists():
                try:
                    with open(package_json, 'r') as f:
                        data = json.load(f)
                    
                    # Check for specific dependencies mentioned in rule
                    required_deps = self._extract_dependencies(rule.content)
                    existing_deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                    
                    for dep in required_deps:
                        if dep not in existing_deps:
                            violations.append(RuleViolation(
                                rule_name=rule.description or rule.content[:50] + "...",
                                rule_priority=rule.priority.value,
                                rule_category=rule.category.value,
                                violation_type="missing_dependency",
                                description=f"Required dependency '{dep}' is missing",
                                file_path="package.json",
                                severity="medium",
                                suggestion=f"Add dependency: npm install {dep}"
                            ))
                            
                except Exception as e:
                    violations.append(RuleViolation(
                        rule_name=rule.description or rule.content[:50] + "...",
                        rule_priority=rule.priority.value,
                        rule_category=rule.category.value,
                        violation_type="analysis_error",
                        description=f"Error reading package.json: {str(e)}",
                        file_path="package.json",
                        severity="low"
                    ))
        
        return violations
    
    def _check_code_style_rule(self, rule: RuleItem) -> List[RuleViolation]:
        """Check code style rules"""
        violations = []
        
        # Example: Check for specific configuration files
        config_files = {
            'eslint': ['.eslintrc.js', '.eslintrc.json', '.eslintrc.yml'],
            'prettier': ['.prettierrc', '.prettierrc.json', '.prettierrc.yml'],
            'black': ['pyproject.toml', 'setup.cfg'],
            'flake8': ['.flake8', 'setup.cfg', 'tox.ini']
        }
        
        for tool, possible_files in config_files.items():
            if tool in rule.content.lower():
                found = any(Path(self.project_root) / f for f in possible_files if (Path(self.project_root) / f).exists())
                
                if not found and "required" in rule.content.lower():
                    violations.append(RuleViolation(
                        rule_name=rule.description or rule.content[:50] + "...",
                        rule_priority=rule.priority.value,
                        rule_category=rule.category.value,
                        violation_type="missing_config",
                        description=f"Required {tool} configuration file is missing",
                        severity="medium",
                        suggestion=f"Create a {tool} configuration file: {possible_files[0]}"
                    ))
        
        return violations
    
    def _check_testing_rule(self, rule: RuleItem) -> List[RuleViolation]:
        """Check testing rules"""
        violations = []
        
        # Check for test directories and files
        test_patterns = ['test/', 'tests/', '__tests__/', '*test.py', '*test.js', '*.spec.js']
        found_tests = False
        
        for pattern in test_patterns:
            test_files = list(Path(self.project_root).rglob(pattern))
            if test_files:
                found_tests = True
                break
        
        if not found_tests and "required" in rule.content.lower():
            violations.append(RuleViolation(
                rule_name=rule.description or rule.content[:50] + "...",
                rule_priority=rule.priority.value,
                rule_category=rule.category.value,
                violation_type="missing_tests",
                description="No test files or directories found",
                severity="high" if rule.priority == RulePriority.MANDATORY else "medium",
                suggestion="Create test files and directories for your project"
            ))
        
        return violations
    
    def _check_documentation_rule(self, rule: RuleItem) -> List[RuleViolation]:
        """Check documentation rules"""
        violations = []
        
        # Check for README file
        readme_files = ['README.md', 'README.rst', 'README.txt', 'readme.md']
        found_readme = any((Path(self.project_root) / f).exists() for f in readme_files)
        
        if not found_readme and "readme" in rule.content.lower():
            violations.append(RuleViolation(
                rule_name=rule.description or rule.content[:50] + "...",
                rule_priority=rule.priority.value,
                rule_category=rule.category.value,
                violation_type="missing_readme",
                description="README file is missing",
                severity="medium",
                suggestion="Create a README.md file with project documentation"
            ))
        
        # Check for docs directory
        docs_dir = Path(self.project_root) / "docs"
        if not docs_dir.exists() and "docs" in rule.content.lower() and "directory" in rule.content.lower():
            violations.append(RuleViolation(
                rule_name=rule.description or rule.content[:50] + "...",
                rule_priority=rule.priority.value,
                rule_category=rule.category.value,
                violation_type="missing_docs_dir",
                description="Documentation directory is missing",
                severity="low",
                suggestion="Create a docs/ directory for project documentation"
            ))
        
        return violations
    
    def _check_security_rule(self, rule: RuleItem) -> List[RuleViolation]:
        """Check security rules"""
        violations = []
        
        # Check for .env files in git
        gitignore_path = Path(self.project_root) / ".gitignore"
        env_files = list(Path(self.project_root).rglob(".env*"))
        
        if env_files and gitignore_path.exists():
            try:
                with open(gitignore_path, 'r') as f:
                    gitignore_content = f.read()
                
                if ".env" not in gitignore_content:
                    violations.append(RuleViolation(
                        rule_name=rule.description or rule.content[:50] + "...",
                        rule_priority=rule.priority.value,
                        rule_category=rule.category.value,
                        violation_type="security_risk",
                        description="Environment files (.env) are not ignored by git",
                        file_path=".gitignore",
                        severity="high",
                        suggestion="Add .env to .gitignore to prevent committing secrets"
                    ))
            except Exception:
                pass
        
        return violations
    
    def _extract_required_items(self, content: str) -> List[str]:
        """Extract required files/directories from rule content"""
        # Simple extraction - in real implementation, use more sophisticated parsing
        items = []
        lines = content.split('\n')
        
        for line in lines:
            if 'must have' in line.lower() or 'required' in line.lower():
                # Look for file/directory patterns
                import re
                matches = re.findall(r'[\'"`]([^\'"`]+)[\'"`]', line)
                items.extend(matches)
        
        return items
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract required dependencies from rule content"""
        # Simple extraction - in real implementation, use more sophisticated parsing
        deps = []
        lines = content.split('\n')
        
        for line in lines:
            if 'dependency' in line.lower() or 'package' in line.lower():
                import re
                matches = re.findall(r'[\'"`]([^\'"`]+)[\'"`]', line)
                deps.extend(matches)
        
        return deps
    
    def _generate_markdown_report(self) -> str:
        """Generate a Markdown format report"""
        report = []
        
        # Header
        report.append("# Project Rules Compliance Report")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Project:** {os.path.basename(self.project_root)}")
        report.append("")
        
        # Executive Summary
        if self.compliance_score:
            report.append("## 📊 Executive Summary")
            report.append("")
            score = self.compliance_score
            report.append(f"- **Overall Grade:** {score.grade}")
            report.append(f"- **Compliance Score:** {score.score_percentage:.1f}%")
            report.append(f"- **Total Rules:** {score.total_rules}")
            report.append(f"- **Passed:** {score.passed_rules}")
            report.append(f"- **Failed:** {score.failed_rules}")
            report.append(f"- **Warnings:** {score.warnings}")
            report.append("")
            
            # Grade interpretation
            if score.grade == "A":
                report.append("🎉 **Excellent!** Your project demonstrates outstanding compliance with established rules.")
            elif score.grade == "B":
                report.append("👍 **Good!** Your project shows good compliance with minor areas for improvement.")
            elif score.grade == "C":
                report.append("⚠️ **Fair.** Your project has some compliance issues that should be addressed.")
            elif score.grade == "D":
                report.append("🔧 **Needs Improvement.** Your project has significant compliance issues.")
            else:
                report.append("🚨 **Critical.** Your project has major compliance violations that need immediate attention.")
            
            report.append("")
        
        # Violations by Category
        if self.violations:
            report.append("## 🚨 Violations by Category")
            report.append("")
            
            # Group violations by category
            by_category = {}
            for violation in self.violations:
                category = violation.rule_category
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(violation)
            
            for category, violations in by_category.items():
                report.append(f"### {category.replace('_', ' ').title()}")
                report.append("")
                
                for violation in violations:
                    severity_emoji = {
                        "high": "🔴",
                        "medium": "🟡",
                        "low": "🟢"
                    }.get(violation.severity, "⚪")
                    
                    priority_emoji = {
                        "MANDATORY": "🚨",
                        "RECOMMENDED": "⚠️",
                        "OPTIONAL": "ℹ️"
                    }.get(violation.rule_priority, "")
                    
                    report.append(f"**{severity_emoji} {violation.rule_name}** {priority_emoji}")
                    report.append(f"- **Type:** {violation.violation_type.replace('_', ' ').title()}")
                    report.append(f"- **Description:** {violation.description}")
                    
                    if violation.file_path:
                        report.append(f"- **File:** `{violation.file_path}`")
                    
                    if violation.line_number:
                        report.append(f"- **Line:** {violation.line_number}")
                    
                    if violation.suggestion:
                        report.append(f"- **Suggestion:** {violation.suggestion}")
                    
                    report.append("")
        
        # Priority Summary
        if self.violations:
            report.append("## 📋 Priority Summary")
            report.append("")
            
            priority_groups = {}
            for violation in self.violations:
                priority = violation.rule_priority
                if priority not in priority_groups:
                    priority_groups[priority] = []
                priority_groups[priority].append(violation)
            
            report.append("| Priority | Count | Impact |")
            report.append("|----------|-------|--------|")
            
            for priority in ["MANDATORY", "RECOMMENDED", "OPTIONAL"]:
                count = len(priority_groups.get(priority, []))
                if count > 0:
                    impact = {
                        "MANDATORY": "🚨 Critical - Must be fixed",
                        "RECOMMENDED": "⚠️ Important - Should be fixed",
                        "OPTIONAL": "ℹ️ Minor - Nice to fix"
                    }.get(priority, "")
                    
                    report.append(f"| {priority} | {count} | {impact} |")
            
            report.append("")
        
        # Recommendations
        report.append("## 💡 Recommendations")
        report.append("")
        
        if not self.violations:
            report.append("🎉 **Congratulations!** Your project is fully compliant with all rules.")
        else:
            # Priority-based recommendations
            mandatory_violations = [v for v in self.violations if v.rule_priority == "MANDATORY"]
            if mandatory_violations:
                report.append("### 🚨 Immediate Actions Required")
                report.append("")
                for violation in mandatory_violations[:5]:  # Top 5
                    if violation.suggestion:
                        report.append(f"- {violation.suggestion}")
                if len(mandatory_violations) > 5:
                    report.append(f"- ... and {len(mandatory_violations) - 5} more mandatory issues")
                report.append("")
            
            recommended_violations = [v for v in self.violations if v.rule_priority == "RECOMMENDED"]
            if recommended_violations:
                report.append("### ⚠️ Recommended Improvements")
                report.append("")
                for violation in recommended_violations[:3]:  # Top 3
                    if violation.suggestion:
                        report.append(f"- {violation.suggestion}")
                if len(recommended_violations) > 3:
                    report.append(f"- ... and {len(recommended_violations) - 3} more recommended improvements")
                report.append("")
        
        # Next Steps
        report.append("## 🚀 Next Steps")
        report.append("")
        report.append("1. **Address Mandatory Issues:** Fix all critical violations first")
        report.append("2. **Implement Recommendations:** Work on recommended improvements")
        report.append("3. **Re-run Analysis:** Use `projectprompt rules report` to track progress")
        report.append("4. **Continuous Monitoring:** Integrate rules checking into your CI/CD pipeline")
        report.append("")
        
        # Footer
        report.append("---")
        report.append("*Report generated by ProjectPrompt Rules System*")
        
        return "\n".join(report)
    
    def _generate_json_report(self) -> str:
        """Generate a JSON format report"""
        report_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "project_root": self.project_root,
                "project_name": os.path.basename(self.project_root),
                "generator": "ProjectPrompt Rules System"
            },
            "compliance_score": self.compliance_score.__dict__ if self.compliance_score else None,
            "violations": [
                {
                    "rule_name": v.rule_name,
                    "rule_priority": v.rule_priority,
                    "rule_category": v.rule_category,
                    "violation_type": v.violation_type,
                    "description": v.description,
                    "file_path": v.file_path,
                    "line_number": v.line_number,
                    "suggestion": v.suggestion,
                    "severity": v.severity
                }
                for v in self.violations
            ],
            "summary": {
                "total_violations": len(self.violations),
                "by_priority": {
                    priority: len([v for v in self.violations if v.rule_priority == priority])
                    for priority in ["MANDATORY", "RECOMMENDED", "OPTIONAL"]
                },
                "by_category": {
                    category: len([v for v in self.violations if v.rule_category == category])
                    for category in set(v.rule_category for v in self.violations)
                },
                "by_severity": {
                    severity: len([v for v in self.violations if v.severity == severity])
                    for severity in ["high", "medium", "low"]
                }
            }
        }
        
        return json.dumps(report_data, indent=2, ensure_ascii=False)
    
    def _generate_html_report(self) -> str:
        """Generate an HTML format report"""
        # HTML template with embedded CSS
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project Rules Compliance Report</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }
        .container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; }
        .content { padding: 30px; }
        .grade { font-size: 3em; font-weight: bold; text-align: center; margin: 20px 0; }
        .grade.A { color: #27ae60; }
        .grade.B { color: #2ecc71; }
        .grade.C { color: #f39c12; }
        .grade.D { color: #e67e22; }
        .grade.F { color: #e74c3c; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }
        .metric { background: #f8f9fa; padding: 20px; border-radius: 6px; text-align: center; }
        .metric-value { font-size: 2em; font-weight: bold; color: #2c3e50; }
        .metric-label { color: #7f8c8d; margin-top: 5px; }
        .violation { border-left: 4px solid #e74c3c; margin: 15px 0; padding: 15px; background: #fdf2f2; border-radius: 0 6px 6px 0; }
        .violation.medium { border-color: #f39c12; background: #fef9e7; }
        .violation.low { border-color: #27ae60; background: #f1f8e9; }
        .violation-title { font-weight: bold; margin-bottom: 8px; }
        .violation-meta { font-size: 0.9em; color: #7f8c8d; margin-bottom: 8px; }
        .violation-suggestion { background: #e8f4f8; padding: 10px; border-radius: 4px; margin-top: 10px; }
        .category-section { margin: 30px 0; }
        .category-title { background: #34495e; color: white; padding: 15px; border-radius: 6px; margin-bottom: 15px; }
        .progress-bar { background: #ecf0f1; height: 20px; border-radius: 10px; overflow: hidden; margin: 10px 0; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #e74c3c, #f39c12, #27ae60); transition: width 0.3s ease; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ Project Rules Compliance Report</h1>
            <p><strong>Project:</strong> {project_name}</p>
            <p><strong>Generated:</strong> {generated_at}</p>
        </div>
        
        <div class="content">
            {content}
        </div>
    </div>
</body>
</html>
        """
        
        content_parts = []
        
        # Executive Summary
        if self.compliance_score:
            score = self.compliance_score
            content_parts.append(f"""
            <div class="grade {score.grade}">{score.grade}</div>
            
            <div class="progress-bar">
                <div class="progress-fill" style="width: {score.score_percentage}%"></div>
            </div>
            <p style="text-align: center; font-size: 1.2em; margin-bottom: 30px;">
                Compliance Score: <strong>{score.score_percentage:.1f}%</strong>
            </p>
            
            <div class="metrics">
                <div class="metric">
                    <div class="metric-value">{score.total_rules}</div>
                    <div class="metric-label">Total Rules</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{score.passed_rules}</div>
                    <div class="metric-label">Passed</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{score.failed_rules}</div>
                    <div class="metric-label">Failed</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{score.warnings}</div>
                    <div class="metric-label">Warnings</div>
                </div>
            </div>
            """)
        
        # Violations
        if self.violations:
            # Group by category
            by_category = {}
            for violation in self.violations:
                category = violation.rule_category
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(violation)
            
            content_parts.append("<h2>🚨 Violations by Category</h2>")
            
            for category, violations in by_category.items():
                content_parts.append(f"""
                <div class="category-section">
                    <div class="category-title">
                        {category.replace('_', ' ').title()} ({len(violations)} issues)
                    </div>
                """)
                
                for violation in violations:
                    severity_emoji = {
                        "high": "🔴",
                        "medium": "🟡", 
                        "low": "🟢"
                    }.get(violation.severity, "⚪")
                    
                    priority_emoji = {
                        "MANDATORY": "🚨",
                        "RECOMMENDED": "⚠️",
                        "OPTIONAL": "ℹ️"
                    }.get(violation.rule_priority, "")
                    
                    suggestion_html = ""
                    if violation.suggestion:
                        suggestion_html = f"""
                        <div class="violation-suggestion">
                            <strong>💡 Suggestion:</strong> {html.escape(violation.suggestion)}
                        </div>
                        """
                    
                    file_info = ""
                    if violation.file_path:
                        file_info = f"<strong>File:</strong> {html.escape(violation.file_path)}"
                        if violation.line_number:
                            file_info += f" (Line {violation.line_number})"
                        file_info += "<br>"
                    
                    content_parts.append(f"""
                    <div class="violation {violation.severity}">
                        <div class="violation-title">
                            {severity_emoji} {html.escape(violation.rule_name)} {priority_emoji}
                        </div>
                        <div class="violation-meta">
                            <strong>Type:</strong> {violation.violation_type.replace('_', ' ').title()}<br>
                            {file_info}
                            <strong>Priority:</strong> {violation.rule_priority}
                        </div>
                        <div>{html.escape(violation.description)}</div>
                        {suggestion_html}
                    </div>
                    """)
                
                content_parts.append("</div>")
        else:
            content_parts.append("""
            <div style="text-align: center; padding: 50px; background: #f1f8e9; border-radius: 8px; color: #27ae60;">
                <h2>🎉 Congratulations!</h2>
                <p>Your project is fully compliant with all rules.</p>
            </div>
            """)
        
        # Next Steps
        content_parts.append("""
        <h2>🚀 Next Steps</h2>
        <ol>
            <li><strong>Address Mandatory Issues:</strong> Fix all critical violations first</li>
            <li><strong>Implement Recommendations:</strong> Work on recommended improvements</li>
            <li><strong>Re-run Analysis:</strong> Use <code>projectprompt rules report</code> to track progress</li>
            <li><strong>Continuous Monitoring:</strong> Integrate rules checking into your CI/CD pipeline</li>
        </ol>
        """)
        
        return html_template.format(
            project_name=html.escape(os.path.basename(self.project_root)),
            generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            content="\n".join(content_parts)
        )
