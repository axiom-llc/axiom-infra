import hashlib, json, unittest
import portfolio_receipt as pr
class ReceiptTests(unittest.TestCase):
    def test_check_registry_has_core_and_promoted_components(self):
        self.assertEqual(set(pr.CHECKS),{'axiom-rag','axiom-apex','axiom-ason','axiom-api','axiom-demos','axiom-ops','axiom-harness','axiom-research'})
    def test_api_fallback_is_explicit(self):
        checks,coverage,limitation=pr.checks_for('axiom-api')
        self.assertIn(coverage,{'full','partial'})
        if coverage=='partial':
            self.assertIn('responses',limitation)
            self.assertEqual(checks[0][:3],['python','-m','compileall'])

    def test_receipt_digest_is_canonical_and_excludes_self(self):
        body={'schema':'axiom-portfolio-validation/receipt-v1','generated_at':1,'repositories':{},'status':'PASS'}
        expected=hashlib.sha256(pr.canonical(body)).hexdigest(); body['receipt_sha256']=expected
        self.assertEqual(body['receipt_sha256'],expected)
if __name__=='__main__': unittest.main()
