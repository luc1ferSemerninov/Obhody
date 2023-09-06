import time, subprocess
import gspread
from google.oauth2.service_account import Credentials
import aiogram.types
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, executor, types

from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton
import telebot
import re
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
import asyncio
import numpy as np
import logging
import asyncio
from aiogram.utils import executor
from datetime import datetime, time
import json
import sql_checker
import sql_insert
import pymysql




def Check():
    markup = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton("Готово", callback_data="Готово")
    button2 = InlineKeyboardButton("Не получается", callback_data="Не получается")
    markup.add(button1, button2)

    return markup


def Chat():
    markup = InlineKeyboardMarkup(row_width=1)

    # Добавляем кнопки, каждая со своим уникальным идентификатором
    button1 = InlineKeyboardButton("Перейти в чат", url="https://t.me/@next_detour_bot", callback_data="Перейти в чат")
    markup.add(button1)

    return markup


#def SendLog(text):
    #bot = telebot.TeleBot(telegram_bot_api_key)
    #bot.send_message(-729345297, text)


keyApi = "AIzaSyAeQxJTUyhUvhkKbiQqcXplBVZf0zIQ8No"
pressed_buttons = set()
storage = MemoryStorage()
API_TOKEN = '6546931263:AAEn7hhTRCZ8lp-Srkq623hlznTZsc5QWZ4'
telegram_bot_api_key = API_TOKEN
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)
chatID = -854534644
message_id = 0

def Action(name, userId, action, idAction): #функция которая собирает данные об обходе и передает другой функции чтобы записать в таблицу
    now = datetime.now()
    #Worksheet(f'{str(now.date())}',f'{now.strftime("%H:%M")}',#передача даты и времени на таблицу
            #  f'{name}',#передача имени заполняющего
           #       f'{userId}',#передача айди на таблицу
           #   f'{action}',#передача названия пункта в чек листе
           #   f'{idAction}')#сделал он этот пункт или нет
    
    sql_insert.Main(f'{now.strftime("%Y-%m-%d")}', 
                    f'{now.strftime("%H:%M")}', 
                    f'{sql_checker.User(userId)}', 
                    f'{userId}', 
                    f'{action}',
                    f'{sql_insert.GetId("taskId")}',
                    f'{sql_insert.GetId("DailyTaskId")}',
                    f'{"Утренний обход"}', 
                    f'{idAction}', 
                    comm="")




@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply("Привет! На данный момент обходов нет :)")


@dp.message_handler(content_types=['text'])
async def blabla(message, state: FSMContext):
    await bot.send_message(654331925, f'{message.from_user.username}: {message.text}')#это нужно для логов
    Action(message.from_user.first_name, message.from_user.id, "Написал комментарий", f'{message.text}')#отправка комментария пользователя


async def send_scheduled_message(text):
    markup = InlineKeyboardMarkup(row_width=1)

    # Добавляем кнопку, о принятии обхода
    button1 = InlineKeyboardButton("Принять", callback_data="Принять")
    markup.add(button1)

    await bot.send_message(chatID, text=text, reply_markup=markup)#отправляем наше оповещение в общий чат


@dp.callback_query_handler(lambda query: query.data in {"Принять"})
async def process_callback_button(callback_query: types.CallbackQuery, state: FSMContext):
    button = callback_query.data #отслеживание нажатой кнопки для уведомления о нажатии пользователю
    #user_id = callback_query.from_user.id
    user_name = sql_checker.User(callback_query.from_user.id)
    pressed_buttons.add(button)
    await bot.answer_callback_query(callback_query.id, f"Вы нажали кнопку: {button}") #вывод уведомления пользователю о нажатой кнопке
    if button == "Принять":
        if sql_checker.Main(callback_query.from_user.id) != "False":
            sql_insert.UpdateId("taskId")
            markup = InlineKeyboardMarkup(row_width=2)#создание макета инлайн кнопок
            button1 = InlineKeyboardButton("Готово", callback_data="accept1")#создаем кнопки, вводим название кнопки и ее callback
            button2 = InlineKeyboardButton("Не получается", callback_data="deny1")
            markup.add(button1, button2)#добавляем кнопки на макет
            await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,
                                        text=f"{user_name} принял обход", reply_markup=Chat()) #редактирование сообщения о принятии обхода
            Action(sql_checker.User(callback_query.from_user.id,),callback_query.from_user.id, "Принял обход", "")
            await bot.send_photo(chat_id=callback_query.from_user.id, photo=r"https://ibb.co/bWKgv8S", caption="1. Включены телевизоры на ресепшене",
                                reply_markup=markup)#отправка первого пункта чек листа лично пользователю, принявшего обходной лист

            sql_insert.UpdateMesId("messageId_first", callback_query.message.message_id)
            with open("data.txt", "w+") as z:#файл data.txt собирает данные о каждом пункте чек листа, чтобы потом переслать в одном сообщении
                z.write("")
                z.close()
            with open("data.txt", "a") as z:
                z.write(user_name + " принял обход\n")#записываем данные кто принял обход



@dp.callback_query_handler(lambda query: query.data in {"accept1", "deny1"})#код будет выполняться только в том случае, если callback был accept1 или deny1
async def process_message(callback_query: types.CallbackQuery, state: FSMContext):
    sql_insert.UpdateId("taskId")
    await bot.answer_callback_query(callback_query.id, f"Вы нажали кнопку: {callback_query.data}")
    if callback_query.data == "accept1":
        d = "Да"
    else:
        d = "Нет"
    task = "Телевизоры на ресепшене"#название первого пункта
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)#удаляем первый пункт в чек листе
    Action(callback_query.from_user.first_name, callback_query.from_user.id, task, d)#отправляем в функцию имя пользователя, айди, задачу и сделал он задачу или нет
    markup = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton("Готово", callback_data="accept2")
    button2 = InlineKeyboardButton("Не получается", callback_data="deny2")
    markup.add(button1, button2)
    
    with open("data.txt", "a") as z:
        z.write(f"{task} - {d}\n")#отправляем итог первого пункта в data.txt, чтобы потом отправить одним сообщением
    await bot.send_photo(chat_id=callback_query.from_user.id, photo=r"https://ibb.co/NK4qQPD",caption="2. Включены телевизоры и свет возле кассы СРМ",reply_markup=markup)#второй пункт чек листа


#дальше идет копипаста, все последующие пункты одинаково устроены, меняется только задача, картинка и callback кнопок
@dp.callback_query_handler(lambda query: query.data in {"accept2", "deny2"})
async def process_message1(callback_query: types.CallbackQuery, state: FSMContext):
    sql_insert.UpdateId("taskId")
    await bot.answer_callback_query(callback_query.id, f"Вы нажали кнопку: {callback_query.data}")
    if callback_query.data == "accept2":
        d = "Да"
    else:
        d = "Нет"
    task = "СРМ"
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    Action(callback_query.from_user.first_name, callback_query.from_user.id, task, d)
    with open("data.txt", "a") as z:
        z.write(f"{task} - {d}\n")
    markup = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton("Готово", callback_data="accept3")
    button2 = InlineKeyboardButton("Не получается", callback_data="deny3")
    markup.add(button1, button2)
    
    await bot.send_photo(chat_id=callback_query.from_user.id, photo=r"https://ibb.co/hCcsdFV", caption="3. Включены свет и телевизоры в Тронном зале",
                         reply_markup=markup)



@dp.callback_query_handler(lambda query: query.data in {"accept3", "deny3"})
async def process_message(callback_query: types.CallbackQuery, state: FSMContext):
    sql_insert.UpdateId("taskId")
    await bot.answer_callback_query(callback_query.id, f"Вы нажали кнопку: {callback_query.data}")
    if callback_query.data == "accept3":
        d = "Да"
    else:
        d = "Нет"
    task = "Тронный зал"
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    Action(callback_query.from_user.first_name, callback_query.from_user.id, task, d)
    with open("data.txt", "a") as z:
        z.write(f"{task} - {d}\n")
    markup = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton("Готово", callback_data="accept4")
    button2 = InlineKeyboardButton("Не получается", callback_data="deny4")
    markup.add(button1, button2)
    
    await bot.send_photo(chat_id=callback_query.from_user.id, photo=r"https://ibb.co.com/qDnc0GR",caption="4. Включена приточная система на цоколе",reply_markup=markup)




@dp.callback_query_handler(lambda query: query.data in {"accept4", "deny4"})
async def process_message(callback_query: types.CallbackQuery, state: FSMContext):
    sql_insert.UpdateId("taskId")
    await bot.answer_callback_query(callback_query.id, f"Вы нажали кнопку: {callback_query.data}")
    if callback_query.data == "accept4":
        d = "Да"
    else:
        d = "Нет"
    task = "Приточная система"
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    Action(callback_query.from_user.first_name, callback_query.from_user.id, task, d)
    with open("data.txt", "a") as z:
        z.write(f"{task} - {d}\n")
    markup = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton("Готово", callback_data="accept5")
    button2 = InlineKeyboardButton("Не получается", callback_data="deny5")
    markup.add(button1, button2)
    
    await bot.send_photo(chat_id=callback_query.from_user.id, photo=r"https://ibb.co.com/jwgKKQp",caption="5. Включена вытяжная система на цоколе", reply_markup=markup)




@dp.callback_query_handler(lambda query: query.data in {"accept5", "deny5"})
async def process_message(callback_query: types.CallbackQuery, state: FSMContext):
    sql_insert.UpdateId("taskId")
    await bot.answer_callback_query(callback_query.id, f"Вы нажали кнопку: {callback_query.data}")
    if callback_query.data == "accept5":
        d = "Да"
    else:
        d = "Нет"
    task = "Вытяжная система"
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    Action(callback_query.from_user.first_name, callback_query.from_user.id, task, d)
    with open("data.txt", "a") as z:
        z.write(f"{task} - {d}\n")
    markup = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton("Готово", callback_data="accept6")
    button2 = InlineKeyboardButton("Не получается", callback_data="deny6")
    markup.add(button1, button2)
    
    await bot.send_photo(chat_id=callback_query.from_user.id, photo=r"https://ibb.co.com/JFcZG1G",caption="6. Включена подсветка за кассой сувениров",reply_markup=markup)





@dp.callback_query_handler(lambda query: query.data in {"accept6", "deny6"})
async def process_message(callback_query: types.CallbackQuery, state: FSMContext):
    sql_insert.UpdateId("taskId")
    await bot.answer_callback_query(callback_query.id, f"Вы нажали кнопку: {callback_query.data}")
    if callback_query.data == "accept6":
        d = "Да"
    else:
        d = "Нет"
    task = "Подсветка за кассой"
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    Action(callback_query.from_user.first_name, callback_query.from_user.id, task, d)
    with open("data.txt", "a") as z:
        z.write(f"{task} - {d}\n")
    markup = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton("Готово", callback_data="accept7")
    button2 = InlineKeyboardButton("Не получается", callback_data="deny7")
    markup.add(button1, button2)
    
    await bot.send_photo(chat_id=callback_query.from_user.id, photo=r"https://ibb.co.com/rk52sj3", caption="7. Телевизоры включены и работают синхронно",reply_markup=markup)





@dp.callback_query_handler(lambda query: query.data in {"accept7", "deny7"})
async def process_message(callback_query: types.CallbackQuery, state: FSMContext):
    sql_insert.UpdateId("taskId")
    await bot.answer_callback_query(callback_query.id, f"Вы нажали кнопку: {callback_query.data}")
    if callback_query.data == "accept7":
        d = "Да"
    else:
        d = "Нет"
    task ="Телевизоры на третьем"
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    Action(callback_query.from_user.first_name, callback_query.from_user.id, task, d)
    with open("data.txt", "a") as z:
        z.write(f"{task} - {d}\n")
    markup = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton("Готово", callback_data="accept8")
    button2 = InlineKeyboardButton("Не получается", callback_data="deny8")
    markup.add(button1, button2)
    
    await bot.send_photo(chat_id=callback_query.from_user.id, photo=r"https://ibb.co.com/Rc1PK39",caption="8. Аркадный автомат включен и работает исправно",reply_markup=markup)






@dp.callback_query_handler(lambda query: query.data in {"accept8", "deny8"})
async def process_message(callback_query: types.CallbackQuery, state: FSMContext):
    sql_insert.UpdateId("taskId")
    await bot.answer_callback_query(callback_query.id, f"Вы нажали кнопку: {callback_query.data}")
    if callback_query.data == "accept8":
        d = "Да"
    else:
        d = "Да"
    task = "Аркадный автомат"
    
    with open("data.txt", "a") as z:
        z.write(f"{task} - {d}\n")
    markup = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton("Готово", callback_data="accept9")
    button2 = InlineKeyboardButton("Не получается", callback_data="deny9")
    markup.add(button1, button2)
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    media_group = [
        types.InputMediaPhoto(media="https://ibb.co.com/0GkPrBH"),
        types.InputMediaPhoto(media="https://ibb.co.com/cJs1ynz"),
        types.InputMediaPhoto(media="https://ibb.co.com/PZQHnVh")
    ]
    Action(callback_query.from_user.first_name, callback_query.from_user.id, task, d)
    await bot.send_media_group(chat_id=callback_query.from_user.id, media=media_group)
    sql_insert.UpdateMesId("messageId", callback_query.message.message_id)
    await bot.send_message(chat_id=callback_query.from_user.id, text="9. Все плейстейшн и джойстики подключены, воспроизводится заставка", reply_markup=markup)





@dp.callback_query_handler(lambda query: query.data in {"accept9", "deny9"})
async def process_message(callback_query: types.CallbackQuery, state: FSMContext):
    sql_insert.UpdateId("taskId")
    await bot.answer_callback_query(callback_query.id, f"Вы нажали кнопку: {callback_query.data}")
    if callback_query.data == "accept9":
        d = "Да"
    else:
        d = "Нет"
    task = "Плейстейшн и джойстики"
    
    with open("data.txt", "a") as z:
        z.write(f"{task} - {d}\n")
    markup = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton("Готово", callback_data="accept10")
    button2 = InlineKeyboardButton("Не получается", callback_data="deny10")
    markup.add(button1, button2)
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    with open("nuzhno.txt","r") as f:  # файл nuzhno.txt хранит в себе айди обхода, мессадж_айди в обходной группе(кто принял обход), и последнее сообщение
        my_data_dict = json.load(f)
    await bot.delete_message(callback_query.from_user.id, sql_insert.GetId("messageId")+1)
    await bot.delete_message(callback_query.from_user.id, sql_insert.GetId("messageId")+2)
    await bot.delete_message(callback_query.from_user.id, sql_insert.GetId("messageId")+3)
    Action(callback_query.from_user.first_name, callback_query.from_user.id, task, d)
    media_group = [
        types.InputMediaPhoto(media="https://ibb.co.com/p6FqJdT"),
        types.InputMediaPhoto(media="https://ibb.co.com/rkjFxCR")
    ]
    await bot.send_media_group(chat_id=callback_query.from_user.id, media=media_group)
    sql_insert.UpdateMesId("messageId", callback_query.message.message_id)
    await bot.send_message(chat_id=callback_query.from_user.id,
                           text="10. В зоне BrawlStars красиво уложена перефирия, компьютеры работают, телевизор в штатном режиме, кондиционер выставлен на нужную температуру",
                           reply_markup=markup)





@dp.callback_query_handler(lambda query: query.data in {"accept10", "deny10"})
async def process_message(callback_query: types.CallbackQuery, state: FSMContext):
    sql_insert.UpdateId("taskId")
    await bot.answer_callback_query(callback_query.id, f"Вы нажали кнопку: {callback_query.data}")
    if callback_query.data == "accept10":
        d = "Да"
    else:
        d = "Нет"
    task = "BrawlStars"
    
    with open("data.txt", "a") as z:
        z.write(f"{task} - {d}\n")
    markup = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton("Готово", callback_data="accept11")
    button2 = InlineKeyboardButton("Не получается", callback_data="deny11")
    markup.add(button1, button2)
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    with open("nuzhno.txt","r") as f:  # файл nuzhno.txt хранит в себе айди обхода, мессадж_айди в обходной группе(кто принял обход), и последнее сообщение
        my_data_dict = json.load(f)
    await bot.delete_message(callback_query.from_user.id, sql_insert.GetId("messageId")+1)
    await bot.delete_message(callback_query.from_user.id, sql_insert.GetId("messageId")+2)
    Action(callback_query.from_user.first_name, callback_query.from_user.id, task, d)
    await bot.send_photo(chat_id=callback_query.from_user.id, photo=r"https://ibb.co.com/Vg4H7kk",
                         caption="11. В зоне Fortnite красиво уложена перефирия, компьютеры работают, телевизор в штатном режиме, кондиционер выставлен на нужную температуру",
                         reply_markup=markup)




@dp.callback_query_handler(lambda query: query.data in {"accept11", "deny11"})
async def process_message(callback_query: types.CallbackQuery, state: FSMContext):
    sql_insert.UpdateId("taskId")
    await bot.answer_callback_query(callback_query.id, f"Вы нажали кнопку: {callback_query.data}")
    if callback_query.data == "accept11":
        d = "Да"
    else:
        d = "Нет"
    task = "Fortnite"
    
    with open("data.txt", "a") as z:
        z.write(f"{task} - {d}\n")
    markup = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton("Готово", callback_data="accept12")
    button2 = InlineKeyboardButton("Не получается", callback_data="deny12")
    markup.add(button1, button2)
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    Action(callback_query.from_user.first_name, callback_query.from_user.id, task, d)
    await bot.send_photo(chat_id=callback_query.from_user.id, photo=r"https://ibb.co.com/yfH28C1",caption="12. Включена подсветка левой стены возле Hyper",reply_markup=markup)



@dp.callback_query_handler(lambda query: query.data in {"accept12", "deny12"})
async def process_message(callback_query: types.CallbackQuery, state: FSMContext):
    sql_insert.UpdateId("taskId")
    await bot.answer_callback_query(callback_query.id, f"Вы нажали кнопку: {callback_query.data}")
    if callback_query.data == "accept12":
        d = "Да"
    else:
        d = "Нет"
    task = "Левой стена возле Hyper"
    
    with open("data.txt", "a") as z:
        z.write(f"{task} - {d}\n")
    markup = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton("Готово", callback_data="accept13")
    button2 = InlineKeyboardButton("Не получается", callback_data="deny13")
    markup.add(button1, button2)
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    Action(callback_query.from_user.first_name, callback_query.from_user.id, task, d)
    await bot.send_photo(chat_id=callback_query.from_user.id, photo=r"https://ibb.co.com/b3SxQ8d",
                         caption="13. В зоне Hyper красиво уложена перефирия, компьютеры работают, телевизор в штатном режиме, кондиционер выставлен на нужную температуру",
                         reply_markup=markup)


@dp.callback_query_handler(lambda query: query.data in {"accept13", "deny13"})
async def process_message(callback_query: types.CallbackQuery, state: FSMContext):
    sql_insert.UpdateId("taskId")
    await bot.answer_callback_query(callback_query.id, f"Вы нажали кнопку: {callback_query.data}")
    if callback_query.data == "accept13":
        d = "Да"
    else:
        d = "Нет"
    task = "Hyper"
    
    with open("data.txt", "a") as z:
        z.write(f"{task} - {d}\n")
    markup = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton("Готово", callback_data="accept14")
    button2 = InlineKeyboardButton("Не получается", callback_data="deny14")
    markup.add(button1, button2)
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    Action(callback_query.from_user.first_name, callback_query.from_user.id, task, d)
    await bot.send_photo(chat_id=callback_query.from_user.id, photo=r"https://ibb.co.com/tYG1vYS",
                             caption="14. В зоне FirstClass красиво уложена перефирия, компьютеры работают, телевизор в штатном режиме, кондиционер выставлен на нужную температуру",
                             reply_markup=markup)




@dp.callback_query_handler(lambda query: query.data in {"accept14", "deny14"})
async def process_message(callback_query: types.CallbackQuery, state: FSMContext):
    sql_insert.UpdateId("taskId")
    await bot.answer_callback_query(callback_query.id, f"Вы нажали кнопку: {callback_query.data}")
    if callback_query.data == "accept14":
        d = "Да"
    else:
        d = "Нет"
    task = "FirstClass"
    
    with open("data.txt", "a") as z:
        z.write(f"{task} - {d}\n")
    markup = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton("Готово", callback_data="accept15")
    button2 = InlineKeyboardButton("Не получается", callback_data="deny15")
    markup.add(button1, button2)
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    Action(callback_query.from_user.first_name, callback_query.from_user.id, task, d)
    media_group = [
        types.InputMediaPhoto(media="https://ibb.co.com/bsVY1Kg"),
        types.InputMediaPhoto(media="https://ibb.co.com/PthSQbn")
    ]

    await bot.send_media_group(chat_id=callback_query.from_user.id, media=media_group)
    sql_insert.UpdateMesId("messageId", callback_query.message.message_id)
    await bot.send_message(chat_id=callback_query.from_user.id,
                           text="15. В зоне Gorilla красиво уложена перефирия, компьютеры работают, телевизор в штатном режиме, кондиционер выставлен на нужную температуру",
                           reply_markup=markup)







@dp.callback_query_handler(lambda query: query.data in {"accept15", "deny15"})
async def process_message(callback_query: types.CallbackQuery, state: FSMContext):
    sql_insert.UpdateId("taskId")
    await bot.answer_callback_query(callback_query.id, f"Вы нажали кнопку: {callback_query.data}")
    if callback_query.data == "accept15":
        d = "Да"
    else:
        d = "Нет"
    task = "Gorilla"
    
    with open("data.txt", "a") as z:
        z.write(f"{task} - {d}\n")
    markup = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton("Готово", callback_data="accept16")#тут создаем особенный callback кнопок, предпоследнего пункта в чеклисте
    button2 = InlineKeyboardButton("Не получается", callback_data="deny16")
    markup.add(button1, button2)
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    with open("nuzhno.txt","r") as f:  # файл nuzhno.txt хранит в себе айди обхода, мессадж_айди в обходной группе(кто принял обход), и последнее сообщение
        my_data_dict = json.load(f)
    await bot.delete_message(callback_query.from_user.id, sql_insert.GetId("messageId")+1)
    await bot.delete_message(callback_query.from_user.id, sql_insert.GetId("messageId")+2)
    Action(callback_query.from_user.first_name, callback_query.from_user.id, task, d)
    await bot.send_photo(chat_id=callback_query.from_user.id, photo=r"https://ibb.co.com/F3zkSLN",caption="16. В зоне New-York красиво уложена перефирия, компьютеры работают, кондиционер выставлен на нужную температуру",reply_markup=markup)

@dp.callback_query_handler(lambda query: query.data in {"accept16", "deny16"})
async def process_message(callback_query: types.CallbackQuery, state: FSMContext):
    sql_insert.UpdateId("taskId")
    await bot.answer_callback_query(callback_query.id, f"Вы нажали кнопку: {callback_query.data}")
    if callback_query.data == "accept16":
        d = "Да"
    else:
        d = "Нет"
    task = "New-York"
    
    with open("data.txt", "a") as z:
        z.write(f"{task} - {d}\n")
    markup = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton("Готово", callback_data="accept17")#тут создаем особенный callback кнопок, предпоследнего пункта в чеклисте
    button2 = InlineKeyboardButton("Не получается", callback_data="deny17")
    markup.add(button1, button2)

    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)    
    Action(callback_query.from_user.first_name, callback_query.from_user.id, task, d)
    
    await bot.send_photo(chat_id=callback_query.from_user.id, photo=r"https://ibb.co.com/f1LBRjR",caption="17. В фуршетной зоне столы стоят ровно, на телевизорах стоит нужная заставка, кондиционер выставлен на нужную температуру",reply_markup=markup)



@dp.callback_query_handler(lambda query: query.data in {"accept17", "deny17"})
async def process_message(callback_query: types.CallbackQuery, state: FSMContext):
    sql_insert.UpdateId("taskId")
    await bot.answer_callback_query(callback_query.id, f"Вы нажали кнопку: {callback_query.data}")
    if callback_query.data == "accept17":
        d = "Да"
    else:
        d = "Нет"
    task = "Фуршетная зона"
    
    with open("data.txt", "a") as z:
        z.write(f"{task} - {d}\n")
    markup = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton("Готово", callback_data="accept18")#тут создаем особенный callback кнопок, предпоследнего пункта в чеклисте
    button2 = InlineKeyboardButton("Не получается", callback_data="deny18")
    markup.add(button1, button2)
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    Action(callback_query.from_user.first_name, callback_query.from_user.id, task, d)
    await bot.send_photo(chat_id=callback_query.from_user.id, photo=r"https://ibb.co.com/M9JSncW",caption="18. Включена приточная система на четвертом этаже",reply_markup=markup)

@dp.callback_query_handler(lambda query: query.data in {"accept18", "deny18"})
async def process_message(callback_query: types.CallbackQuery, state: FSMContext):
    sql_insert.UpdateId("taskId")
    await bot.answer_callback_query(callback_query.id, f"Вы нажали кнопку: {callback_query.data}")
    if callback_query.data == "accept18":
        d = "Да"
    else:
        d = "Нет"
    task = "Приточная система 4 этаж"
    
    with open("data.txt", "a") as z:
        z.write(f"{task} - {d}\n")
    markup = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton("Готово", callback_data="accept19")#тут создаем особенный callback кнопок, предпоследнего пункта в чеклисте
    button2 = InlineKeyboardButton("Не получается", callback_data="deny19")
    markup.add(button1, button2)

    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    Action(callback_query.from_user.first_name, callback_query.from_user.id, task, d)
    await bot.send_photo(chat_id=callback_query.from_user.id, photo=r"https://ibb.co.com/QNFfpvB",caption="19. Включена вытяжная система четвертого этажа",reply_markup=markup)

@dp.callback_query_handler(lambda query: query.data in {"accept19", "deny19"})
async def process_message(callback_query: types.CallbackQuery, state: FSMContext):
    sql_insert.UpdateId("taskId")
    await bot.answer_callback_query(callback_query.id, f"Вы нажали кнопку: {callback_query.data}")
    if callback_query.data == "accept19":
        d = "Да"
    else:
        d = "Нет"
    task = "Вытяжная система 4 этаж"
    
    with open("data.txt", "a") as z:
        z.write(f"{task} - {d}\n")
    markup = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton("Готово", callback_data="accept20")#тут создаем особенный callback кнопок, предпоследнего пункта в чеклисте
    button2 = InlineKeyboardButton("Не получается", callback_data="deny20")
    markup.add(button1, button2)


    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    Action(callback_query.from_user.first_name, callback_query.from_user.id, task, d)
    await bot.send_photo(chat_id=callback_query.from_user.id, photo=r"https://ibb.co.com/8BqSr8F", caption="20. Ресепшен на четвертом этаже чист",reply_markup=markup)

@dp.callback_query_handler(lambda query: query.data in {"accept20", "deny20"})
async def process_message(callback_query: types.CallbackQuery, state: FSMContext):
    sql_insert.UpdateId("taskId")
    await bot.answer_callback_query(callback_query.id, f"Вы нажали кнопку: {callback_query.data}")
    if callback_query.data == "accept20":
        d = "Да"
    else:
        d = "Нет"
    task = "Ресепшен 4 этаж"
    
    with open("data.txt", "a") as z:
        z.write(f"{task} - {d}\n")
    markup = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton("Готово", callback_data="accept21")#тут создаем особенный callback кнопок, предпоследнего пункта в чеклисте
    button2 = InlineKeyboardButton("Не получается", callback_data="deny21")
    markup.add(button1, button2)


    media_group = [
        types.InputMediaPhoto(media="https://ibb.co.com/fCWzgTH"),
        types.InputMediaPhoto(media="https://ibb.co.com/ccSPxTd"),
        types.InputMediaPhoto(media="https://ibb.co.com/WnKdSkr")
    ]
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    Action(callback_query.from_user.first_name, callback_query.from_user.id, task, d)
    await bot.send_media_group(chat_id=callback_query.from_user.id, media=media_group)
    sql_insert.UpdateMesId("messageId", callback_query.message.message_id)

    await bot.send_message(chat_id=callback_query.from_user.id,
                           text="21. В зале Грин работает Алиса, компьютеры работают, перефирия в чистоте, на телевизоре стоит заставка, кондиционеры в соответствующем режиме",
                           reply_markup=markup)


@dp.callback_query_handler(lambda query: query.data in {"accept21", "deny21"})
async def process_message(callback_query: types.CallbackQuery, state: FSMContext):
    sql_insert.UpdateId("taskId")
    await bot.answer_callback_query(callback_query.id, f"Вы нажали кнопку: {callback_query.data}")
    if callback_query.data == "accept21":
        d = "Да"
    else:
        d = "Нет"
    task = "Грин"
    
    with open("data.txt", "a") as z:
        z.write(f"{task} - {d}\n")
    markup = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton("Готово", callback_data="accept22")#тут создаем особенный callback кнопок, предпоследнего пункта в чеклисте
    button2 = InlineKeyboardButton("Не получается", callback_data="deny22")
    markup.add(button1, button2)
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    await bot.delete_message(callback_query.from_user.id, sql_insert.GetId("messageId")+1)
    await bot.delete_message(callback_query.from_user.id, sql_insert.GetId("messageId")+2)
    await bot.delete_message(callback_query.from_user.id, sql_insert.GetId("messageId")+3)
    Action(callback_query.from_user.first_name, callback_query.from_user.id, task, d)
    media_group = [
        types.InputMediaPhoto(media="https://ibb.co.com/HXms6Fr"),
        types.InputMediaPhoto(media="https://ibb.co.com/vvMSncR"),
        types.InputMediaPhoto(media="https://ibb.co.com/vvMSncR")
    ]
    await bot.send_media_group(chat_id=callback_query.from_user.id, media=media_group)
    sql_insert.UpdateMesId("messageId", callback_query.message.message_id)
    await bot.send_message(chat_id=callback_query.from_user.id,
                           text="22. В зале Бордо на телевизорах стоит заставка, кондиционеры в соответствующем режиме",
                           reply_markup=markup)

@dp.callback_query_handler(lambda query: query.data in {"accept22", "deny22"})
async def process_message(callback_query: types.CallbackQuery, state: FSMContext):
    sql_insert.UpdateId("taskId")
    await bot.answer_callback_query(callback_query.id, f"Вы нажали кнопку: {callback_query.data}")
    if callback_query.data == "accept22":
        d = "Да"
    else:
        d = "Нет"
    task = "Бордо"
    
    with open("data.txt", "a") as z:
        z.write(f"{task} - {d}\n")
    markup = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton("Готово", callback_data="accept23")#тут создаем особенный callback кнопок, предпоследнего пункта в чеклисте
    button2 = InlineKeyboardButton("Не получается", callback_data="deny23")
    markup.add(button1, button2)
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    await bot.delete_message(callback_query.from_user.id, sql_insert.GetId("messageId")+1)
    await bot.delete_message(callback_query.from_user.id, sql_insert.GetId("messageId")+2)
    await bot.delete_message(callback_query.from_user.id, sql_insert.GetId("messageId")+3)
    Action(callback_query.from_user.first_name, callback_query.from_user.id, task, d)
    await bot.send_photo(chat_id=callback_query.from_user.id, photo=r"https://ibb.co.com/W3Svhpr", caption="23. В зале Олимпия включена заставка, караоке работает",reply_markup=markup)





@dp.callback_query_handler(lambda query: query.data in {"accept23", "deny23"})
async def process_message(callback_query: types.CallbackQuery, state: FSMContext):
    sql_insert.UpdateId("taskId")
    await bot.answer_callback_query(callback_query.id, f"Вы нажали кнопку: {callback_query.data}")
    if callback_query.data == "accept23":
        d = "Да"
    else:
        d = "Нет"
    task = "Олимпия"
    
    with open("data.txt", "a") as z:
        z.write(f"{task} - {d}\n")
    markup = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton("Готово", callback_data="acc")#тут создаем особенный callback кнопок, предпоследнего пункта в чеклисте
    button2 = InlineKeyboardButton("Не получается", callback_data="den")
    markup.add(button1, button2)
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    Action(callback_query.from_user.first_name, callback_query.from_user.id, task, d)
    media_group = [
        types.InputMediaPhoto(media="https://ibb.co.com/HXms6Fr"),
        types.InputMediaPhoto(media="https://ibb.co.com/vvMSncR")
    ]
    await bot.send_media_group(chat_id=callback_query.from_user.id, media=media_group)


    sql_insert.UpdateMesId("messageId", callback_query.message.message_id)


    await bot.send_message(chat_id=callback_query.from_user.id,
                           text="24. В зале Лофт работает Алиса и вызов персонала, компьютеры работают, перефирия в чистоте, на телевизоре стоит заставка, кондиционеры в соответствующем режиме, караоке исправно",
                           reply_markup=markup)



@dp.callback_query_handler(lambda query: query.data in {"acc", "den"})
async def process_message2(callback_query: types.CallbackQuery, state: FSMContext):
    sql_insert.UpdateId("taskId")
    await bot.answer_callback_query(callback_query.id, f"Вы нажали кнопку: {callback_query.data}")
    if callback_query.data == "acc":
        d = "Да"
    else:
        d = "Нет"
    task = "Лофт"
    
    with open("data.txt", "a") as z:
        z.write(f"{task} - {d}\n")
    markup = InlineKeyboardMarkup(row_width=1)
    button1 = InlineKeyboardButton("Завершить обход", callback_data="Finish")#тут уже у нас будет callback finish, т.к. чеклист кончился, пора закрывать его
    markup.add(button1)
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    await bot.delete_message(callback_query.from_user.id, sql_insert.GetId("messageId")+1)
    await bot.delete_message(callback_query.from_user.id, sql_insert.GetId("messageId")+2)
    Action(callback_query.from_user.first_name, callback_query.from_user.id, task, d)
    await bot.send_photo(chat_id=callback_query.from_user.id, photo="https://ibb.co/yFWcSqN", caption="Супер! Ты завершил обход", reply_markup=markup)
    sql_insert.UpdateMesId("messageId1", callback_query.message.message_id)




@dp.callback_query_handler(lambda query: query.data in {"Finish"})
async def process_message2(callback_query: types.CallbackQuery, state: FSMContext):
    sql_insert.UpdateId("taskId")
    await bot.answer_callback_query(callback_query.id, f"Вы нажали кнопку: {callback_query.data}")
    with open("data.txt", "r") as z:
        z = z.read() #считываем полностью файл о логах чек листа, кто что сделал и не сделал
    await bot.send_message(654331925, z) #Отправка отчета по обходу
    now = datetime.now()
    await bot.delete_message(callback_query.from_user.id, sql_insert.GetId("messageId1")+1)#удаляем последнее сообщение в личной переписке с ботом
    await bot.edit_message_text(chat_id=chatID, message_id=sql_insert.GetId("messageId_first"),
                                    text=f"{callback_query.from_user.first_name} завершил обход в {now.strftime('%H:%M')}")#редачим сообщение в основной группе с ботом на "завершил обход"
    task = "Завершил обход"

    Action(f'{callback_query.from_user.first_name}', f"{callback_query.from_user.id}", f"{task}", "")
    sql_insert.UpdateId("DailyTaskId")




def Worksheet(date, time, who, userId, action, idAction):
    # Путь к вашему JSON-ключу
    json_keyfile = r'mamapapa1.json'

    # Создание области видимости
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

    # Загрузка JSON-ключа и создание учетных данных
    creds = Credentials.from_service_account_file(json_keyfile, scopes=scope)

    # Подключение к Google Sheets API
    gc = gspread.authorize(creds)

    # Открываем таблицу по URL или названию
    # Если у вас URL, то выглядит так: https://docs.google.com/spreadsheets/d/your-sheet-id/edit
    spreadsheet = gc.open_by_url(r'https://docs.google.com/spreadsheets/d/1Vyp3saWe09_HcTVAp_l-Vm8Kcy9ny2xFYddQbfod92w/edit#gid=0')

    # Получаем доступ к нужному листу
    worksheet = spreadsheet.get_worksheet(0)


    # Запись данных
    with open("nuzhno.txt", "r") as f:
        my_data_dict = json.load(f)#считываем файл, чтобы достать из него айди обхода
    id = my_data_dict["id"]
    allMessage = [f'{date}', f'{time}', f'{who}', f'{userId}', f'{action}', f"{id}", "Утренний обход", f'{idAction}']#записываем все нужные данные в массив
    



async def send_message_at_specific_time(hour, minute, text):
    while True:
        now = datetime.now().time()
        target_time = time(hour, minute)
        # if now.hour == target_time.hour and now.minute == target_time.minute:#сверяемся чтобы время совпадало со временем прихода обхода
        if now.hour == now.hour and now.minute == now.minute:
            await send_scheduled_message(text)# отправляем наш текст о приходе чеклиста
        await asyncio.sleep(24234234)  # Подождать минуту перед следующей проверкой


loop = asyncio.get_event_loop()#лупим наш код
loop.create_task(send_message_at_specific_time(hour=9, minute=50, text="Пупупу, пришел новый обход"))#отправляем наш обход(время, когда должен прийти чеклист, текст для оповещения)
while True:
    executor.start_polling(dp, skip_updates=True)


