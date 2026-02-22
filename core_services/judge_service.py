import subprocess
import tempfile
import os
import time

class JudgeService:
    @staticmethod
    def execute_code(code: str, test_cases: list, timeout_seconds=2.0) -> dict:
        start_time = time.time()
        failures = []
        passed_count = 0

        # Write code to a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(code)
            temp_script_path = temp_file.name

        try:
            for idx, tc in enumerate(test_cases):
                stdin_data = str(tc.get('input', ''))
                expected_output = str(tc.get('output', '')).strip()

                try:
                    # Run subprocess and pipe standard I/O
                    result = subprocess.run(
                        ['python3', temp_script_path],
                        input=stdin_data,
                        text=True,
                        capture_output=True,
                        timeout=timeout_seconds
                    )

                    actual_output = result.stdout.strip()
                    error_output = result.stderr.strip()

                    if result.returncode != 0:
                        failures.append({
                            'test_case': f"Test {idx+1}",
                            'message': 'Runtime Error',
                            'details': error_output
                        })
                    elif actual_output != expected_output:
                        failures.append({
                            'test_case': f"Test {idx+1}",
                            'message': 'Wrong Answer',
                            'expected': expected_output,
                            'actual': actual_output
                        })
                    else:
                        passed_count += 1

                except subprocess.TimeoutExpired:
                    failures.append({'test_case': f"Test {idx+1}", 'message': 'Time Limit Exceeded'})
                    break
        finally:
            if os.path.exists(temp_script_path):
                os.remove(temp_script_path)

        return {
            'passed': len(failures) == 0,
            'passed_count': passed_count,
            'total_tests': len(test_cases),
            'failures': failures,
            'solve_time': time.time() - start_time
        }