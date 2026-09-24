import unittest
from unittest.mock import patch,Mock
import core_stack as cs
class CoreStackTests(unittest.TestCase):
    def test_reference_binds_rag_and_durable_authorization(self):
        auth={'authorization_id':'a1','authority_ref':'core-stack:offline-reference','policy_digest_or_ref':'p','approved_plan_digest':'d'}
        submit={'authorization':auth,'apex_response':{'run_id':7,'status':'HALTED'}}
        cp=Mock(returncode=0,stdout=__import__('json').dumps(submit),stderr='')
        with patch.dict('os.environ',{'RAG_API_TOKEN':'r','APEX_API_KEY':'a'}), patch.object(cs,'post',return_value={'namespace':'documents-gemini-embedding-2','exists':False}), patch.object(cs,'get',return_value={'authorization':auth,'ledger':{'plan_digest':'d'}}), patch.object(cs.subprocess,'run',return_value=cp), patch.object(cs,'revisions',return_value={'axiom-infra':'x'}):
            r=cs.run(); self.assertEqual(r['status'],'PASS'); self.assertEqual(r['apex']['plan_digest'],'d'); self.assertEqual(r['authorization']['authority_ref'],'core-stack:offline-reference')
if __name__=='__main__': unittest.main()
