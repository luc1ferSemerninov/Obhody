import time
from aiogram import Bot, Dispatcher, executor, types

from aiogram.types import InlineKeyboardMarkup, \
    InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
import asyncio
from aiogram.utils import executor
from datetime import datetime, time
import sql_checker
import sql_insert
import taskSql

keyApi = "AIzaSyAeQxJTUyhUvhkKbiQqcXplBVZf0zIQ8No"
pressed_buttons = set()
storage = MemoryStorage()
API_TOKEN = '6546931263:AAEn7hhTRCZ8lp-Srkq623hlznTZsc5QWZ4'
telegram_bot_api_key = API_TOKEN
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)
chatID = -854534644
class status(StatesGroup):
    denied = State()

array = taskSql.MainAll()
for i in array:
    x = i[0]
print(x)

def Action(userId, action, idAction): #функция которая собирает данные об обходе и передает другой функции чтобы записать в таблицу
    now = datetime.now()
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
    print(123123)

async def send_scheduled_message(text):
    markup = InlineKeyboardMarkup(row_width=1)

    # Добавляем кнопку, о принятии обхода
    button1 = InlineKeyboardButton("Принять", callback_data="Принять")
    markup.add(button1)

    await bot.send_message(chatID, text=text, reply_markup=markup)#отправляем наше оповещение в общий чат

@dp.callback_query_handler(lambda query: query.data in {"Принять"})
async def process_callback_button(callback_query: types.CallbackQuery, state: FSMContext):
    now = datetime.now()
    sql_insert.UpdateId("taskId")
    sql_insert.UpdateMesId("idCheck", "1")
    sql_insert.UpdateId("DailyTaskId")
    user = sql_checker.User(callback_query.from_user.id)
    await bot.edit_message_text(chat_id=chatID, message_id=callback_query.message.message_id, text=f"{user} принял обход в {now.strftime('%H:%M')}")
    sql_insert.UpdateMesId("messageId_first", callback_query.message.message_id)
    Action(callback_query.from_user.id, action="Принял обход", idAction="")
    sql_insert.UpdateId("taskId")
    await Next(callback_query.from_user.id)
    
async def Next(user):
    if sql_insert.GetId("idCheck") == x+1:
        await Final(user)
    else:
        arr = taskSql.Main(taskSql.Otdelno())
        print(arr)
        task_id = arr[0]
        task_mini = arr[1]
        task_full = arr[2]
        task_img = arr[3]

        markup = InlineKeyboardMarkup(row_width=2)
        button1 = InlineKeyboardButton("Готово", callback_data="accept")
        button2 = InlineKeyboardButton("Не получается", callback_data="deny")
        markup.add(button1, button2)

        await bot.send_photo(user, photo=task_img[0], caption=task_full[0], reply_markup=markup)
        Action(user, task_mini[0], "")

@dp.callback_query_handler(lambda query: query.data in {"accept"})
async def process_callback_button(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    sql_insert.Tasker("Да", sql_insert.GetId("taskId"))
    sql_insert.UpdateId("taskId")
    sql_insert.UpdateId("idCheck")
    await Next(callback_query.from_user.id)

@dp.callback_query_handler(lambda query: query.data in {"deny"})
async def process_callback_button(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    sql_insert.Tasker("Нет", sql_insert.GetId("taskId"))
    sql_insert.UpdateId("taskId")
    sql_insert.UpdateId("idCheck")
    await bot.send_message(chat_id=callback_query.from_user.id, text="В чем проблема?")
    await status.denied.set()

@dp.message_handler(state=status.denied)
async def process_message(message: types.Message, state: FSMContext):
    sql_insert.TaskUpdate(message.text, sql_insert.GetId("taskId")-1)
    await bot.delete_message(message.from_user.id, message_id=message.message_id-1)
    await bot.delete_message(message.from_user.id, message_id=message.message_id)
    await state.finish()
    await Next(message.from_user.id)

async def Final(user):
    now = datetime.now()
    await bot.send_message(user, "Спасибо, Вы завершили обход!")
    Action(user, "Завершил обход", "")
    person = sql_checker.User(user)
    await bot.edit_message_text(chat_id=chatID, message_id=sql_insert.GetId("messageId_first"), text=f"{person} завершил обход в {now.strftime('%H:%M')}")

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