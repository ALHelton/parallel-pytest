import argparse
import asyncio
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from typing import List, Tuple
import shutil


class ParaPytestRunner:
    """
    Pytest runner that chunks tests and runs in parallel for faster CLI testing
    """

    def __init__(self, chunks: int = 4, pytest_args: List[str] = None):
        self.chunks = chunks
        self.pytest_args = pytest_args or []


    def collect_tests(self) -> List[str]:
        # Get list of all tests from pytest they can be divided into parallel chunks
        cmd = ["pytest", "--collect-only", "-q"] + self.pytest_args

        # Run pytest collection and capture the output as text
        collected = subprocess.run(cmd, capture_output=True, text=True)

        if collected.returncode  != 0 and collected.returncode != 5:
            if len(collected.stderr) > 0:
                print(f"Error Collecting Tests:\n{collected.stderr}")
            else:
                print("Error Collecting Tests. Process Exited.")
            sys.exit(1)


        # # parse collected tests text
        tests = []
        for line in collected.stdout.split('\n'):
            line = line.strip()
            # Look for lines that are test items (usually contain "::")
            if '::' in line and not line.startswith('='):
                # get the test path only
                test_item = line.split()[0] if ' ' in line else line
                tests.append(test_item)

        return tests
    
    
    def chunk_tests(self, tests: List[str]) -> List[List[str]]:
        """Split tests into roughly equal chunks"""
        if not tests:
            return []
        
        # Divide tests evenly across chunks, minimum 1 test per chunk
        chunk_size = max(1, len(tests) // self.chunks)
        chunks = []

        for i in range(0, len(tests), chunk_size):
            chunk = tests[i:i + chunk_size]
            if chunk:
                chunks.append(chunk)

        # If there are more chunks than requested caused by rounding, merge the last ones
        while len(chunks) > self.chunks:
            chunks[-2].extend(chunks[-1])
            chunks.pop()
        
        return chunks
    

    async def run_chunk(self, tests: List[str]) -> Tuple[int, str, str]:
        """Run a single chunk of tests asynchronously"""

        temp_file = tempfile.NamedTemporaryFile(mode='w' ,delete=False, suffix='.json')
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
    

    async def run_all_chunks(self, test_chunks: List[List[str]]):
        """Run all test chunks concurrently"""

        time_start = time.time()
        
        tasks = []
        for chunk in test_chunks:
            tasks.append(self.run_chunk(chunk))

        results = await asyncio.gather(*tasks)

        all_passed = True
        all_failures = []
        total_passed = 0
        total_failed = 0

        cyan = '\033[36m'
        bold = '\033[1m'
        red = '\033[31m'
        green = '\033[32m'
        reset = '\033[0m'

        for code, report in results:
            summary = report.get('summary', {})
            total_passed += summary.get('passed', 0)
            total_failed += summary.get('failed', 0)

            if code != 0:
                all_passed = False

                colored_output = report.get('colored_output', '')
                if 'FAILURES' in colored_output:
                    start = colored_output.find('FAILURES')
                    end = colored_output.find('short test summary')
                    if end != -1:
                        failure_content = colored_output[start:end].strip()
                        lines = []
                        for line in failure_content.split('\n'):
                            if 'FAILURES' not in line and '===' not in line:
                                lines.append(line)
                        all_failures.append('\n'.join(lines))

        total_time = time.time() - time_start

        # Get terminal width
        term_width = shutil.get_terminal_size().columns

        if all_passed:
            green = '\033[32m'
            reset = '\033[0m'
            print(f"{green}{bold}{total_passed} passed{reset}{green} in {total_time:.2f}s{reset}")
            return 0
        else:
            for failure in all_failures:
                # Replace with dynamic underscores - terminal width
                adjusted = re.sub(
                    r'_+\s+(\S+)\s+_+',
                    lambda m: '_' * ((term_width - len(m.group(1)) - 2) // 2) + ' ' + m.group(1) + ' ' + '_' * ((term_width - len(m.group(1)) - 2) // 2),
                    failure
                )
                print(adjusted)
                print()
            
            summary_text = " short test summary info "
            padding = (term_width - len(summary_text)) // 2
            
            print(f"{cyan}{bold}{'=' * padding}{summary_text}{'=' * padding}{reset}\n")
            
            # Print failed test list from JSON
            for code, report in results:
                for test in report.get('tests', []):
                    if test['outcome'] == 'failed':
                        print(f"{red}FAILED{reset} {test['nodeid']}")
            
            print(f"{red}{bold}{total_failed} failed{reset}, {green}{total_passed} passed{reset} {red}in {total_time:.2f}s{reset}")
            
            return 1

    def run(self):
        tests = self.collect_tests()
        
        if not tests:
            print("No tests collected")
            return 0
        
        test_chunks = self.chunk_tests(tests)
        
        exit_code = asyncio.run(self.run_all_chunks(test_chunks))

        return exit_code

def main():
    parser = argparse.ArgumentParser(description="Run pytest tests in parallel chunks")
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

    args = parser.parse_args()
    runner = ParaPytestRunner(chunks=args.chunks, pytest_args=[args.path])
    sys.exit(runner.run())

if __name__ == "__main__":
    main()