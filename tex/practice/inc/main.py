import sqlite3
from datetime import date
from datetime import datetime
from aiogram import Bot, Dispatcher, executor, types

# Настройка бд
conn = sqlite3.connect('TB_bot', check_same_thread=False)
cursor = conn.cursor()


def db_table_val(person_name: str, date_of_birth: str, person_passport: str, test_date: date, tg_nick: str ):
    cursor.execute('INSERT INTO tasks (fullname, date, passport, date_of_tb_test, tg_nickname) VALUES (?, ?, ?, ?, ?)',
                   (person_name, date_of_birth, person_passport, test_date, tg_nick))
    conn.commit()


# Настройка бота

API_TOKEN = '**************************************'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)



#Обработка команд происходит посредством асинхронных функций вида:
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    global current_chat_id
    current_chat_id = message.from_user.id
    await message.reply("Бот СМОЛСТРОЙГАРАНТ\nУправление и администрирование базой данных сотрудников")


@dp.message_handler(commands=['get_all_workers'])
async def get_workers_list(message: types.Message):
    global last_command
    current_user = await bot.get_chat_member(message.chat.id, message.from_user.id)
    last_command = 'get_all_workers'
    if current_user.status == 'administrator' or current_user.status == 'creator':
        all_workers = sort_and_convert_list_to_str(get_workers_list(False))
        answer = 'Список всех сотрудников:\n' + all_workers
        await message.answer(answer)
        answer = ''
        bad_workers = sort_and_convert_list_to_str(get_bad_or_good_tasks_list(True))
        answer = 'Не прошли тестированиеям:\n' + bad_workers + answer
        await message.answer(answer)
    else:
        await message.answer('У вас нет прав на использование данной команды.')

#Так же предусмотрено разграничение пользователей на администраторов, имеющих полный доступ к базе данных,
# и обычных пользователей (38 строка)

#Добавление и удаление сотрудника из бд прямо в телеграмме:

@dp.message_handler(commands=['new_worker'])
async def new_worker(message: types.Message):
    global current_chat_id
    global last_command
    current_chat_id = message.chat.id
    current_user = await bot.get_chat_member(current_chat_id, message.from_user.id)

    if current_user.status == 'administrator' or current_user.status == 'creator':
        await message.reply(
            'Введите параметры в следующем виде:\nФИО, дата рождения, серия и номер паспорта, дата прохождения тестирования, телеграмм @имя'
            '\nПример:\nИванов Иван Иванович, 01.01.1990, 1111222222, 10.06.23, @username')
        last_command = 'new_worker'
    else:
        await message.reply('У вас нет прав на использование данной команды.')


@dp.message_handler(commands=['delete_worker'])
async def delete_tasks(message: types.Message):
    global current_chat_id
    global last_command
    current_chat_id = message.chat.id

    current_user = await bot.get_chat_member(current_chat_id, message.from_user.id)

    if current_user.status == 'administrator' or current_user.status == 'creator':
        await message.reply('Введите @username сотрудника, которого необходимо удалить')
        last_command = 'delete_worker'
    else:
        await message.reply('У вас нет прав на использование данной команды')


#Так же осуществляется проверка корректности введенных при добавлении сотрудника данных, таких как дата:

def is_data_correct(message):
    current_text = message.split()
    flag = 0
    if len(current_text) != 3 or current_text[1].find(".") != 2:
        flag += 1
    else:
        data = current_text[1].split('.')
        try:
            day = data[0]
            month = data[1]
            year = data[2]
            if int(day) < date.today().day and int(month) < date.today().month and int(year) < date.today().year:
                flag += 1
            if int(day) > 31 or int(month) > 12 or int(year) > 2050:
                flag += 1
            if current_text[2].find("@") != 0:
                flag += 1
        except ValueError:
            flag += 1
    if flag > 0:
        res = 'Неверный формат данных'
    else:
        res = message

    return res

# Работа с бд осуществляется функциями вида:

def get_worker_id():
    try:
        sqlite_connection = sqlite3.connect('')
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sqlite_select_query = """SELECT id from workers"""
        cursor.execute(sqlite_select_query)
        all_workers_ids = cursor.fetchall()
        last_worker_id = all_workers_ids[len(all_workers_ids) - 1]
        lenth_of_str = len(last_worker_id)
        res = str(last_worker_id)[1:lenth_of_str - 3]
        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")

    return res


