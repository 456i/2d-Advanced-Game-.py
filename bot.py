import random
import telebot
from cfg import *
import json


token = '5845666637:AAF9bkuftijijPKaLa7nhLZFxRvS-EWR4BU'
bot = telebot.TeleBot(token)
main_keys_teachers = keys_teachers
main_keys_admins = keys_admins


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



@bot.message_handler(commands=['start'])
def start_message(message):
    f_name = message.from_user.first_name
    l_name = message.from_user.last_name
    if str(message.from_user.id) in list(data['Users'].keys()):
        status = data["Users"][str(message.from_user.id)]["status"]
        if l_name is None:
            bot.send_message(message.chat.id, f'Здравствуйте, {f_name}; ваш статус {status}.\nСпасибо, что пользуетесь нашим ботом!!!')
        else:
            bot.send_message(message.chat.id, f'Здравствуйте, {f_name} {l_name}; ваш статус {status}.\nСпасибо, что пользуетесь нашим ботом!!!')

    else:
        bot.send_message(message.chat.id, f'Здравствуйте, {f_name} {l_name}.\nЖелаете ли вы создать нового пользователя?',
                         reply_markup=create_2_inline_markup('Да', 'frsДа', 'Нет', 'frsНет'))


@bot.callback_query_handler(func=lambda call: True)
def query(call):
    if call.data == 'frsДа' and not (call.from_user.id in list(data['Users'].keys())):
        bot.send_message(call.message.chat.id, 'Отлично!\nСоздан новый пользователь.')
        bot.delete_message(call.message.chat.id, call.message.message_id)

        if call.from_user.last_name is not None:
            data['Users'][str(call.from_user.id)] = {'first name': call.from_user.first_name, 'last name': call.from_user.last_name, 'operations': operations, 'status': ''}
        else:
            data['Users'][str(call.from_user.id)] = {'first name': call.from_user.first_name, 'operations': operations, 'status': ''}

        bot.send_message(call.message.chat.id, 'Укажите ваш статус?', reply_markup=create_3_inline_markup('Student', 'curStudent', 'Teacher', 'curTeacher', 'Admin', 'curAdmin'))
        write_to_json()

    elif call.data == 'frsНет':
        bot.send_message(call.message.chat.id, 'Ладно..')
        bot.delete_message(call.message.chat.id, call.message.message_id)


    if call.data == 'curStudent':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        data['Users'][str(call.from_user.id)]['status'] = 'student'
        data['Users'][str(call.from_user.id)]['lessons'] = {}
        bot.send_message(call.message.chat.id, f'Ваш user обновлён -> {data["Users"][str(call.from_user.id)]}')
        write_to_json()

    elif call.data == 'curTeacher':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Скиньте код')
        data['Users'][str(call.from_user.id)]['operations']['sending_code_to_get_status_teacher'] = True

    elif call.data == 'curAdmin':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Скиньте код')
        data['Users'][str(call.from_user.id)]['operations']['sending_code_to_get_status_admin'] = True


@bot.message_handler(commands=['help'])
def helping(message):
    try:
        bot.send_message(message.chat.id, f'Вас бот обнаружил: вы {data["Users"][str(message.from_user.id)]["first name"]}, ваш статус {data["Users"][str(message.from_user.id)]["status"]}')

    except:
        bot.send_message(message.chat.id, 'Вас бот не обнаружил, пожалуйста синхронизируете ваш текущий аккаунт с ботом\n/start')


@bot.message_handler(commands=['showabilities'])
def show_abilities(message):
    try:
        user_id = str(message.from_user.id)
        status = data['Users'][user_id]['status']
        if status == 'student':
            bot.send_message(message.chat.id, f'Вы, {data["Users"][user_id]["first name"]}, являетесь *учеником*\nВам *доступны следующие* действия:\n/passvote <- оценить урок', parse_mode='Markdown')

        if status == 'teacher':
            bot.send_message(message.chat.id, f'Вы, {data["Users"][user_id]["first name"]}, являетесь *учителем*\nВам *доступны следующие* действия:\n/viewstudents <-посмотреть учеников'
                                              f'\n/viewresults <- посмотреть оценивания учеников\n/inform participant\n/passvote <- оценить урокn\n/createlesson <- создать урок', parse_mode='Markdown')

        if status == 'admin':
            bot.send_message(message.chat.id, f'Вы, {data["Users"][user_id]["first name"]}, являетесь *админом*\nВам доступны *все* действия:\n/viewadmins <-посмотреть админов'
                                              f'\n/viewteachers <- посмотреть учителей\n/viewstudents <- посмотреть учеников\n/passvote <- оценить урок\n/createlesson <- создать урок', parse_mode='Markdown')

    except:
        bot.send_message(message.chat.id, 'Вас бот не обнаружил, пожалуйста синхронизируете ваш текущий аккаунт с ботом\n/start')


@bot.message_handler(commands=['createlesson'])
def create_lesson(message):
    try:
        status = data['Users'][str(message.from_user.id)]['status']
        if status == 'teacher' or status == 'admin':
            bot.send_message(message.chat.id, f'Вы ,{message.from_user.first_name},'f' решили создать урок.\nПожалуйста назовите урок.')
            data['Users'][str(message.from_user.id)]['operations']['create_lesson'] = True
    except:
        bot.send_message(message.chat.id, 'У вас отсутствует статус либо недостаточно прав.')


@bot.message_handler(commands=['viewresults'])
def resulting(message):
    if data['Users'][str(message.from_user.id)]['status'] == 'teacher' or data['Users'][str(message.from_user.id)]['status'] == 'admin':
        results = []
        ides = list(data['Users'].keys())
        for id in ides:
            if data['Users'][id]['status'] == 'student' and id != ides[-1]:
                try:
                    try:
                        results.append(f'{data["Users"][id]["first name"]} {data["Users"][id]["last name"]} {data["Users"][id]["lessons"]},')
                    except:
                        results.append(f'{data["Users"][id]["first name"]} {data["Users"][id]["lessons"]},')
                except:
                    try:
                        results.append(f'{data["Users"][id]["first name"]} {data["Users"][id]["last name"]} не сделал никаких оцениваний,')
                    except:
                        results.append(data['Users'][id]['first name'] + ' не сделал никаких оцениваний,')

            elif data['Users'][id]['status'] == 'student':
                try:
                    try:
                        results.append(f'{data["Users"][id]["first name"]} {data["Users"][id]["last name"]} {data["Users"][id]["lessons"]}.')
                    except:
                        results.append(f'{data["Users"][id]["first name"]} {data["Users"][id]["lessons"]}.')
                except:
                    try:
                        results.append(f'{data["Users"][id]["first name"]} {data["Users"][id]["last name"]} не сделал никаких оцениваний.')
                    except:
                        results.append(data['Users'][id]['first name'] + ' не сделал никаких оцениваний.')

        bot.send_message(message.chat.id, f'Результаты учеников {results}')


@bot.message_handler(commands=['viewadmins'])
def showingadmins(message):
    if data['Users'][str(message.from_user.id)]['status'] == 'admin':
        admins = ''
        ides = list(data['Users'].keys())
        for id in ides:
            if data['Users'][id]['status'] == 'admin' and id != ides[-1]:
                try:
                    admins += f'{data["Users"][id]["first name"]} {data["Users"][id]["last name"]} id{id}, '
                except:
                    admins += f'{data["Users"][id]["first name"]} id{id}, '

            elif data['Users'][id]['status'] == 'admin':
                try:
                    admins += f'{data["Users"][id]["first name"]} {data["Users"][id]["last name"]} id{id}.'
                except:
                    admins += f'{data["Users"][id]["first name"]} id{id}.'
        print(admins)
        bot.send_message(message.chat.id, f'Вот все *админы* {admins}', parse_mode='Markdown')


@bot.message_handler(commands=['viewteachers'])
def showingteachers(message):
    if data['Users'][str(message.from_user.id)]['status'] == 'admin':
        teachers = ''
        ides = list(data['Users'].keys())
        for id in ides:
            if data['Users'][id]['status'] == 'teacher' and id != ides[-1]:
                try:
                    teachers += f'{data["Users"][id]["first name"]} {data["Users"][id]["last name"]} id{id}, '
                except:
                    teachers += f'{data["Users"][id]["first name"]} id{id}, '

            elif data['Users'][id]['status'] == 'teacher':
                try:
                    teachers += f'{data["Users"][id]["first name"]} {data["Users"][id]["last name"]} id{id}.'
                except:
                    teachers += f'{data["Users"][id]["first name"]} id{id}.'
        print(teachers)
        bot.send_message(message.chat.id, f'Вот все *учителя* {teachers}', parse_mode='Markdown')


@bot.message_handler(commands=['viewstudents'])
def showstudents(message):
    if data['Users'][str(message.from_user.id)]['status'] == 'admin' or data['Users'][str(message.from_user.id)]['status'] == 'teacher':
        students = ''
        ides = list(data['Users'].keys())
        for id in ides:
            if data['Users'][id]['status'] == 'student' and id != ides[-1]:
                try:
                    students += f'{data["Users"][id]["first name"]} {data["Users"][id]["last name"]} id{id}, '
                except:
                    students += f'{data["Users"][id]["first name"]} id{id}, '

            if data['Users'][id]['status'] == 'student':
                try:
                    students += f'{data["Users"][id]["first name"]} {data["Users"][id]["last name"]} id{id}.'
                except:
                    students += f'{data["Users"][id]["first name"]} id{id}.'
        print(students)
        bot.send_message(message.chat.id, f'Вот все *ученики* {students}', parse_mode='Markdown')


@bot.message_handler(commands=['passvote'])
def passing_vote(message):
    try:
        status = data['Users'][str(message.from_user.id)]['status']
        if status == 'student' or status == 'teacher' or status == 'admin':
            all_lessons = list(lessons.keys())
            all_lessons_str = ''
            for lesson in all_lessons:
                lesson = lesson.replace("'", "")
                all_lessons_str += lesson + '  '
            bot.send_message(message.chat.id, f'Вы решили оценить работу учителя.\nПожалуйста, выбирите соответствующий урок из списка всех уроков -->  {all_lessons_str}')
            data['Users'][str(message.from_user.id)]['operations']['choosing_lesson'] = True
    except:
        bot.send_message(str(message.from_user.id), 'У вас отсутствует статус')


@bot.message_handler(content_types=['text'])
def chating(message):
    if data['Users'][str(message.from_user.id)]['operations']['sending_code_to_get_status_teacher']:
        if message.chat.type == 'private':
            t_code = message.text
            if t_code in main_keys_teachers:
                main_keys_teachers.remove(t_code)
                data['Users'][str(message.from_user.id)]['lessons'] = {}
                data['Users'][str(message.from_user.id)]['status'] = 'teacher'
                bot.send_message(message.chat.id, f'Ваш user обновлён -> {data["Users"][str(message.from_user.id)]}')
                data['Users'][str(message.from_user.id)]['operations']['sending_code_to_get_status_teacher'] = False
                write_to_json()

            else:
                bot.send_message(message.chat.id, f'Отправте код ещё раз, не распознан {message.text}.') if random.randint(0, 1) else bot.send_message(message.chat.id, f'Не пон, отправь код ещё раз.')


    if data['Users'][str(message.from_user.id)]['operations']['sending_code_to_get_status_admin']:
        if message.chat.type == 'private':
            a_code = message.text
            if a_code in main_keys_admins:
                main_keys_admins.remove(a_code)
                data['Users'][str(message.from_user.id)]['lessons'] = {}
                data['Users'][str(message.from_user.id)]['status'] = 'admin'
                bot.send_message(message.chat.id, f'Ваш user обновлён -> {data["Users"][str(message.from_user.id)]}')
                data['Users'][str(message.from_user.id)]['operations']['sending_code_to_get_status_admin'] = False
                write_to_json()

            else:
                bot.send_message(message.chat.id, f'Отправте код ещё раз, не распознан {message.text}.') if random.randint(0, 1) else bot.send_message(message.chat.id, f'Не пон, отправь код ещё раз.')


    if data['Users'][str(message.from_user.id)]['operations']["don't know what to do"]:
        bot.send_message(message.chat.id, 'Если вы не знаете, что делать воспользуйтесь этими *командами*, надеюсь они вам помогут', parse_mode='Markdown', reply_markup=create_3_reply_markup('/start', '/help', '/showabilities'))
        data['Users'][str(message.from_user.id)]['operations']["don't know what to do"] = False


    elif data['Users'][str(message.from_user.id)]['operations']['choosing_lesson']:
        if message.chat.type == 'private':
            chosen_lesson = message.text
            all_lessons = list(lessons.keys())
            if chosen_lesson in all_lessons:
                bot.send_message(message.chat.id, f'Вы выбрали {chosen_lesson} для оценивания.')
                data['Users'][str(message.from_user.id)]['lessons']['chosen_lesson'] = chosen_lesson
                data['Users'][str(message.from_user.id)]['lessons'][chosen_lesson] = lessons[chosen_lesson]
                bot.send_message(message.chat.id, f'Введите любой символ для продолжения оценивания.')
                data['Users'][str(message.from_user.id)]['operations']['choosing_lesson'] = False
                data['Users'][str(message.from_user.id)]['operations']['voting_lesson'] = True
                data['Users'][str(message.from_user.id)]['operations']['index_voting'] = True
                write_to_json()
            else:
                bot.send_message(message.chat.id, 'Повторите выбор еще раз') if random.randint(0, 1) else bot.send_message(message.chat.id, 'Введите название урока еще раз')


    elif data['Users'][str(message.from_user.id)]['operations']['voting_lesson']:
        if message.chat.type == 'private':
            chosen_lesson = data['Users'][str(message.from_user.id)]['lessons']['chosen_lesson']
            dict_of_lesson = data['Users'][str(message.from_user.id)]['lessons'][chosen_lesson]

            list_of_tasks = list(dict_of_lesson.keys())

            if data['Users'][str(message.from_user.id)]['operations']['index_voting']:
                cycle_task = len(list_of_tasks) - 1
                data['Users'][str(message.from_user.id)]['lessons']['cycle_task'] = str(cycle_task)
                print(list_of_tasks)
                data['Users'][str(message.from_user.id)]['operations']['index_voting'] = False
            cycle_task = int(data['Users'][str(message.from_user.id)]['lessons']['cycle_task'])


            print(cycle_task)

            if cycle_task >= 0:
                if data['Users'][str(message.from_user.id)]['operations']['index_for_writing_answers']:
                    task = list_of_tasks[cycle_task]
                    answer = message.text
                    if answer.isdigit() and int(answer) >= 0:
                        if int(answer) <= 10:
                            data['Users'][str(message.from_user.id)]['lessons'][chosen_lesson][task] = answer
                            print(task + '  ' + answer)
                            cycle_task -= 1
                            if cycle_task >= 0:

                                data['Users'][str(message.from_user.id)]['lessons']['cycle_task'] = str(cycle_task)
                                task = list_of_tasks[cycle_task]
                                bot.send_message(message.chat.id, task)

                            else:
                                bot.send_message(message.chat.id, 'Да это всё.')
                                data['Users'][str(message.from_user.id)]['operations']['voting_lesson'] = False
                                data['Users'][str(message.from_user.id)]['operations']['index_for_writing_answers'] = False
                                write_to_json()
                    else:
                        bot.send_message(message.chat.id, 'Укажите число от 1 до 10.')

                else:
                    data['Users'][str(message.from_user.id)]['lessons']['cycle_task'] = str(cycle_task)
                    data['Users'][str(message.from_user.id)]['operations']['index_for_writing_answers'] = True
                    task = list_of_tasks[cycle_task]
                    bot.send_message(message.chat.id, task)
                    print(task)

    elif data['Users'][str(message.from_user.id)]['operations']['create_lesson']:
        if message.chat.type == 'private':
            current_lesson = message.text
            lessons[current_lesson] = {
                "Отцените урок от 1 до 10": '',
                "Отцените свое понимание изученного материала от 1 до 10": '',
                "Отцените, насколько понятно учитель объясняет материал от 1 до 10": '',
                "Сколько раз вам хотелось вздремнуть ": ''
            }
            bot.send_message(message.chat.id, f'Отлично, урок  ━━ {current_lesson} создан.')
            data['Users'][str(message.from_user.id)]['operations']['create_lesson'] = False


if __name__ == '__main__':
    load_data()
    bot.polling(none_stop=True)
