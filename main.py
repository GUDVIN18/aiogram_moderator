from aiogram import types, Bot, executor, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import json

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize FSM storage
memory_storage = MemoryStorage()

# Initialize bot and dispatcher
bot = Bot(token="")
dp = Dispatcher(bot, storage=memory_storage)

class InputUserData(StatesGroup):
    step_1 = State()
    step_2 = State()
    step_3 = State()

@dp.message_handler(commands=['start'])
async def startpg(message: types.Message, state: FSMContext):
    keyboard_markup = types.InlineKeyboardMarkup()
    chat_message = types.InlineKeyboardButton('chat_message', callback_data='chat_message')
    chanal_message = types.InlineKeyboardButton('chanal_message', callback_data='chanal_message')
    support = types.InlineKeyboardButton('support', callback_data='support')
    keyboard_markup.row(chat_message, chanal_message, support)
    await message.reply('Добро пожаловать!\nЭто бот тестер, нажмите на Inline кнопку ниже', reply_markup=keyboard_markup)



@dp.callback_query_handler(lambda c: c.data == 'chat_message') 
async def handle_chat_message(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text('Введите запрос в чат:')
    await InputUserData.step_1.set()




@dp.callback_query_handler(lambda c: c.data == 'chanal_message') 
async def handle_channel_message(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text('Введите запрос для канала:')
    await InputUserData.step_2.set()



@dp.callback_query_handler(lambda c: c.data == 'support') 
async def handle_channel_message(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text('Админ уже в пути. Введите ваш запрос')
    await InputUserData.step_3.set()




@dp.message_handler(state=InputUserData.step_1, content_types=types.ContentTypes.TEXT)
async def handle_user_message(message: types.Message, state: FSMContext):
    async with state.proxy() as user_data:
        user_data['input_user'] = message.text.replace('\n', ' ')

    a = user_data['input_user']
    user_info = f'ID: {message.from_user.id}\nName: {message.from_user.first_name} {message.from_user.last_name}\nUsername: {message.from_user.username}'
    admin_chat_id = -1002054325995
    await bot.send_message(admin_chat_id, f'Сообщение в чат:\n\n{a}\n\n{user_info}') #как этот текст менять 
    await state.finish()


@dp.message_handler(state=InputUserData.step_2, content_types=types.ContentTypes.TEXT)
async def handle_user_message(message: types.Message, state: FSMContext):
    async with state.proxy() as user_data:
        user_data['input_user'] = message.text.replace('\n', ' ')
        
    a = user_data['input_user']
    user_info = f'ID: {message.from_user.id}\nName: {message.from_user.first_name} {message.from_user.last_name}\nUsername: {message.from_user.username}'
    admin_chat_id = -1001994403707
    await bot.send_message(admin_chat_id, f'Сообщение в канал:\n\n{a}\n\n{user_info}')
    await state.finish()


@dp.message_handler(state=InputUserData.step_3)
async def handle_user_message(message: types.Message, state: FSMContext):
    async with state.proxy() as user_data:
        user_data['input_user'] = message.text.replace('\n', ' ')
        
    a = user_data['input_user']
    user_info = f'ID: {message.from_user.id}\nName: {message.from_user.first_name} {message.from_user.last_name}\nUsername: {message.from_user.username}'
    admin_chat_id = 6424595615

    # Извлечение и печать ID
    user_id = message.from_user.id
    print(f"User ID: {user_id}")

    # Уведомление ожидания ответа
    await bot.send_message(user_id, "Спасибо за ваш запрос! Пожалуйста, ожидайте ответа.")

    keyboard_markup = types.InlineKeyboardMarkup()
    chat_message = types.InlineKeyboardButton('Подключиться', callback_data=f'chat_message_connect:{user_id}')
    keyboard_markup.row(chat_message)
    await bot.send_message(admin_chat_id, f'Сообщение в поддержке\n\nID: {user_id}\n\n{a}\n\n{user_info}', reply_markup=keyboard_markup)

    await state.finish()


# Создайте словарь для отслеживания состояний подключения
connected_users = {}

@dp.callback_query_handler(lambda c: c.data.startswith('chat_message_connect:')) 
async def handle_channel_message(callback_query: types.CallbackQuery):
    # Извлечение user_id из данных колбэка
    user_id = int(callback_query.data.split(':')[-1])

    # Добавление пользователя в словарь подключенных пользователей
    connected_users[user_id] = True

    # Создание клавиатуры для отключения
    keyboard_markup = types.InlineKeyboardMarkup()
    chat_message_unconnect = types.InlineKeyboardButton('Отключиться', callback_data=f'chat_message_unconnect:{user_id}')
    keyboard_markup.row(chat_message_unconnect)
    
    # Отправка сообщения пользователю
    await bot.send_message(user_id, f'Админ подключился')
    await bot.send_message(callback_query.from_user.id, f'Подключение к пользователю {user_id} - успешно!', reply_markup=keyboard_markup)
    connected_users[callback_query.from_user.id] = True






@dp.callback_query_handler(lambda c: c.data.startswith('chat_message_unconnect:')) 
async def handle_channel_unmessage(callback_query: types.CallbackQuery):
    # Извлечение user_id из данных колбэка
    user_id = int(callback_query.data.split(':')[-1])

    # Удаление пользователя из словаря подключенных пользователей
    connected_users[user_id] = None  # или используйте какое-то другое значение вместо None, чтобы обозначить отключение

    # Создание клавиатуры для подключения
    keyboard_markup = types.InlineKeyboardMarkup()
    chat_message_connect = types.InlineKeyboardButton('Подключиться', callback_data=f'chat_message_connect:{user_id}')
    keyboard_markup.row(chat_message_connect)
    
    # Отправка сообщения пользователю
    await bot.send_message(user_id, f'Админ отключился')
    await bot.send_message(callback_query.from_user.id, f'Отключение от пользователя {user_id} - успешно!', reply_markup=keyboard_markup)





@dp.message_handler()
async def handle_all_messages(message: types.Message):
    user_id = message.from_user.id

    # Если пользователь подключен, отправляем сообщение администратору и всем пользователям
    if connected_users.get(user_id, False):
        admin_chat_id = 6424595615  # Замените на ваш реальный идентификатор чата администратора

        # Отправка сообщения администратору
        await bot.send_message(admin_chat_id, f'Пользователь {user_id}: {message.text}')

        # Отправка сообщения всем подключенным пользователям, пока администратор подключен
    
        for user_chat_id, connected in connected_users.items():
            if connected and user_chat_id != user_id and user_chat_id != admin_chat_id:
                await bot.send_message(user_chat_id, f'Админ: {message.text}')










@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def handle_json_message(message: types.Message):
    try:
        # Пытаемся разобрать JSON из текстового сообщения
        json_data = json.loads(message.text)

        # Проверяем наличие обязательных полей в JSON
        if 'user_id' in json_data and 'message' in json_data:
            user_id = json_data['user_id']
            response_message = json_data['message']

            # Ваша логика обработки сообщения
            # Например, отправка ответа пользователю по user_id
            await bot.send_message(user_id, f"Администратор: {response_message}")

        else:
            await bot.send_message(message.chat.id, "Неверный формат JSON. Пожалуйста, укажите 'user_id' и 'message'.")
    except json.JSONDecodeError:
        await bot.send_message(message.chat.id, "Ошибка при разборе JSON. Пожалуйста, укажите корректный JSON.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
