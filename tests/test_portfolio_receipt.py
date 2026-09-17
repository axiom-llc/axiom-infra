import hashlib,json,unittest
from unittest.mock import patch
import portfolio_receipt as pr
class ReceiptTests(unittest.TestCase):
    def test_registry_covers_all_active_repositories(self): self.assertEqual(set(pr.CHECKS),set(pr.ACTIVE)); self.assertEqual(len(pr.ACTIVE),13)
    def test_api_fallback_is_explicit(self):
        checks,coverage,limitation=pr.checks_for('axiom-api'); self.assertIn(coverage,{'full','partial'})
        if coverage=='partial': self.assertIn('responses',limitation)
    def test_selected_subset_is_explicit_partial_coverage(self):
        with patch.object(pr,'git',return_value=('abc',[])), patch.object(pr,'checks_for',return_value=([['true']],'full',None)), patch.object(pr,'run',return_value={'command':['true'],'exit_code':0,'stdout_tail':'','stderr_tail':''}):
            r=pr.build(['axiom-apex']); self.assertEqual(r['status'],'PASS_WITH_LIMITS'); self.assertEqual(r['coverage'],'partial'); self.assertIn('outside full validation coverage',r['limitation'])
    def test_component_fallback_marks_portfolio_coverage_partial(self):
        with patch.object(pr,'git',return_value=('abc',[])), patch.object(pr,'checks_for',side_effect=lambda n: ([['true']],'partial','tool unavailable') if n=='axiom-blender' else ([['true']],'full',None)), patch.object(pr,'run',return_value={'command':['true'],'exit_code':0,'stdout_tail':'','stderr_tail':''}):
            r=pr.build(); self.assertEqual(r['status'],'PASS_WITH_LIMITS'); self.assertEqual(r['coverage'],'partial')
    def test_missing_is_strict_locally_and_limited_when_allowed(self):
        with patch.object(pr,'ROOT',pr.ROOT/'definitely-missing'):
            self.assertEqual(pr.build(['axiom-apex'])['status'],'FAIL')
            r=pr.build(['axiom-apex'],allow_missing=True); self.assertEqual(r['status'],'PASS_WITH_LIMITS'); self.assertEqual(r['repositories']['axiom-apex']['status'],'UNAVAILABLE')
    def test_digest_is_canonical_and_excludes_self(self):
        body={'schema':'axiom-portfolio-validation/receipt-v2','generated_at':1,'coverage':'full','limitation':None,'repositories':{},'status':'PASS'}
        digest=hashlib.sha256(pr.canonical(body)).hexdigest(); body['status']='FAIL'; self.assertNotEqual(digest,hashlib.sha256(pr.canonical(body)).hexdigest())
if __name__=='__main__': unittest.main()
