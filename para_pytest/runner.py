import argparse
import asyncio
import fnmatch
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from typing import List, Tuple, Dict
import shutil


class ParaPytestRunner:
    """
    Pytest runner that chunks tests and runs in parallel for faster CLI testing
    """

    def __init__(self, chunks: int = 4, pytest_args: List[str] = None, debug: bool = False, serial_patterns: List[str] = None):
        self.chunks = chunks
        self.pytest_args = pytest_args or []
        self.debug = debug
        
        # Load serial patterns from pyproject.toml or use explicit patterns
        if serial_patterns is not None:
            self.serial_patterns = serial_patterns
        else:
            self.serial_patterns = self._load_serial_patterns()
        
        if self.debug and self.serial_patterns:
            print(f"Serial patterns: {self.serial_patterns}")


    def _load_serial_patterns(self) -> List[str]:
        """Load serial patterns from pyproject.toml [tool.para-pytest] section"""
        
        if not os.path.exists('pyproject.toml'):
            return []
        
        try:
            with open('pyproject.toml', 'r') as f:
                content = f.read()
            
            patterns = []
            in_section = False
            in_array = False
            
            for line in content.split('\n'):
                line = line.strip()
                
                if line.startswith('[tool.para-pytest]'):
                    in_section = True
                    continue
                elif line.startswith('[') and in_section:
                    break
                
                if in_section and 'serial_patterns' in line and '=' in line:
                    in_array = True
                    if '[' in line and ']' in line:
                        patterns.extend(self._parse_toml_array(line[line.index('['):line.index(']')+1]))
                        in_array = False
                    elif '[' in line:
                        patterns.extend(self._parse_toml_array(line))
                    continue
                
                if in_array:
                    if ']' in line:
                        patterns.extend(self._parse_toml_array(line.split(']')[0]))
                        in_array = False
                    else:
                        patterns.extend(self._parse_toml_array(line))
            
            if patterns and self.debug:
                print(f"Loaded {len(patterns)} serial patterns from pyproject.toml")
            
            return patterns
            
        except Exception as e:
            if self.debug:
                print(f"Warning: Could not parse pyproject.toml: {e}")
            return []


    def _parse_toml_array(self, text: str) -> List[str]:
        """Extract quoted strings from TOML array"""
        import re
        matches = re.findall(r'["\']([^"\']+)["\']', text)
        return [m.strip() for m in matches if m.strip()]


    def _matches_pattern_single(self, test: str, pattern: str) -> bool:
        """
        Check if a test matches a single pattern.
        Handles both exact patterns and file patterns.
        
        For patterns ending in .py (with or without wildcards):
        - Tries direct match first
        - If no :: in pattern, tries with ::* appended to match test node IDs
        """
        # Try direct match first
        if fnmatch.fnmatch(test, pattern):
            return True
        
        # If pattern ends with .py and doesn't contain ::,
        # automatically try matching with ::* appended to handle test node IDs
        if pattern.endswith('.py') and '::' not in pattern:
            if fnmatch.fnmatch(test, f"{pattern}::*"):
                return True
        
        return False


    def _matches_serial_pattern(self, test: str) -> bool:
        """
        Check if a test matches any serial pattern.
        Handles both exact patterns and file patterns.
        
        For patterns ending in .py without wildcards, tries:
        1. Exact match with pattern
        2. Match with pattern::* (to match test node IDs)
        """
        return any(self._matches_pattern_single(test, pattern) for pattern in self.serial_patterns)


    def collect_tests(self) -> List[str]:
        cmd = ["pytest", "--collect-only", "-q"] + self.pytest_args
        
        # Prevent line wrapping in pytest output
        env = os.environ.copy()
        env['COLUMNS'] = '9999'
        env['LINES'] = '9999'
        
        collected = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
        )
        
        if collected.returncode != 0 and collected.returncode != 5:
            if len(collected.stderr) > 0:
                print(f"Error Collecting Tests:\n{collected.stderr}")
            else:
                print("Error Collecting Tests. Process Exited.")
            sys.exit(1)
        
        tests = []
        for line in collected.stdout.split('\n'):
            line = line.strip()
            if not line or ' collected' in line or ' passed' in line:
                continue
            if '::' in line:
                tests.append(line)
        
        print(f"Collected {len(tests)} tests")
        return tests
    
    
    def chunk_tests(self, tests: List[str]) -> List[List[str]]:
        """Split tests into equal chunks, separating serial tests"""
        if not tests:
            return []
        
        parallel_tests = []
        serial_tests = []
        
        for test in tests:
            if self._matches_serial_pattern(test):
                serial_tests.append(test)
            else:
                parallel_tests.append(test)
        
        if serial_tests:
            yellow = '\033[33m'
            reset = '\033[0m'
            print(f"{yellow}ℹ️  {len(serial_tests)} tests configured to run serially{reset}")
            if self.debug:
                for pattern in self.serial_patterns:
                    matching = [t for t in serial_tests if self._matches_pattern_single(t, pattern)]
                    if matching:
                        print(f"   Pattern '{pattern}': {len(matching)} tests")
        
        chunk_size = max(1, len(parallel_tests) // self.chunks)
        chunks = []

        for i in range(0, len(parallel_tests), chunk_size):
            chunk = parallel_tests[i:i + chunk_size]
            if chunk:
                chunks.append(chunk)

        while len(chunks) > self.chunks:
            chunks[-2].extend(chunks[-1])
            chunks.pop()
        
        if serial_tests:
            chunks.append(serial_tests)
        
        return chunks
    

    async def run_chunk(self, tests: List[str]) -> Tuple[int, dict]:
        """Run a single chunk of tests asynchronously"""

        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        temp_file.close()

        cmd = [
            "pytest",
            "-q",
            "--color=yes",
            "--json-report", 
            f"--json-report-file={temp_file.name}", 
            "--json-report-indent=2",
            "--json-report-omit=log"
        ] + tests

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, _ = await process.communicate()

        with open(temp_file.name, 'r') as f:
            report = json.load(f)

        report['colored_output'] = stdout.decode()

        os.unlink(temp_file.name)

        return process.returncode, report
    

    def validate_execution(self, collected_tests: List[str], results: List[Tuple[int, dict]]) -> Dict:
        """Validate all tests were executed and return statistics"""
        
        executed_tests = set()
        failed_tests = []
        passed_tests = []
        skipped_tests = []
        error_tests = []
        
        for _, report in results:
            for test in report.get('tests', []):
                nodeid = test['nodeid']
                executed_tests.add(nodeid)
                
                outcome = test['outcome']
                if outcome == 'passed':
                    passed_tests.append(nodeid)
                elif outcome == 'failed':
                    failed_tests.append(nodeid)
                elif outcome == 'skipped':
                    skipped_tests.append(nodeid)
                elif outcome == 'error':
                    error_tests.append(nodeid)
        
        missing_tests = set(collected_tests) - executed_tests
        
        return {
            'collected': len(collected_tests),
            'executed': len(executed_tests),
            'passed': passed_tests,
            'failed': failed_tests,
            'skipped': skipped_tests,
            'errors': error_tests,
            'missing': list(missing_tests)
        }


    def print_test_summary(self, stats: Dict, results: List[Tuple[int, dict]], total_time: float) -> int:
        """Print final test summary and return exit code"""
        
        cyan = '\033[36m'
        bold = '\033[1m'
        red = '\033[31m'
        green = '\033[32m'
        yellow = '\033[33m'
        reset = '\033[0m'
        term_width = shutil.get_terminal_size().columns
        
        if stats['missing']:
            print(f"\n{red}⚠️  CRITICAL: {len(stats['missing'])} tests were NEVER executed!{reset}")
            if self.debug or len(stats['missing']) <= 10:
                print(f"{red}Missing tests:{reset}")
                for test in sorted(stats['missing']):
                    print(f"  {red}- {test}{reset}")
            else:
                print(f"{red}Missing tests (showing first 10):{reset}")
                for test in sorted(stats['missing'][:10]):
                    print(f"  {red}- {test}{reset}")
                print(f"  {red}... and {len(stats['missing']) - 10} more (use --debug to see all){reset}")
            print()
        
        all_passed = len(stats['failed']) == 0 and len(stats['errors']) == 0 and not stats['missing']
        
        if all_passed:
            print(f"{green}{bold}{len(stats['passed'])} passed{reset}{green} in {total_time:.2f}s{reset}")
            return 0
        
        # Print failure details
        self._print_failure_details(results, term_width)
        
        # Print failed test summary
        print(f"{cyan}{bold}{'=' * ((term_width - 24) // 2)} short test summary info {'=' * ((term_width - 24) // 2)}{reset}\n")
        
        for code, report in results:
            for test in report.get('tests', []):
                if test['outcome'] == 'failed':
                    print(f"{red}FAILED{reset} {test['nodeid']}")
                elif test['outcome'] == 'error':
                    print(f"{red}ERROR{reset} {test['nodeid']}")
        
        # Print summary statistics
        summary_parts = []
        if len(stats['failed']) > 0:
            summary_parts.append(f"{red}{bold}{len(stats['failed'])} failed{reset}")
        if len(stats['errors']) > 0:
            summary_parts.append(f"{red}{len(stats['errors'])} errors{reset}")
        if len(stats['passed']) > 0:
            summary_parts.append(f"{green}{len(stats['passed'])} passed{reset}")
        if len(stats['skipped']) > 0:
            summary_parts.append(f"{yellow}{len(stats['skipped'])} skipped{reset}")
        if stats['missing']:
            summary_parts.append(f"{red}{len(stats['missing'])} not executed{reset}")
        
        print(f"\n{', '.join(summary_parts)} {red}in {total_time:.2f}s{reset}")
        return 1


    def _print_failure_details(self, results: List[Tuple[int, dict]], term_width: int):
        """Extract and print failure details from test results"""
        
        for code, report in results:
            if code != 0:
                colored_output = report.get('colored_output', '')
                if 'FAILURES' in colored_output:
                    start = colored_output.find('FAILURES')
                    end = colored_output.find('short test summary')
                    if end != -1:
                        failure_content = colored_output[start:end].strip()
                        lines = [line for line in failure_content.split('\n') 
                                if 'FAILURES' not in line and '===' not in line]
                        failure_text = '\n'.join(lines)
                        
                        adjusted = re.sub(
                            r'_+\s+(\S+)\s+_+',
                            lambda m: '_' * ((term_width - len(m.group(1)) - 2) // 2) + ' ' + m.group(1) + ' ' + '_' * ((term_width - len(m.group(1)) - 2) // 2),
                            failure_text
                        )
                        print(adjusted)
                        print()


    async def run_all_chunks(self, test_chunks: List[List[str]]):
        """Run all test chunks concurrently"""
        print(f"\nRunning tests...")

        time_start = time.time()
        
        all_collected_tests = [test for chunk in test_chunks for test in chunk]
        
        tasks = [self.run_chunk(chunk) for chunk in test_chunks]
        results = await asyncio.gather(*tasks)
        
        stats = self.validate_execution(all_collected_tests, results)
        
        total_time = time.time() - time_start
        return self.print_test_summary(stats, results, total_time)

    def run(self):
        tests = self.collect_tests()
        
        if not tests:
            print("No tests collected")
            return 0
        
        test_chunks = self.chunk_tests(tests)
        
        if self.debug:
            print(f"\nSplit into {len(test_chunks)} chunks:")
            for i, chunk in enumerate(test_chunks, 1):
                print(f"  Chunk {i}: {len(chunk)} tests")
        
        return asyncio.run(self.run_all_chunks(test_chunks))

def main():
    parser = argparse.ArgumentParser(
        description="Run pytest tests in parallel chunks",
        epilog="Configure serial patterns in pyproject.toml: [tool.para-pytest] serial_patterns = [...]"
    )
    parser.add_argument(
        "--chunks",
        type=int,
        default=4,
        help="Number of parallel chunks to divide tests into (default: 4)"
    )
    parser.add_argument(
        "--path",
        type=str,
        default='.',
        help="Path to tests (default: current directory)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output showing missing tests and chunking info"
    )

    args = parser.parse_args()
    runner = ParaPytestRunner(
        chunks=args.chunks, 
        pytest_args=[args.path], 
        debug=args.debug
    )
    sys.exit(runner.run())

if __name__ == "__main__":
    main()