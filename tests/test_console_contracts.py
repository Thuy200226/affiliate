from pathlib import Path
import shutil
import subprocess
import unittest


class ConsoleContracts(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node.js optional for console contract tests")
    def test_preview_urls_and_metric_values(self):
        script = Path(__file__).with_name("console_contracts.js")
        result = subprocess.run([shutil.which("node"), str(script)], capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS", result.stdout)
