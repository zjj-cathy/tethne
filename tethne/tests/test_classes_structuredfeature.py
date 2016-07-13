import sys
sys.path.append('./')

from collections import Counter

import unittest

from tethne.classes.feature import StructuredFeature, StructuredFeatureSet


class TestStructuredFeatureSetToGensim(unittest.TestCase):
    def test_to_gensim_corpus(self):
        tokens1 = [chr(i) for i in range(65, 250)]
        tokens2 = [chr(i) for i in range(65, 250)][::-1]
        contexts1 = [('sentence', [0, 25, 57, 89, 124, 156, 172]),
                     ('paragraph', [0, 89, 172])]
        contexts2 = [('paragraph', [0, 101])]
        feature1 = StructuredFeature(tokens1, contexts1)
        feature2 = StructuredFeature(tokens2, contexts2)
        features = {
            'first': feature1,
            'second': feature2,
        }
        fset = StructuredFeatureSet(features)
        # print fset.index
        gensim_corpus = fset.to_gensim_corpus('paragraph')
        self.assertIsInstance(gensim_corpus, list)
        self.assertEqual(len(gensim_corpus), 5)
        self.assertIsInstance(gensim_corpus[0], list)
        self.assertIsInstance(gensim_corpus[0][0], str)

    def test_end_to_end(self):
        """
        Runs the Gensim LDA workflow
        (https://radimrehurek.com/gensim/wiki.html#latent-dirichlet-allocation).
        """
        from tethne.readers.wos import read
        corpus = read('./tethne/tests/data/wos3.txt')
        from nltk.tokenize import word_tokenize
        corpus.index_feature('abstract', word_tokenize, structured=True)

        gensim_corpus = corpus.features['abstract'].to_gensim_corpus()
        from gensim import corpora, models

        dictionary = corpora.Dictionary(gensim_corpus)
        corpus = [dictionary.doc2bow(text) for text in gensim_corpus]
        model = models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary,
                                         num_topics=5, update_every=1,
                                         chunksize=100, passes=1)
        model.print_topics()


class TestStructuredFeatureSet(unittest.TestCase):
    def setUp(self):
        self.tokens1 = list(range(0, 205))
        self.tokens2 = list(range(0, 42))
        contexts1 = [('sentence', [0, 25, 57, 89, 124, 156, 172, 191]),
                     ('paragraph', [0, 89, 172])]
        contexts2 = [('paragraph', [0, 29])]

        self.feature1 = StructuredFeature(self.tokens1, contexts1)
        self.feature2 = StructuredFeature(self.tokens2, contexts2)

    def test_init(self):
        features = {
            'first': self.feature1,
            'second': self.feature2,
        }
        fset = StructuredFeatureSet(features)
        self.assertEqual(len(fset), len(features))
        self.assertIsInstance(fset.unique, set)

        N_features_expected = max(len(self.tokens1), len(self.tokens2))
        self.assertEqual(fset.N_features, N_features_expected)
        self.assertEqual(fset.N_documents, len(features))

        expected_count = Counter(self.tokens1 + self.tokens2)[0]
        self.assertEqual(fset.count(0), expected_count)

        self.assertEqual(len(fset.papers_containing(0)), len(features))

    def test_transform(self):
        features = {
            'first': self.feature1,
            'second': self.feature2,
        }
        fset = StructuredFeatureSet(features)
        xf = lambda f, c, fc, dc: f if f % 2 == 0 else False
        fset2 = fset.transform(xf)
        self.assertGreater(len(fset.index), len(fset2.index))

    def test_select_context(self):
        features = {
            'first': self.feature1,
            'second': self.feature2,
        }
        fset = StructuredFeatureSet(features)

        N_paragraphs = len(fset.features['first'].contexts['paragraph']) + \
                       len(fset.features['second'].contexts['paragraph'])
        papers, chunks = fset.context_chunks('paragraph')

        self.assertEqual(len(chunks), N_paragraphs)
        self.assertEqual(len(papers), len(features))


class TestStructuredFeature(unittest.TestCase):
    def setUp(self):
        self.testTokens = range(0, 50)
        self.testSentence = ('sentence', [0, 20, 27, 34])
        self.testPara = ('paragraph', [0, 27])

    def test_init(self):
        contexts = [self.testPara, self.testSentence]
        sfeature = StructuredFeature(self.testTokens, contexts)
        self.assertEqual(len(sfeature), len(self.testTokens))
        self.assertEqual(len(sfeature.contexts), len(contexts))

    def test_select(self):
        name, sentences = self.testSentence

        contexts = [self.testPara, self.testSentence]
        sfeature = StructuredFeature(self.testTokens, contexts)
        selected_sentences = sfeature['sentence']

        self.assertIsInstance(sentences, list)
        self.assertEqual(len(sentences), len(sentences), """
        __getitem__(context) should return all tokens, separated into context
        chunks.""")

    def test_select_chunk(self):
        name, sentences =self.testSentence
        sentence_size = sentences[1] - sentences[0]

        contexts = [self.testPara, self.testSentence]
        sfeature = StructuredFeature(self.testTokens, contexts)

        selected_sentence = sfeature[('sentence', 0)]

        self.assertIsInstance(selected_sentence, list)
        self.assertEqual(len(selected_sentence), sentence_size, """
        __getitem__((context, chunk)) should the tokens in that chunk""")

    def test_add_context(self):
        name = 'orthogonal'
        indices = [0, 5, 22, 38]
        newContext = (name, indices)

        contexts = [self.testPara, self.testSentence]
        sfeature = StructuredFeature(self.testTokens, contexts)
        N_contexts_prior = len(sfeature.contexts)
        sfeature.add_context(*newContext)
        N_contexts_post = len(sfeature.contexts)

        self.assertGreater(N_contexts_post, N_contexts_prior)

        selected_sentences = sfeature['orthogonal']
        self.assertEqual(len(selected_sentences), len(indices))

        selected_sentence = sfeature['orthogonal', 1]
        self.assertEqual(len(selected_sentence), indices[2] - indices[1])


if __name__ == '__main__':
    unittest.main()
