import numpy as np
import re
from fuzzywuzzy import process, fuzz
from navec import Navec
from catboost import CatBoostClassifier
from nltk.tokenize import WordPunctTokenizer

with open('toxic_vocab_extended_red.txt', 'r', encoding='utf-8-sig') as file:
    bad_words = file.read().split()

with open('ignore_list.txt', 'r', encoding='utf-8-sig') as file:
    ignore = file.read().split()


model = Navec.load("navec_hudlit_v1_12B_500K_300d_100q.tar")

tokenizer = WordPunctTokenizer()


def get_text_embedding(words: list, word_model):
    # get text embedding, simply averaging embeddings of words in it
    vec = []
    for word in words:
        try:
            vec.append(word_model[word])
        except KeyError:
            vec.append(np.zeros(300))
    return np.array(vec).mean(axis=0)


class RulesClassifier:

    valid_symbols_re = re.compile('[^a-zа-я]', flags=re.IGNORECASE)

    def __init__(self, bad_words: list, ignore: list, bad_word_threshold=0.75) -> None:

        self.ignore = ignore
        self.list_of_bad_words = bad_words
        self.bad_word_threshold = bad_word_threshold

    def clear_text(self, text: str) -> str:
        return self.valid_symbols_re.sub('', text)

    def predict(self, x: list) -> np.array:
        y = []
        for row in x:
            in_list = False
            for word in row:
                clear_word = self.clear_text(word)
                if clear_word == '':
                    continue
                if process.extractOne(clear_word, self.ignore, scorer=fuzz.ratio)[1] < 70:
                    a = process.extractOne(clear_word, self.list_of_bad_words, scorer=fuzz.ratio)
                    if a[1] > self.bad_word_threshold * 100:
                        in_list = True
                        why = (clear_word + " seems like " + a[0])
                        break

            if in_list:
                y.append(1)
            else:
                y.append(0)
                why = False
        return [np.array(y), why]


class CBClassifier_model:
    def __init__(self, model_path: str) -> None:
        self.CBC_model = CatBoostClassifier()
        self.CBC_model.load_model("CBCToxicClassifier.model", format='cbm')

    def predict(self, x) -> np.array:
        x = self.CBC_model.predict([get_text_embedding(tokenizer.tokenize(text.lower()), model) for text in [x]])
        return x


print("loaded")
