import numpy as np
import pandas as pd

from navec import Navec

from custom_classes import RulesClassifier, CBClassifier_model, bad_words, get_text_embedding, ignore
from nltk.tokenize import WordPunctTokenizer

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import aiogram
import asyncio

import json
import copy













bot = Bot(token='XXXXXXX-XXXXXXXXXXXX')
dp = Dispatcher(bot)

model = CBClassifier_model('CBCToxicClassifier_fulldf.model')
# model.load_model('CBCToxicClassifier.model', format='cbm')
global shadow_mode
shadow_mode = False

comp_to_list = RulesClassifier(bad_words, ignore, bad_word_threshold=0.78)
tokenizer = WordPunctTokenizer()



def check_is_toxic(text: str) -> bool:
    tokenized_data = tokenizer.tokenize(text.lower())
    is_toxic = comp_to_list.predict([tokenized_data])

    if bool(is_toxic[0]):

        return is_toxic[1]

    else:
        return False


# load data from json
def load_data(path: str) -> dict:
    data = None
    try:
        with open(path, 'r') as file:
            data = json.loads(file.read())
    except Exception as e:
        if e == json.JSONDecodeError:
            print('Data is crash')
            exit(1)
    return data


# save data to json
def save_data(data: dict, path: str) -> None:
    with open(path, 'w') as file:
        file.write(json.dumps(data))


# add chat to data
def add_chat(chat_id: str, data: dict) -> dict:
    chat_id = str(chat_id)

    data[chat_id] = copy.deepcopy(data['000000000000'])


    return data


# create user in the data
def create_user(user_id: int, chat_id: str, data) -> dict:
    # create user
    data[chat_id]['user_id'].append(user_id)
    data[chat_id]['rating'].append(0)
    data[chat_id]['toxic'].append(0)
    data[chat_id]['positive'].append(0)
    data[chat_id]['is_toxic'].append(False)
    # return data
    return data





# check the message is not from the group
async def check_the_message_is_not_from_the_group(message: types.Message) -> bool:
    if message.chat.type != 'group' and message.chat.type != 'private':
        await message.reply('Эта команда работает только в группах')
        return True
    return False


data = load_data('users.json')

@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):

    await message.reply("Привет! Добавь меня в чат!")


@dp.message_handler(commands=["silent_mode"])
async def start_command(message: types.Message):
    global shadow_mode
    if shadow_mode:
        shadow_mode = False
        await message.answer("Бесшумный режим выключен")
    else:
        shadow_mode = True
        await message.answer("Включен бесшумный режим")







@dp.message_handler(commands=['get_statistics'])
async def get_statistics(message: types.Message):
    #if message.chat.type != 'group' and message.chat.type != 'supergroup':
        #await message.reply('Эта команда работает только в группах')
        #return


    chat_id = str(message.chat.id)

    data = load_data('users.json')

    if chat_id not in data:
        await message.reply('Статистики пока нет')
        return

    users_stat = []
    for i in range(len(data[chat_id]['user_id'])):

        try:
            user = await bot.get_chat_member(message.chat.id, data[chat_id]['user_id'][i])
            username = user["user"]["username"] if user["user"]["username"] is not None \
                else user["user"]["last_name"] + ' ' + user["user"]["first_name"]

            users_stat.append([username,
                               'rating ' + str(data[chat_id]['rating'][i]), 'toxic ' + str(data[chat_id]['toxic'][i]),
                               'positive ' + str(data[chat_id]['positive'][i])])
        except Exception:
            pass


    statistics = ''
    for row in users_stat:
        buf = ''

        for item in row:
            buf += str(item) + '|'

        buf += '\n'
        statistics += buf

    statistics = 'Статистики пока нет' if statistics == '' else statistics

    statistics_list = statistics.split('\n')

    if len(statistics_list) < 10:
        await message.answer(statistics)
    else:
        await message.answer("Статистика:")

        step = 10

        for i in range(0, len(statistics_list), step):
            statistics_package = '\n'.join(statistics_list[i:i + step])

            await message.answer(statistics_package)




@dp.message_handler(content_types=['text'])
async def moderate(message: types.Message):

    #if message.chat.type != 'group' and message.chat.type != 'supergroup':
        #await message.reply('Эта команда работает только в группах')
        #return
    global shadow_mode
    chat_id = str(message.chat.id)
    # get user
    user = message.from_user

    # load users data
    data = load_data('users.json')

    if chat_id not in data:
        data = add_chat(chat_id, data)

        # find user in data
    user_index = -1
    if user.id in data[chat_id]['user_id']:
        for i, user_id in enumerate(data[chat_id]['user_id']):
            if user.id == user_id:
                user_index = i
                break
    else:
        # create user in data
        data = create_user(user.id, chat_id, data)
        user_index = len(data[chat_id]['user_id']) - 1



    # check the user for toxicity and change rating
    check = check_is_toxic(str(message.text))

    if check:
        data[chat_id]['rating'][user_index] -= 1
        data[chat_id]['toxic'][user_index] += 1
        global shadow_mode
        if not shadow_mode:
            answer = f"avoid this word!\n{check}"
            await message.reply(answer)
    else:
        data[chat_id]['rating'][user_index] += 0.25
        data[chat_id]['positive'][user_index] += 1

    # save user data
    save_data(data, 'users.json')


if __name__ == '__main__':
    executor.start_polling(dp)
