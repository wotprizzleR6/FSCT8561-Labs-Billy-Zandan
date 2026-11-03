import unittest
import sys
from pathlib import Path

# Add Lab6 to sys.path
sys.path.insert(0, r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6")
import test_e2e_lab6

# Point NOTEBOOK_PATH to prototype_Lab6.ipynb for testing M2 pass rate
test_e2e_lab6.NOTEBOOK_PATH = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\m2_explorer_3\prototype_Lab6.ipynb")

# Run only the test classes or run full test suite
loader = unittest.TestLoader()
suite = loader.loadTestsFromModule(test_e2e_lab6)
runner = unittest.TextTestRunner(verbosity=1)
result = runner.run(suite)

print(f"\nResults: Ran {result.testsRun} tests.")
print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)}")
print(f"Failures: {len(result.failures)}")
print(f"Errors: {len(result.errors)}")
print(f"Skipped: {len(result.skipped)}")

if result.skipped:
    print("\nRemaining skipped tests (should only be M3 Word doc tests):")
    for test, reason in result.skipped:
        print(f"  {test.id().split('.')[-1]}: {reason}")
