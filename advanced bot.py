from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from cfg import *

token = '5845666637:AAF9bkuftijijPKaLa7nhLZFxRvS-EWR4BU'

bot = Bot(token)
dp = Dispatcher(bot)


def load_data():
    global data
    try:
        with open('config.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
    except:
        data = {"Users": {}}


def write_to_json():
    with open('config.json', 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=3)


@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    f_name = message.from_user.first_name
    l_name = message.from_user.last_name
    button_yes = InlineKeyboardButton('Да', callback_data='autoДа')
    button_no = InlineKeyboardButton('Нет', callback_data='autoНет')
    markup_yes_no = InlineKeyboardMarkup(row_width=2).add(button_yes, button_no)

    if str(message.from_user.id) in list(data['Users'].keys()):
        status = data["Users"][str(message.from_user.id)]["status"]
        if l_name is None:
            await message.answer(f'Здравствуйте, {f_name}; ваш статус {status}.\nСпасибо, что пользуетесь нашим ботом!!!')
        else:
            await message.answer(f'Здравствуйте, {f_name} {l_name}; ваш статус {status}.\nСпасибо, что пользуетесь нашим ботом!!!')

    else:
        await message.answer(f'Здравствуйте, {f_name} {l_name}.\nЖелаете ли вы создать нового пользователя?', reply_markup=markup_yes_no)


@dp.callback_query_handler()
async def call_back_yes_no(callback: types.CallbackQuery):
    if callback.data == 'autoДа':
        await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
        await bot.send_message(chat_id=callback.from_user.id, text='Отлично, создан новый пользователь.')
        if callback.from_user.last_name is not None:
            data['Users'][str(callback.from_user.id)] = {'first name': callback.from_user.first_name, 'last name': callback.from_user.last_name, 'operations': operations, 'status': ''}
        else:
            data['Users'][str(callback.from_user.id)] = {'first name': callback.from_user.first_name, 'operations': operations, 'status': ''}


    elif callback.data == 'utoНет':
        await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
        await bot.send_message(chat_id=callback.from_user.id, text='Ладно, в следующий раз...')


@dp.message_handler(commands=['createlesson'])
async def createlesson(message: types.Message):
    try:
        status = data['Users'][str(message.from_user.id)]['status']
        if status == 'teacher' or status == 'admin':
            await message.answer(f'Вы ,{message.from_user.first_name},'f' решили создать урок.\nПожалуйста назовите урок.')
            data['Users'][str(message.from_user.id)]['operations']['create_lesson'] = True
    except:
        await message.answer('У вас отсутствует статус, либо недостаточно прав.')


@dp.message_handler(content_types=['text'])
async def chating(message: types.Message):
    if data['Users'][str(message.from_user.id)]['operations']['sending_code_to_get_status_teacher']:
        t_code = message.text
        if t_code in main_keys_teachers:
            main_keys_teachers.remove(t_code)
            data['Users'][str(message.from_user.id)]['lessons'] = {}
            data['Users'][str(message.from_user.id)]['status'] = 'teacher'
            await message.answer(f'Ваш user обновлён -> {data["Users"][str(message.from_user.id)]}')
            data['Users'][str(message.from_user.id)]['operations']['sending_code_to_get_status_teacher'] = False
            write_to_json()

        else:
            await message.answer(f'Отправте код ещё раз, не распознан {message.text}.') if random.randint(0, 1) else await message.answer(f'Не пон, отправь код ещё раз.')

    elif data['Users'][str(message.from_user.id)]['operations']['sending_code_to_get_status_admin']:
        a_code = message.text
        if a_code in main_keys_admins:
            main_keys_admins.remove(a_code)
            data['Users'][str(message.from_user.id)]['lessons'] = {}
            data['Users'][str(message.from_user.id)]['status'] = 'admin'
            await message.answer(f'Ваш user обновлён -> {data["Users"][str(message.from_user.id)]}')
            data['Users'][str(message.from_user.id)]['operations']['sending_code_to_get_status_admin'] = False
            write_to_json()

        else:
            await message.answer(f'Отправте код ещё раз, не распознан {message.text}.') if random.randint(0, 1) else await message.answer(f'Не пон, отправь код ещё раз.')

    elif data['Users'][str(message.from_user.id)]['operations']["don't know what to do"]:
        button_start = types.KeyboardButton('/start')
        button_help = types.KeyboardButton('/help')
        button_showabilities = types.KeyboardButton('/showabilities')
        markup = types.ReplyKeyboardMarkup(row_width=3).add(button_start, button_help, button_showabilities)
        await message.answer('Если вы не знаете, что делать воспользуйтесь этими *командами*, надеюсь они вам помогут', parse_mode='Markdown', reply_markup=markup)
        data['Users'][str(message.from_user.id)]['operations']["don't know what to do"] = False

    if data['Users'][str(message.from_user.id)]['operations']['create_lesson']:
        current_lesson = message.text
        lessons[current_lesson] = {
            "Отцените урок от 1 до 10": '',
            "Отцените свое понимание изученного материала от 1 до 10": '',
            "Отцените, насколько понятно учитель объясняет материал от 1 до 10": '',
            "Сколько раз вам хотелось вздремнуть ": ''
        }
        await message.answer(f'Отлично, урок  ━━ {current_lesson} создан.')
        data['Users'][str(message.from_user.id)]['operations']['create_lesson'] = False


if __name__ == '__main__':
    load_data()
    executor.start_polling(dp)
