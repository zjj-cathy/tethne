import sys
sys.path.append('./')

import unittest

from tethne.classes.feature import Feature, FeatureSet


class TestFeature(unittest.TestCase):
    def test_init_datum(self):
        """
        Initialize with a single token.
        """
        feature = Feature('bob')

        self.assertEqual(len(feature), 1)
        self.assertEqual(feature[0], ('bob', 1))

    def test_init_list(self):
        """
        Initialize with a list of tokens.
        """
        feature = Feature(['bob', 'joe', 'bob', 'bobert', 'bob'])

        self.assertEqual(len(feature), 3)
        self.assertEqual(dict(feature)['bob'], 3)
        self.assertEqual(dict(feature)['joe'], 1)

    def test_init_counts(self):
        """
        Initialize with a list of 2-tuple token values.
        """
        feature = Feature([('bob', 3), ('joe', 1), ('bobert', 1)])

        self.assertEqual(len(feature), 3)
        self.assertEqual(dict(feature)['bob'], 3)
        self.assertEqual(dict(feature)['joe'], 1)

    def test_init_tuples(self):
        feature = Feature([('bob', 'dole'), ('roy', 'snaydon')])

        self.assertEqual(len(feature), 2)
        self.assertEqual(dict(feature)[('bob', 'dole')], 1)

    def test_norm(self):
        feature = Feature([('bob', 3), ('joe', 1), ('bobert', 1)])
        T = sum(zip(*feature)[1])
        for n, r in zip(zip(*feature.norm)[1], zip(*feature)[1]):
            self.assertEqual(n, float(r)/T)
            
    def test_extend(self):
        feature = Feature([('bob', 3), ('joe', 1), ('bobert', 1)])
     
        feature.extend([('bob', 1)])
        self.assertEqual(feature.value('bob'), 4)
        
        feature.extend(['bob'])
        self.assertEqual(feature.value('bob'), 5)        
        
        feature.extend('bob')
        self.assertEqual(feature.value('bob'), 6)        
        
        
    def test_iadd(self):
        feature = Feature([('bob', 3), ('joe', 1), ('bobert', 1)])
   
        feature += [('bob', 1)]
        self.assertEqual(feature.value('bob'), 4)
        
        feature += ['bob']
        self.assertEqual(feature.value('bob'), 5)
        
        feature += 'bob'
        self.assertEqual(feature.value('bob'), 6)        
        
    def test_isub(self):
        feature = Feature([('bob', 3), ('joe', 1), ('bobert', 1)])
   
        feature -= [('bob', 1)]
        self.assertEqual(feature.value('bob'), 2)
        
        feature -= ['bob']
        self.assertEqual(feature.value('bob'), 1)
        
        feature -= 'bob'
        self.assertEqual(feature.value('bob'), 0)           


class TestFeatureSet(unittest.TestCase):
    def test_init_empty(self):
        """
        Initialize with no Features.
        """

        try:
            featureset = FeatureSet()
            featureset.__init__()
        except:
            self.fail()

    def test_init_features(self):
        """
        Initialize with multiple features.
        """
        feature1 = Feature([('bob', 3), ('joe', 1), ('bobert', 1)])
        feature2 = Feature([('bob', 3), ('jane', 1), ('fido', 1)])
        featureset = FeatureSet({'p1': feature1, 'p2': feature2})

        self.assertEqual(len(featureset.features), 2)

        expected = len(feature1.unique | feature2.unique)

        self.assertEqual(len(featureset.index), expected)
        self.assertEqual(len(featureset.lookup), expected)
        self.assertEqual(len(featureset.counts), expected)
        self.assertEqual(len(featureset.documentCounts), expected)
        self.assertEqual(len(featureset.unique), expected)

        self.assertEqual(featureset.documentCount('bob'), 2)
        self.assertEqual(featureset.count('bob'), 6)

        self.assertIn('p1', featureset.papers_containing('bob'))
        self.assertIn('p2', featureset.papers_containing('bob'))

    def test_add_feature(self):
        """
        Initialize empty, then add a feature.
        """
        featureset = FeatureSet()
        feature = Feature([('bob', 3), ('joe', 1), ('bobert', 1)])
        featureset.add('p1', feature)

        self.assertEqual(len(featureset.features), 1)

        expected = len(feature.unique)

        self.assertEqual(len(featureset.index), expected)
        self.assertEqual(len(featureset.lookup), expected)
        self.assertEqual(len(featureset.counts), expected)
        self.assertEqual(len(featureset.documentCounts), expected)
        self.assertEqual(len(featureset.unique), expected)

        self.assertIn('p1', featureset.papers_containing('bob'))

        self.assertEqual(featureset.documentCount('bob'), 1)
        self.assertEqual(featureset.count('bob'), 3)

    def test_top(self):
        featureset = FeatureSet()
        feature = Feature([('bob', 3), ('joe', 1), ('bobert', 1)])
        feature2 = Feature([('blob', 3), ('joe', 1), ('brobert', 1)])
        feature3 = Feature([('blob', 1), ('joe', 1), ('brobert', 1)])
        featureset.add('p1', feature)
        featureset.add('p2', feature2)
        featureset.add('p3', feature3)

        N = 3
        top = featureset.top(N)
        self.assertIsInstance(top, list)
        self.assertIsInstance(top[0], tuple)
        self.assertEqual(len(top), N)
        self.assertSetEqual(set(zip(*top)[0]), set(['blob', 'bob', 'joe']))

        top = featureset.top(N, by='documentCounts')
        self.assertIsInstance(top, list)
        self.assertIsInstance(top[0], tuple)
        self.assertEqual(len(top), N)
        self.assertSetEqual(set(zip(*top)[0]), set(['blob', 'brobert', 'joe']))

    def test_as_matrix(self):
        featureset = FeatureSet()
        feature = Feature([('bob', 3), ('joe', 1), ('bobert', 1)])
        feature2 = Feature([('blob', 3), ('joe', 1), ('brobert', 1)])
        feature3 = Feature([('blob', 1), ('joe', 1), ('brobert', 1)])
        featureset.add('p1', feature)
        featureset.add('p2', feature2)
        featureset.add('p3', feature3)

        M = featureset.as_matrix()
        self.assertEqual(len(M), len(featureset))
        self.assertEqual(len(M[0]), len(featureset.unique))

    def test_as_vector(self):
        featureset = FeatureSet()
        feature = Feature([('bob', 3), ('joe', 1), ('bobert', 1)])
        feature2 = Feature([('blob', 3), ('joe', 1), ('brobert', 1)])
        feature3 = Feature([('blob', 1), ('joe', 1), ('brobert', 1)])
        featureset.add('p1', feature)
        featureset.add('p2', feature2)
        featureset.add('p3', feature3)

        v = featureset.as_vector('p1')
        v_norm = featureset.as_vector('p1', norm=True)

        self.assertIsInstance(v, list)
        self.assertIsInstance(v_norm, list)
        self.assertEqual(len(v), len(v_norm))
        self.assertEqual(len(v), len(featureset.unique))
        self.assertGreater(sum(v), 0)
        self.assertGreater(sum(v_norm), 0)
        self.assertEqual(sum(v_norm), 1.0)


if __name__ == '__main__':
    unittest.main()