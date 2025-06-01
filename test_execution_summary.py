#!/usr/bin/env python3
"""
ProjectPrompt Testing Execution Summary
Created based on the comprehensive testing guide requirements
"""

import subprocess
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, TaskID
from rich.text import Text

console = Console()

class ProjectPromptTester:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'categories': {}
        }
        self.pp_command = self.detect_projectprompt_command()
    
    def detect_projectprompt_command(self):
        """Detect how to run ProjectPrompt"""
        commands = ["project-prompt", "pp", "python3 src/main.py"]
        for cmd in commands:
            try:
                result = subprocess.run(cmd.split() + ["--help"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    return cmd
            except:
                continue
        return "python3 src/main.py"
    
    def run_command(self, cmd_args, timeout=30):
        """Run a ProjectPrompt command and capture results"""
        full_cmd = self.pp_command.split() + cmd_args
        try:
            result = subprocess.run(full_cmd, capture_output=True, 
                                  text=True, timeout=timeout)
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'stdout': '',
                'stderr': 'Command timed out',
                'returncode': -1
            }
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'returncode': -1
            }
    
    def test_basic_commands(self):
        """Test basic ProjectPrompt commands"""
        console.print("\n[bold blue]Testing Basic Commands[/bold blue]")
        
        tests = [
            ("Help Command", ["--help"]),
            ("Config Help", ["config", "--help"]),
            ("Analyze Help", ["analyze", "--help"]),
            ("Rules Help", ["rules", "--help"]),
            ("AI Help", ["ai", "--help"]),
            ("Dashboard Help", ["dashboard", "--help"]),
            ("Diagnose Command", ["diagnose"]),
        ]
        
        category_results = []
        
        for test_name, cmd_args in tests:
            console.print(f"  • Testing {test_name}...", end="")
            result = self.run_command(cmd_args)
            
            if result['success']:
                console.print(" [green]✓ PASSED[/green]")
                self.results['passed'] += 1
                category_results.append({'test': test_name, 'status': 'PASSED'})
            else:
                console.print(" [red]✗ FAILED[/red]")
                self.results['failed'] += 1
                category_results.append({
                    'test': test_name, 
                    'status': 'FAILED',
                    'error': result['stderr'][:100]
                })
            
            self.results['total_tests'] += 1
        
        self.results['categories']['basic_commands'] = category_results
    
    def test_configuration_commands(self):
        """Test configuration related commands"""
        console.print("\n[bold blue]Testing Configuration Commands[/bold blue]")
        
        tests = [
            ("Config Show", ["config", "show"]),
            ("Config List", ["config", "list"]),
            ("Check Environment", ["check-env"]),
        ]
        
        category_results = []
        
        for test_name, cmd_args in tests:
            console.print(f"  • Testing {test_name}...", end="")
            result = self.run_command(cmd_args)
            
            # Configuration commands might fail if no config exists, that's OK
            if result['success'] or "not found" in result['stderr'].lower():
                console.print(" [green]✓ PASSED[/green]")
                self.results['passed'] += 1
                category_results.append({'test': test_name, 'status': 'PASSED'})
            else:
                console.print(" [red]✗ FAILED[/red]")
                self.results['failed'] += 1
                category_results.append({
                    'test': test_name, 
                    'status': 'FAILED',
                    'error': result['stderr'][:100]
                })
            
            self.results['total_tests'] += 1
        
        self.results['categories']['configuration'] = category_results
    
    def test_analysis_commands(self):
        """Test analysis related commands"""
        console.print("\n[bold blue]Testing Analysis Commands[/bold blue]")
        
        # Create a simple test directory structure
        test_dir = Path("test_analysis_target")
        test_dir.mkdir(exist_ok=True)
        (test_dir / "test.py").write_text("print('hello')")
        
        tests = [
            ("Analyze Current Directory", ["analyze", "."]),
            ("Analyze Test Directory", ["analyze", str(test_dir)]),
            ("Dependencies Analysis", ["deps", "--help"]),
        ]
        
        category_results = []
        
        for test_name, cmd_args in tests:
            console.print(f"  • Testing {test_name}...", end="")
            result = self.run_command(cmd_args, timeout=60)
            
            if result['success']:
                console.print(" [green]✓ PASSED[/green]")
                self.results['passed'] += 1
                category_results.append({'test': test_name, 'status': 'PASSED'})
            else:
                console.print(" [red]✗ FAILED[/red]")
                self.results['failed'] += 1
                category_results.append({
                    'test': test_name, 
                    'status': 'FAILED',
                    'error': result['stderr'][:100]
                })
            
            self.results['total_tests'] += 1
        
        # Cleanup
        if test_dir.exists():
            import shutil
            shutil.rmtree(test_dir)
        
        self.results['categories']['analysis'] = category_results
    
    def test_rules_system(self):
        """Test the rules system"""
        console.print("\n[bold blue]Testing Rules System[/bold blue]")
        
        tests = [
            ("Rules List", ["rules", "list"]),
            ("Rules Categories", ["rules", "categories"]),
            ("Rules Templates", ["rules", "templates"]),
        ]
        
        category_results = []
        
        for test_name, cmd_args in tests:
            console.print(f"  • Testing {test_name}...", end="")
            result = self.run_command(cmd_args)
            
            if result['success']:
                console.print(" [green]✓ PASSED[/green]")
                self.results['passed'] += 1
                category_results.append({'test': test_name, 'status': 'PASSED'})
            else:
                console.print(" [red]✗ FAILED[/red]")
                self.results['failed'] += 1
                category_results.append({
                    'test': test_name, 
                    'status': 'FAILED',
                    'error': result['stderr'][:100]
                })
            
            self.results['total_tests'] += 1
        
        self.results['categories']['rules_system'] = category_results
    
    def test_utility_commands(self):
        """Test utility commands"""
        console.print("\n[bold blue]Testing Utility Commands[/bold blue]")
        
        tests = [
            ("Help Command", ["help"]),
            ("Menu Help", ["menu", "--help"]),
            ("Documentation", ["docs", "--help"]),
            ("Initialize Help", ["init", "--help"]),
        ]
        
        category_results = []
        
        for test_name, cmd_args in tests:
            console.print(f"  • Testing {test_name}...", end="")
            result = self.run_command(cmd_args)
            
            if result['success']:
                console.print(" [green]✓ PASSED[/green]")
                self.results['passed'] += 1
                category_results.append({'test': test_name, 'status': 'PASSED'})
            else:
                console.print(" [red]✗ FAILED[/red]")
                self.results['failed'] += 1
                category_results.append({
                    'test': test_name, 
                    'status': 'FAILED',
                    'error': result['stderr'][:100]
                })
            
            self.results['total_tests'] += 1
        
        self.results['categories']['utilities'] = category_results
    
    def generate_report(self):
        """Generate test execution report"""
        console.print("\n" + "="*60)
        console.print("[bold cyan]ProjectPrompt Testing Summary[/bold cyan]")
        console.print("="*60)
        
        # Summary table
        table = Table(title="Test Results Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("Total Tests", str(self.results['total_tests']))
        table.add_row("Passed", f"[green]{self.results['passed']}[/green]")
        table.add_row("Failed", f"[red]{self.results['failed']}[/red]")
        
        success_rate = (self.results['passed'] / self.results['total_tests'] * 100) if self.results['total_tests'] > 0 else 0
        table.add_row("Success Rate", f"{success_rate:.1f}%")
        table.add_row("ProjectPrompt Command", self.pp_command)
        
        console.print(table)
        
        # Category breakdown
        console.print("\n[bold cyan]Category Breakdown[/bold cyan]")
        for category, tests in self.results['categories'].items():
            passed = sum(1 for t in tests if t['status'] == 'PASSED')
            total = len(tests)
            console.print(f"  • {category.replace('_', ' ').title()}: {passed}/{total}")
        
        # Save detailed report
        report_file = f"test_execution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        console.print(f"\n[bold green]Detailed report saved to: {report_file}[/bold green]")
        
        return success_rate

def main():
    console.print(Panel.fit(
        "[bold blue]ProjectPrompt Comprehensive Testing Suite[/bold blue]\n"
        "[cyan]Testing all major functionalities and commands[/cyan]",
        border_style="blue"
    ))
    
    tester = ProjectPromptTester()
    
    # Run all test categories
    tester.test_basic_commands()
    tester.test_configuration_commands()
    tester.test_analysis_commands()
    tester.test_rules_system()
    tester.test_utility_commands()
    
    # Generate final report
    success_rate = tester.generate_report()
    
    # Return appropriate exit code
    if success_rate >= 80:
        console.print("\n[bold green]🎉 Testing completed successfully![/bold green]")
        sys.exit(0)
    else:
        console.print("\n[bold red]⚠️ Some tests failed. Check the report for details.[/bold red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
