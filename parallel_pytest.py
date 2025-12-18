import asyncio
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
        print("Collecting Tests from Pytest...")

        # Get list of all tests from pytest they can be divided into parallel chunks
        cmd = ["pytest", "--collect-only", "-q"] + self.pytest_args

        # Run pytest collection and capture the output as text
        collected = subprocess.run(cmd, capture_output=True, text=True)

        if collected.returncode  != 0 and collected.returncode != 5:
            print(f"Error Collecting Tests:\n{collected.stderr}")
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
    

    async def run_chunk(self, chunk_id: int, tests: List[str]) -> Tuple[int, str, str]:
        """Run a single chunk of tests asynchronously"""
        print(f"Chunk Number: {chunk_id}, Starting {len(tests)} tests...")

        # Run pytest with the specific test items
        cmd = ["pytest", "-v"] + tests + self.pytest_args

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            print(f"Chunk {chunk_id} failed to process")

        return process.returncode, stdout.decode(), stderr.decode()


if __name__ == "__main__":
    runner = ParallelPytestRunner(pytest_args=['tests/'])
    tests = runner.collect_tests()
    chunks = runner.chunk_tests(tests)

    for i, chunk in enumerate(chunks, 1):
        returncode, stdout, stderr = asyncio.run(runner.run_chunk(i, chunk))