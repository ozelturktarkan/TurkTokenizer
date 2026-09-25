import concurrent.futures, os, unittest
from turktokenizer_native import NativeTokenizer, NativeError

@unittest.skipUnless(os.environ.get('TURKTOKENIZER_RUNTIME'),'Set TURKTOKENIZER_RUNTIME for integration tests')
class Integration(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.t=NativeTokenizer()
    @classmethod
    def tearDownClass(cls): cls.t.close()
    def test_roundtrip_and_yont(self):
        for text in ['Çocuk öğretmenin kitabını okudu.',"Ankara’ya 123 🙂\n\tİSTANBUL",'evlerimizden','']:
            self.assertEqual(self.t.decode(self.t.encode(text)),text)
        r=self.t.analyze('Çocuk öğretmenin kitabını okudu.')
        self.assertEqual(r['binding']['status'],'G0_CONSENSUS')
        self.assertEqual(r['binding']['conditional_role_answer']['subject'],0)
        self.assertEqual(r['baseline']['input_ids'],self.t.encode('Çocuk öğretmenin kitabını okudu.'))
    def test_budget_and_invalid_input(self):
        r=self.t.analyze('Çocuk öğretmenin kitabını okudu.',node_budget=0)
        self.assertEqual(r['binding']['status'],'INCOMPLETE')
        with self.assertRaises(ValueError): self.t.decode([-1])
        with self.assertRaises(ValueError): self.t.analyze('ev',node_budget=True)
        with self.assertRaises(TypeError): self.t.encode(5)
        with self.assertRaises(NativeError): self.t.decode([4294967295])
        self.assertEqual(self.t.decode(self.t.encode('evler')),'evler')
    def test_serialized_threads(self):
        with concurrent.futures.ThreadPoolExecutor(2) as pool:
            results=list(pool.map(self.t.encode,['ev','evler']))
        self.assertEqual([self.t.decode(x) for x in results],['ev','evler'])
    def test_closed(self):
        t=NativeTokenizer(); t.close(); t.close()
        with self.assertRaises(NativeError):t.encode('ev')

if __name__=='__main__':unittest.main()
