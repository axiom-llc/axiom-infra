import re
import unittest
from pathlib import Path

import portfolio_receipt as pr


class PortfolioWorkflowTests(unittest.TestCase):
    def test_ci_checkout_and_artifact_contract(self):
        text = Path('.github/workflows/portfolio.yml').read_text()
        lines = text.splitlines()
        checkout_paths = set()
        for i, line in enumerate(lines):
            if line.strip() != '- uses: actions/checkout@v4':
                continue
            for child in lines[i + 1:]:
                if child.startswith('      - '):
                    break
                stripped = child.strip()
                if stripped.startswith('path: '):
                    checkout_paths.add(stripped.removeprefix('path: '))
                    break
        self.assertEqual(set(pr.ACTIVE) - checkout_paths, {'axiom-director', 'axiom-harness'})
        self.assertEqual(checkout_paths - set(pr.ACTIVE), set())
        self.assertEqual(text.count('persist-credentials: false'), len(checkout_paths))
        self.assertIn('portfolio_receipt.py --allow-missing -o axiom-portfolio-validation.json', text)
        self.assertIn("if: matrix.python-version == '3.12' && always()", text)
        self.assertIn('uses: actions/upload-artifact@v4', text)
        self.assertIn('if-no-files-found: error', text)


if __name__ == '__main__':
    unittest.main()
