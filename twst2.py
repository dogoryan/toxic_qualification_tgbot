from custom_classes import RulesClassifier, CBClassifier_model, bad_words, get_text_embedding
from nltk.tokenize import WordPunctTokenizer

import numpy as np
import pandas as pd

from navec import Navec

model = CBClassifier_model('CBCToxicClassifier_fulldf.model')
#model.load_model('CBCToxicClassifier.model', format='cbm')

comp_to_list = RulesClassifier(bad_words, bad_word_threshold = 0.85)
tokenizer = WordPunctTokenizer()

def check_is_toxic(text: str) -> bool:

    y = model.predict(text)
    y = bool(y)
    return y



@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await message.reply("Привет! Напиши мне сообщения, и я скажу, токсик ли ты!")


@dp.message_handler()
async def is_tox(message: types.Message):

    if check_is_toxic(str(message.text)):
        answer = f"Ты токсик, однозначно!"
    else:
        answer = "О, приятно иметь с Вами дело, Вы не токсик!"

    await message.reply(answer)









from fuzzywuzzy import process, fuzz

with open('toxic_vocab_extended_red.txt', 'r', encoding='utf-8-sig') as file:
    bad_words = file.read().split()





for index in range(len(bad_words)):
    print(f"Iteraction №{index} of {len(bad_words)}...")
    for ind in range(index + 1,len(bad_words)):
        if fuzz.ratio(bad_words[index], bad_words[ind]) > 60:
            bad_words[ind] = "удалить"

bad_words_optimized = []


for el in bad_words:
    if el != "удалить":
      bad_words_optimized.append(el)




with open('toxic_vocab_optimized.txt', 'w') as filehandle:
    for listitem in bad_words_optimized:
        filehandle.write('%s\n' % listitem)


