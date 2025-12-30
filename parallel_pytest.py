import asyncio
import re
import subprocess
import sys
import time
from typing import List, Tuple


class ParallelPytestRunner:
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

        # Run pytest with the specific test items
        cmd = ["pytest", "-q", "--color=yes"] + tests

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        return process.returncode, stdout.decode(), stderr.decode()
    

    async def run_all_chunks(self, test_chunks: List[List[str]]):
        """Run all test chunks concurrently"""

        tasks = []
        for chunk in test_chunks:
            tasks.append(self.run_chunk(chunk))

        results = await asyncio.gather(*tasks)

        all_passed = True
        failure_details = []
        all_summaries = []
        total_tests = 0

        for result in results:
            returncode, stdout, _ = result

            # Look for passing tests in output
            match = re.search(r'(\d+) passed', stdout)
            if match:
                total_tests += int(match.group(1))
            
            if returncode != 0:
                all_passed = False
                
                # Extract just the failure content
                if 'FAILURES' in stdout:
                    start = stdout.find('FAILURES')
                    end = stdout.find('short test summary')
                    if end != -1:
                        content = stdout[start:end].strip()
                        
                        # Remove lines with FAILURES or lines with multiple =
                        lines = []
                        for line in content.split('\n'):
                            # Skip if line contains FAILURES or has 3+ consecutive =
                            if 'FAILURES' not in line and '===' not in line:
                                lines.append(line)
                        
                        failure_details.append('\n'.join(lines))

                # Extract short test summary
                if 'short test summary' in stdout:
                    summary_start = stdout.find('short test summary')
                    # Find where summary ends (usually at a line of ===)
                    remaining = stdout[summary_start:]
                    summary_lines = []
                    for line in remaining.split('\n')[1:]:  # Skip the header line
                        if line.strip() and '===' not in line:
                            summary_lines.append(line)
                        elif '===' in line:
                            break
                    if summary_lines:
                        all_summaries.extend(summary_lines)


        if all_passed:
            # Green text for success
            green = '\033[32m'
            reset = '\033[0m'
            print(f"{green}{total_tests} passed{reset}")
            return 0
        
        else:
            # Print failures
            for details in failure_details:
                print("\n"+details)

            # Print summary
            if all_summaries:
                print("\n\nShort test summary info\n")
                for summary in all_summaries:
                    if "passed" in summary or "failed" in summary:
                        break
                    print(summary)
            
            return 1

    def run(self):
        """Main entry point"""
        tests = self.collect_tests()
        
        if not tests:
            print("No tests collected")
            return 0
        
        test_chunks = self.chunk_tests(tests)
        
        start_time = time.time()

        exit_code = asyncio.run(self.run_all_chunks(test_chunks))

        total_time = time.time() - start_time
        print(f"\nTotal time: {total_time:.2f}s")
        
        return exit_code


if __name__ == "__main__":
    runner = ParallelPytestRunner(pytest_args=['tests/'])
    runner.run()