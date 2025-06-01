#!/usr/bin/env python3
"""
ProjectPrompt Comprehensive Test Suite

This Python script provides a comprehensive testing framework for all ProjectPrompt
functionalities, including AI features, configuration management, and analysis tools.
"""

import os
import sys
import json
import time
import asyncio
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

# Add project root to path
current_dir = Path(__file__).parent
project_root = current_dir
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Rich imports for better output
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.text import Text
    from rich.tree import Tree
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Rich not available - using basic output")

class TestResult(Enum):
    """Test result types"""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"

class TestCategory(Enum):
    """Test categories"""
    BASIC = "basic"
    CONFIG = "configuration"
    ANALYSIS = "analysis"
    SETUP = "setup"
    AI = "ai"
    RULES = "rules"
    PROGRESS = "progress"
    DOCS = "documentation"
    UTILITIES = "utilities"
    ERROR_HANDLING = "error_handling"
    API = "api"
    PREMIUM = "premium"

@dataclass
class TestCase:
    """Individual test case"""
    name: str
    command: str
    description: str
    category: TestCategory
    expect_success: bool = True
    timeout: int = 30
    requires_api: bool = False
    interactive: bool = False
    input_data: Optional[str] = None
    result: Optional[TestResult] = None
    output: str = ""
    error: str = ""
    duration: float = 0.0
    exit_code: int = 0

@dataclass
class TestSuite:
    """Complete test suite"""
    name: str = "ProjectPrompt Comprehensive Tests"
    test_cases: List[TestCase] = field(default_factory=list)
    results_dir: Optional[Path] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    @property
    def passed_count(self) -> int:
        return sum(1 for tc in self.test_cases if tc.result == TestResult.PASSED)
    
    @property
    def failed_count(self) -> int:
        return sum(1 for tc in self.test_cases if tc.result == TestResult.FAILED)
    
    @property
    def skipped_count(self) -> int:
        return sum(1 for tc in self.test_cases if tc.result == TestResult.SKIPPED)
    
    @property
    def error_count(self) -> int:
        return sum(1 for tc in self.test_cases if tc.result == TestResult.ERROR)
    
    @property
    def total_count(self) -> int:
        return len(self.test_cases)
    
    @property
    def success_rate(self) -> float:
        total_executed = self.passed_count + self.failed_count + self.error_count
        if total_executed == 0:
            return 0.0
        return (self.passed_count / total_executed) * 100

class ProjectPromptTester:
    """Main testing class"""
    
    def __init__(self, results_dir: Optional[str] = None):
        self.console = Console() if RICH_AVAILABLE else None
        self.suite = TestSuite()
        
        # Setup results directory
        if results_dir:
            self.suite.results_dir = Path(results_dir)
        else:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            self.suite.results_dir = Path(f"test-results-{timestamp}")
        
        self.suite.results_dir.mkdir(exist_ok=True)
        
        # Determine ProjectPrompt command
        self.pp_cmd = self._detect_pp_command()
        
        # Initialize test cases
        self._init_test_cases()
    
    def _detect_pp_command(self) -> str:
        """Detect how to run ProjectPrompt"""
        # Try different ways to access ProjectPrompt
        commands_to_try = [
            "project-prompt",
            "pp",
            "python3 src/main.py",
            "python src/main.py"
        ]
        
        for cmd in commands_to_try:
            try:
                result = subprocess.run(
                    f"{cmd} version", 
                    shell=True, 
                    capture_output=True, 
                    timeout=5
                )
                if result.returncode == 0:
                    if self.console:
                        self.console.print(f"✓ Using command: {cmd}", style="green")
                    else:
                        print(f"✓ Using command: {cmd}")
                    return cmd
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                continue
        
        # Default fallback
        return "python3 src/main.py"
    
    def _init_test_cases(self):
        """Initialize all test cases"""
        # Basic Information Commands
        basic_tests = [
            TestCase("version", f"{self.pp_cmd} version", "Show version information", TestCategory.BASIC),
            TestCase("help_general", f"{self.pp_cmd} help", "Show general help", TestCategory.BASIC),
            TestCase("help_analyze", f"{self.pp_cmd} help analyze", "Show analyze command help", TestCategory.BASIC),
            TestCase("help_config", f"{self.pp_cmd} help config", "Show config command help", TestCategory.BASIC),
            TestCase("diagnose", f"{self.pp_cmd} diagnose", "Run diagnostic checks", TestCategory.BASIC),
        ]
        
        # Configuration Commands
        config_tests = [
            TestCase("config_show", f"{self.pp_cmd} config show", "Show current configuration", TestCategory.CONFIG),
            TestCase("config_list", f"{self.pp_cmd} config list", "List configuration options", TestCategory.CONFIG),
            TestCase("check_env", f"{self.pp_cmd} check-env", "Check environment variables", TestCategory.CONFIG),
            TestCase("set_log_level_info", f"{self.pp_cmd} set-log-level INFO", "Set log level to INFO", TestCategory.CONFIG),
            TestCase("set_log_level_debug", f"{self.pp_cmd} set-log-level DEBUG", "Set log level to DEBUG", TestCategory.CONFIG),
            TestCase("config_set_name", f"{self.pp_cmd} config set project_name TestProject", "Set project name", TestCategory.CONFIG),
            TestCase("config_set_desc", f"{self.pp_cmd} config set description 'Testing ProjectPrompt'", "Set project description", TestCategory.CONFIG),
        ]
        
        # Analysis Commands
        analysis_tests = [
            TestCase("analyze", f"{self.pp_cmd} analyze", "Analyze current project", TestCategory.ANALYSIS),
            TestCase("analyze_detailed", f"{self.pp_cmd} analyze --detailed", "Detailed project analysis", TestCategory.ANALYSIS),
            TestCase("analyze_output", f"{self.pp_cmd} analyze --output {self.suite.results_dir}/analysis.md", "Analysis with output file", TestCategory.ANALYSIS),
            TestCase("deps", f"{self.pp_cmd} deps", "Dependency analysis", TestCategory.ANALYSIS),
            TestCase("deps_limited", f"{self.pp_cmd} deps --max-files 50", "Limited dependency analysis", TestCategory.ANALYSIS),
            TestCase("deps_output", f"{self.pp_cmd} deps --output {self.suite.results_dir}/dependencies.md", "Dependency analysis with output", TestCategory.ANALYSIS),
            TestCase("dashboard", f"{self.pp_cmd} dashboard", "Generate dashboard", TestCategory.ANALYSIS),
            TestCase("dashboard_md", f"{self.pp_cmd} dashboard --format markdown", "Dashboard in markdown format", TestCategory.ANALYSIS),
            TestCase("dashboard_json", f"{self.pp_cmd} dashboard --format json --output {self.suite.results_dir}/dashboard.json", "Dashboard in JSON format", TestCategory.ANALYSIS),
        ]
        
        # Project Setup Commands
        setup_tests = [
            TestCase("init_folder", f"{self.pp_cmd} init-project-folder", "Initialize project folder", TestCategory.SETUP),
            TestCase("setup_deps", f"{self.pp_cmd} setup-deps", "Setup dependencies", TestCategory.SETUP),
            TestCase("setup_alias", f"{self.pp_cmd} setup-alias", "Setup command alias", TestCategory.SETUP, interactive=True, input_data="n\n"),
        ]
        
        # AI Commands (may require API keys)
        ai_tests = [
            TestCase("analyze_group_list", f"{self.pp_cmd} analyze-group", "List available groups", TestCategory.AI, expect_success=False, requires_api=True),
            TestCase("analyze_group_specific", f"{self.pp_cmd} analyze-group 'src/analyzers'", "Analyze specific group", TestCategory.AI, expect_success=False, requires_api=True),
            TestCase("generate_suggestions", f"{self.pp_cmd} generate-suggestions --group 'src/analyzers'", "Generate suggestions", TestCategory.AI, expect_success=False, requires_api=True),
            TestCase("ai_chat", f"{self.pp_cmd} ai chat 'Hello'", "AI chat test", TestCategory.AI, expect_success=False, requires_api=True),
            TestCase("premium_list", f"{self.pp_cmd} premium list", "List premium features", TestCategory.PREMIUM, expect_success=False),
        ]
        
        # Rules Management
        rules_tests = [
            TestCase("rules_suggest", f"{self.pp_cmd} rules suggest", "Generate rule suggestions", TestCategory.RULES),
            TestCase("rules_patterns", f"{self.pp_cmd} rules analyze-patterns", "Analyze project patterns", TestCategory.RULES),
            TestCase("rules_project", f"{self.pp_cmd} rules generate-project-rules --output {self.suite.results_dir}/project-rules.md", "Generate project rules", TestCategory.RULES),
            TestCase("rules_structured", f"{self.pp_cmd} rules generate-structured-rules --output {self.suite.results_dir}/structured-rules.yaml", "Generate structured rules", TestCategory.RULES),
        ]
        
        # Progress and Status Commands
        progress_tests = [
            TestCase("status", f"{self.pp_cmd} status", "Show sync status", TestCategory.PROGRESS),
            TestCase("track_progress", f"{self.pp_cmd} track-progress --group 'src/analyzers' --phase 1", "Track progress", TestCategory.PROGRESS, expect_success=False),
        ]
        
        # Documentation Commands
        docs_tests = [
            TestCase("docs_list", f"{self.pp_cmd} docs list", "List documentation", TestCategory.DOCS),
            TestCase("docs_search", f"{self.pp_cmd} docs search 'api'", "Search documentation", TestCategory.DOCS),
        ]
        
        # Utility Commands
        utility_tests = [
            TestCase("telemetry_status", f"{self.pp_cmd} telemetry status", "Check telemetry status", TestCategory.UTILITIES),
            TestCase("telemetry_disable", f"{self.pp_cmd} telemetry disable", "Disable telemetry", TestCategory.UTILITIES),
            TestCase("telemetry_enable", f"{self.pp_cmd} telemetry enable", "Enable telemetry", TestCategory.UTILITIES),
            TestCase("update_check", f"{self.pp_cmd} update check", "Check for updates", TestCategory.UTILITIES),
        ]
        
        # Error Handling Tests
        error_tests = [
            TestCase("analyze_invalid_path", f"{self.pp_cmd} analyze /nonexistent/path", "Analysis with invalid path", TestCategory.ERROR_HANDLING, expect_success=False),
            TestCase("group_nonexistent", f"{self.pp_cmd} analyze-group 'nonexistent-group'", "Analyze nonexistent group", TestCategory.ERROR_HANDLING, expect_success=False),
            TestCase("config_invalid", f"{self.pp_cmd} config set invalid_key invalid_value", "Set invalid config", TestCategory.ERROR_HANDLING, expect_success=False),
        ]
        
        # API Configuration Tests
        api_tests = [
            TestCase("verify_api", f"{self.pp_cmd} verify-api", "Verify API configuration", TestCategory.API),
            TestCase("set_dummy_api", f"{self.pp_cmd} set-api anthropic dummy-key-for-testing", "Set dummy Anthropic key", TestCategory.API, expect_success=False),
        ]
        
        # Add all test cases to suite
        all_tests = (
            basic_tests + config_tests + analysis_tests + setup_tests +
            ai_tests + rules_tests + progress_tests + docs_tests +
            utility_tests + error_tests + api_tests
        )
        
        self.suite.test_cases.extend(all_tests)
    
    async def run_test_case(self, test_case: TestCase) -> TestCase:
        """Run a single test case"""
        start_time = time.time()
        
        try:
            if test_case.interactive and test_case.input_data:
                # Handle interactive commands
                process = subprocess.Popen(
                    test_case.command,
                    shell=True,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                try:
                    stdout, stderr = process.communicate(
                        input=test_case.input_data,
                        timeout=test_case.timeout
                    )
                    test_case.exit_code = process.returncode
                    test_case.output = stdout
                    test_case.error = stderr
                except subprocess.TimeoutExpired:
                    process.kill()
                    test_case.result = TestResult.ERROR
                    test_case.error = "Test timed out"
                    return test_case
            else:
                # Handle regular commands
                result = subprocess.run(
                    test_case.command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=test_case.timeout
                )
                test_case.exit_code = result.returncode
                test_case.output = result.stdout
                test_case.error = result.stderr
            
            # Determine test result
            if test_case.expect_success:
                if test_case.exit_code == 0:
                    test_case.result = TestResult.PASSED
                else:
                    test_case.result = TestResult.FAILED
            else:
                if test_case.exit_code != 0:
                    test_case.result = TestResult.PASSED
                else:
                    test_case.result = TestResult.FAILED
                    
        except subprocess.TimeoutExpired:
            test_case.result = TestResult.ERROR
            test_case.error = "Test timed out"
        except Exception as e:
            test_case.result = TestResult.ERROR
            test_case.error = str(e)
        
        test_case.duration = time.time() - start_time
        
        # Save individual test result
        self._save_test_result(test_case)
        
        return test_case
    
    def _save_test_result(self, test_case: TestCase):
        """Save individual test result to file"""
        result_file = self.suite.results_dir / f"{test_case.name}_result.json"
        
        result_data = {
            "name": test_case.name,
            "command": test_case.command,
            "description": test_case.description,
            "category": test_case.category.value,
            "result": test_case.result.value if test_case.result else None,
            "exit_code": test_case.exit_code,
            "duration": test_case.duration,
            "expect_success": test_case.expect_success,
            "requires_api": test_case.requires_api,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(result_file, 'w') as f:
            json.dump(result_data, f, indent=2)
        
        # Save output and error to separate files
        if test_case.output:
            output_file = self.suite.results_dir / f"{test_case.name}_output.txt"
            with open(output_file, 'w') as f:
                f.write(test_case.output)
        
        if test_case.error:
            error_file = self.suite.results_dir / f"{test_case.name}_error.txt"
            with open(error_file, 'w') as f:
                f.write(test_case.error)
    
    async def run_tests(self, categories: Optional[List[TestCategory]] = None, parallel: bool = False):
        """Run all tests or specific categories"""
        self.suite.start_time = datetime.now()
        
        # Filter tests by category if specified
        tests_to_run = self.suite.test_cases
        if categories:
            tests_to_run = [tc for tc in self.suite.test_cases if tc.category in categories]
        
        if self.console:
            self.console.print(Panel(f"Running {len(tests_to_run)} tests", title="ProjectPrompt Test Suite", style="blue"))
        else:
            print(f"Running {len(tests_to_run)} tests")
        
        if parallel and len(tests_to_run) > 1:
            # Run tests in parallel (limited concurrency for safety)
            semaphore = asyncio.Semaphore(3)  # Max 3 concurrent tests
            
            async def run_with_semaphore(test_case):
                async with semaphore:
                    return await self.run_test_case(test_case)
            
            tasks = [run_with_semaphore(tc) for tc in tests_to_run]
            
            if self.console:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    transient=True,
                ) as progress:
                    task = progress.add_task("Running tests...", total=len(tasks))
                    
                    for completed_task in asyncio.as_completed(tasks):
                        await completed_task
                        progress.advance(task)
            else:
                await asyncio.gather(*tasks)
        else:
            # Run tests sequentially
            for i, test_case in enumerate(tests_to_run, 1):
                if self.console:
                    self.console.print(f"[{i}/{len(tests_to_run)}] Running: {test_case.description}")
                else:
                    print(f"[{i}/{len(tests_to_run)}] Running: {test_case.description}")
                
                await self.run_test_case(test_case)
                
                # Show immediate result
                if test_case.result == TestResult.PASSED:
                    status = "✓ PASSED" if not self.console else "[green]✓ PASSED[/green]"
                elif test_case.result == TestResult.FAILED:
                    status = "✗ FAILED" if not self.console else "[red]✗ FAILED[/red]"
                elif test_case.result == TestResult.ERROR:
                    status = "⚠ ERROR" if not self.console else "[yellow]⚠ ERROR[/yellow]"
                else:
                    status = "? UNKNOWN" if not self.console else "[dim]? UNKNOWN[/dim]"
                
                if self.console:
                    self.console.print(f"  {status} ({test_case.duration:.2f}s)")
                else:
                    print(f"  {status} ({test_case.duration:.2f}s)")
        
        self.suite.end_time = datetime.now()
    
    def generate_report(self) -> str:
        """Generate comprehensive test report"""
        duration = 0
        if self.suite.start_time and self.suite.end_time:
            duration = (self.suite.end_time - self.suite.start_time).total_seconds()
        
        report_lines = [
            "# ProjectPrompt Test Report",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Duration:** {duration:.2f} seconds",
            f"**Results Directory:** {self.suite.results_dir}",
            "",
            "## Summary",
            "",
            f"- **Total Tests:** {self.suite.total_count}",
            f"- **Passed:** {self.suite.passed_count}",
            f"- **Failed:** {self.suite.failed_count}",
            f"- **Errors:** {self.suite.error_count}",
            f"- **Skipped:** {self.suite.skipped_count}",
            f"- **Success Rate:** {self.suite.success_rate:.1f}%",
            "",
            "## Results by Category",
            ""
        ]
        
        # Group results by category
        results_by_category = {}
        for test_case in self.suite.test_cases:
            if test_case.category not in results_by_category:
                results_by_category[test_case.category] = {
                    'passed': 0, 'failed': 0, 'error': 0, 'skipped': 0, 'tests': []
                }
            
            category_data = results_by_category[test_case.category]
            category_data['tests'].append(test_case)
            
            if test_case.result == TestResult.PASSED:
                category_data['passed'] += 1
            elif test_case.result == TestResult.FAILED:
                category_data['failed'] += 1
            elif test_case.result == TestResult.ERROR:
                category_data['error'] += 1
            else:
                category_data['skipped'] += 1
        
        for category, data in results_by_category.items():
            total_category = data['passed'] + data['failed'] + data['error'] + data['skipped']
            success_rate = (data['passed'] / max(1, total_category)) * 100
            
            report_lines.extend([
                f"### {category.value.title()}",
                "",
                f"- Total: {total_category}",
                f"- Passed: {data['passed']}",
                f"- Failed: {data['failed']}",
                f"- Errors: {data['error']}",
                f"- Success Rate: {success_rate:.1f}%",
                ""
            ])
        
        # Add detailed test results
        report_lines.extend([
            "## Detailed Test Results",
            "",
            "| Test | Category | Result | Duration | Description |",
            "|------|----------|--------|----------|-------------|"
        ])
        
        for test_case in self.suite.test_cases:
            result_emoji = {
                TestResult.PASSED: "✅",
                TestResult.FAILED: "❌",
                TestResult.ERROR: "⚠️",
                TestResult.SKIPPED: "⏭️"
            }.get(test_case.result, "❓")
            
            report_lines.append(
                f"| {test_case.name} | {test_case.category.value} | "
                f"{result_emoji} {test_case.result.value if test_case.result else 'unknown'} | "
                f"{test_case.duration:.2f}s | {test_case.description} |"
            )
        
        # Add recommendations
        report_lines.extend([
            "",
            "## Recommendations",
            ""
        ])
        
        if self.suite.failed_count == 0 and self.suite.error_count == 0:
            report_lines.append("✅ **All tests passed!** ProjectPrompt is working correctly.")
        else:
            report_lines.extend([
                f"⚠️ **{self.suite.failed_count + self.suite.error_count} tests failed.** Consider the following:",
                "",
                "1. Check API key configuration for AI features",
                "2. Ensure all dependencies are installed (`pip install -r requirements.txt`)",
                "3. Verify file permissions and access rights",
                "4. Review error logs in individual test result files",
                "5. Check network connectivity for API-dependent features"
            ])
        
        return "\n".join(report_lines)
    
    def display_summary(self):
        """Display test summary"""
        if self.console:
            # Rich display
            table = Table(title="Test Results Summary")
            table.add_column("Category", style="cyan")
            table.add_column("Total", justify="right")
            table.add_column("Passed", style="green", justify="right")
            table.add_column("Failed", style="red", justify="right")
            table.add_column("Errors", style="yellow", justify="right")
            table.add_column("Success Rate", justify="right")
            
            # Group by category
            results_by_category = {}
            for test_case in self.suite.test_cases:
                if test_case.category not in results_by_category:
                    results_by_category[test_case.category] = {'passed': 0, 'failed': 0, 'error': 0, 'skipped': 0}
                
                if test_case.result == TestResult.PASSED:
                    results_by_category[test_case.category]['passed'] += 1
                elif test_case.result == TestResult.FAILED:
                    results_by_category[test_case.category]['failed'] += 1
                elif test_case.result == TestResult.ERROR:
                    results_by_category[test_case.category]['error'] += 1
                else:
                    results_by_category[test_case.category]['skipped'] += 1
            
            for category, data in results_by_category.items():
                total = data['passed'] + data['failed'] + data['error'] + data['skipped']
                success_rate = (data['passed'] / max(1, total)) * 100
                
                table.add_row(
                    category.value.title(),
                    str(total),
                    str(data['passed']),
                    str(data['failed']),
                    str(data['error']),
                    f"{success_rate:.1f}%"
                )
            
            # Overall summary
            table.add_row(
                "[bold]OVERALL[/bold]",
                f"[bold]{self.suite.total_count}[/bold]",
                f"[bold green]{self.suite.passed_count}[/bold green]",
                f"[bold red]{self.suite.failed_count}[/bold red]",
                f"[bold yellow]{self.suite.error_count}[/bold yellow]",
                f"[bold]{self.suite.success_rate:.1f}%[/bold]"
            )
            
            self.console.print(table)
            
            # Final status
            if self.suite.failed_count == 0 and self.suite.error_count == 0:
                self.console.print(Panel("🎉 All tests passed! ProjectPrompt is working correctly.", style="green"))
            else:
                self.console.print(Panel(
                    f"⚠️ {self.suite.failed_count + self.suite.error_count} tests failed. Check the detailed report for more information.",
                    style="yellow"
                ))
        else:
            # Basic display
            print("\n" + "="*50)
            print("TEST RESULTS SUMMARY")
            print("="*50)
            print(f"Total Tests: {self.suite.total_count}")
            print(f"Passed: {self.suite.passed_count}")
            print(f"Failed: {self.suite.failed_count}")
            print(f"Errors: {self.suite.error_count}")
            print(f"Success Rate: {self.suite.success_rate:.1f}%")
            print("="*50)

async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ProjectPrompt Comprehensive Test Suite")
    parser.add_argument("--categories", nargs="+", choices=[c.value for c in TestCategory],
                       help="Test categories to run (default: all)")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--output-dir", help="Output directory for results")
    parser.add_argument("--no-report", action="store_true", help="Skip generating detailed report")
    
    args = parser.parse_args()
    
    # Create tester
    tester = ProjectPromptTester(args.output_dir)
    
    # Determine categories to run
    categories = None
    if args.categories:
        categories = [TestCategory(cat) for cat in args.categories]
    
    # Run tests
    await tester.run_tests(categories=categories, parallel=args.parallel)
    
    # Display summary
    tester.display_summary()
    
    # Generate and save report
    if not args.no_report:
        report = tester.generate_report()
        report_file = tester.suite.results_dir / "test_report.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        if tester.console:
            tester.console.print(f"\n📄 Detailed report saved to: {report_file}")
        else:
            print(f"\n📄 Detailed report saved to: {report_file}")
    
    # Exit with appropriate code
    if tester.suite.failed_count > 0 or tester.suite.error_count > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
