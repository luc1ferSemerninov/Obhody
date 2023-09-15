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
import taskSql




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
        if sql_checker.Main(callback_query.from_user.id) == "True":
            sql_insert.UpdateId("taskId")
            markup = InlineKeyboardMarkup(row_width=2)#создание макета инлайн кнопок
            button1 = InlineKeyboardButton("Готово", callback_data=f"accept{taskSql.Otdelno()}")#создаем кнопки, вводим название кнопки и ее callback
            button2 = InlineKeyboardButton("Не получается", callback_data=f"deny{taskSql.Otdelno()}")
            markup.add(button1, button2)#добавляем кнопки на макет
            await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,
                                        text=f"{user_name} принял обход", reply_markup=Chat()) #редактирование сообщения о принятии обхода
            Action(sql_checker.User(callback_query.from_user.id,),callback_query.from_user.id, "Принял обход", "")
            await bot.send_photo(chat_id=callback_query.from_user.id, photo=r"https://ibb.co/bWKgv8S", caption="1. Включены телевизоры на ресепшене",
                                reply_markup=markup)#отправка первого пункта чек листа лично пользователю, принявшего обходной лист
            sql_insert.UpdateMesId("messageId_first", callback_query.message.message_id)
        else:
            await bot.send_message(callback_query.from_user.id, "тоби пизда")

    
@dp.callback_query_handler(lambda query: query.data in {f"accept{taskSql.Otdelno()}", f"deny{taskSql.Otdelno()}"})#код будет выполняться только в том случае, если callback был accept1 или deny1
async def process_message(callback_query: types.CallbackQuery, state: FSMContext):
    
    kall = list(taskSql.Main(str(taskSql.Otdelno())))
    sql_insert.UpdateId("taskId")
    await bot.answer_callback_query(callback_query.id, f"Вы нажали кнопку: {callback_query.data}")
    if callback_query.data == f"accept{taskSql.Otdelno()}":
        d = "Да"
        sql_insert.UpdateId("idCheck")
    else:
        d = "Нет"
        sql_insert.UpdateId("idCheck")
    all = []
    for item in kall:
        all.append(item)
    task_id = all[0]
    task_name = all[1]
    task_full = all[2]
    task_img = all[3]

    Action(callback_query.from_user.first_name, callback_query.from_user.id, task_name, d)#отправляем в функцию имя пользователя, айди, задачу и сделал он задачу или нет
    markup = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton("Готово", callback_data=f"accept{taskSql.Otdelno()}")
    button2 = InlineKeyboardButton("Не получается", callback_data=f"deny{taskSql.Otdelno()}")
    markup.add(button1, button2)
    #отправляем итог первого пункта в data.txt, чтобы потом отправить одним сообщением
    await bot.send_photo(chat_id=654331925, photo=f"{task_img}",caption=f"{task_id}. {task_full}",reply_markup=markup)#второй пункт чек листа




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
