import unittest
import release_compatibility as rc
class CompatibilityTests(unittest.TestCase):
    def test_canonical_core_tuple_matches_source_metadata(self):
        m,e=rc.validate(); self.assertFalse(e); self.assertEqual(m['order'],['axiom-rag','axiom-apex','axiom-ason']); self.assertFalse(m['publication_authorized'])
if __name__=='__main__': unittest.main()
