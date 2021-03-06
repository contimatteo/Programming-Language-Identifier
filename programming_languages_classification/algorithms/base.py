# /usr/bin/env python3

import json
from utils import FileManager
from dataset import DatasetInstance
import keras.preprocessing.text as kpt
from utils import ConfigurationManager
from keras.models import load_model
import joblib
from dataset import DatasetManager


TOKENIZER_CONFIG: dict = ConfigurationManager.tokenizerConfiguration
ESCAPED_TOKENS = ConfigurationManager.escaped_tokens


class _BaseAlgorithm:

    def __init__(self):
        self.type: str = 'MISSING'
        self.Dataset: DatasetInstance = None
        self.model: None
        self.config: dict = {}
        self.DatasetManger = DatasetManager()

    def initialize(self):
        # load the dataset
        self.DatasetManger.initialize(self.type).load()
        # save the dataset instance
        self.Dataset = self.DatasetManger.Dataset

        return self

    #

    def importVocabulary(self):
        return json.loads(FileManager.readFile(FileManager.getVocabularyFileUrl(self.type)))

    def exportVocabulary(self, indexes):
        FileManager.writeFile(FileManager.getVocabularyFileUrl(self.type), json.dumps(indexes))
        return self

    def importKerasTrainedModel(self):
        self.model = load_model(FileManager.getTrainedModelFileUrl(self.type))
        return self

    def importScikitTrainedModel(self):
        self.model = joblib.load(FileManager.getTrainedModelFileUrl(self.type))
        return self

    def exportKerasTrainedModel(self):
        self.model.save(FileManager.getTrainedModelFileUrl(self.type))
        return self

    def exportScikitTrainedModel(self):
        joblib.dump(self.model, FileManager.getTrainedModelFileUrl(self.type))
        return self

    def exportClassificationReport(self, report: str):
        FileManager.writeFile(FileManager.getReportFileUrl(self.type), report)

    #

    def generateWordsIndexesForUnknownExample(self, wordsIndexes, source: str):
        wordvec = []
        max_features: int = self.config['max_features']

        # one really important thing that `text_to_word_sequence` does
        # is make all texts the same length -- in this case, the length
        # of the longest text in the set.
        for word in kpt.text_to_word_sequence(source, filters=TOKENIZER_CONFIG['filter']):
            if word in wordsIndexes:
                if wordsIndexes[word] <= max_features:
                    wordvec.append([wordsIndexes[word]])
                else:
                    wordvec.append([0])
            else:
                wordvec.append([0])

        return wordvec

    #

    def extractSources(self, dataset: str, sourceType: str = 'parsed'):
        X_raw = []
        Y_raw = []
        sources: dict = self.Dataset.getSources(dataset)

        for language in sources:
            for exampleDict in sources[language]:
                source = str(exampleDict[sourceType])
                source = source.replace(ESCAPED_TOKENS['ALPHA'], '')
                source = source.replace(ESCAPED_TOKENS['NUMBER'], '')
                source = source.replace(ESCAPED_TOKENS['NOT_RELEVANT'], '')
                source = source.replace('\n', ' ')

                source = ' '.join([w for w in source.split(' ') if len(w.strip()) > 0])

                X_raw.append(source)
                Y_raw.append(language)

        return X_raw, Y_raw
