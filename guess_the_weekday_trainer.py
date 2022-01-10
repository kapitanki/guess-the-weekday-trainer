"Тренер угадывания дней недели по заданной дате"
VERSION = "1.0"

import datetime
import calendar
import random
import re
from pathlib import Path

def generate_dates_and_answers(start_date, end_date, length=10):
    # Высчитываем длительность промежутка в днях
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    
    dates_and_answers = []
    for i in range(length):
        # Генерируется случайную дату
        random_number_of_days = random.randrange(days_between_dates+1)
        random_date = start_date + datetime.timedelta(days=random_number_of_days)
        
        # Наполняется список
        # [Дата, день недели числом, день недели словом, ответ пользователя, правильность ответа]
        dates_and_answers.append([random_date,
                                  random_date.isoweekday(),
                                  random_date.strftime("%A"),
                                  None,
                                  None])
    return dates_and_answers
    
    
def start_game(dates_and_answers):
    """
    Циклически задаются вопросы пользователю и принимаются ответы.
    Возвращается кортеж с списком вопросов и ответов, длительность угадывания в секундах
    """

    print("\nНачалась полная игра")
    start_time = datetime.datetime.now()
    for i in range(len(dates_and_answers)):
        # Обрабатывается ввод пользователя
        try:
            weekday_number_answer = int(input("{} : ".format(
                dates_and_answers[i][0].strftime("%Y.%m.%d"))))
        except ValueError:
            weekday_number_answer = 9
        if weekday_number_answer == 0:
            weekday_number_answer = 7
        dates_and_answers[i][3] = weekday_number_answer
    end_time = datetime.datetime.now()
    session_time_seconds = (end_time - start_time).seconds
    return (dates_and_answers, session_time_seconds)

def check_results(answers):
    for i in answers:
        if i[1] == i[3]:
            i[4] = True
        else:
            i[4] = False
    return answers

def save_to_file(dates_and_answers, session_time_seconds, session_number, correct_answers,
                 game_type, start_date, end_date, mode=None):
    total_answers = len(dates_and_answers)
    single_attempt_average_time = int(session_time_seconds / len(dates_and_answers))
    time_now = datetime.datetime.now()
    dates_and_answers_str = ''
    for i in dates_and_answers:
        dates_and_answers_str += str(i[0]) + " " + str(i[2]) + " " + str(i[4]) + "\n"

    save_data = f"""Тип игры: {game_type}
Попытка №{session_number}
Правильных ответов: {correct_answers}/{total_answers}
Среднее время на одну дату: {single_attempt_average_time} сек
Время суммарно: {session_time_seconds} сек
Дата и время: {time_now:%Y.%m.%d  %H:%M}
Временные рамки: {start_date:%Y}-{end_date:%Y} года
{dates_and_answers_str}

"""
    with open("save_for_guess_weekday_game.txt", mode="a") as file:
        file.write(save_data)
        print("Saved...")
        
def count_correct_answers(dates_and_answers):
    """Вычисляется количество правильных ответов"""
    correct_answers = 0
    for i in dates_and_answers:
        if i[4] == True:
            correct_answers += 1
    return correct_answers


def pick_game():
    print("Главное меню")
    print("1 - полная игра")
    print("2 - тренировка по годам")
    print("3 - тренировка по месяцам и числам")
    print("9 - вспомогательная информация")
    print("0 - статистика")
    try:
        pick = int(input("Выберите игру: "))
    except ValueError as err:
        pick = 1
    if pick == 2:
        return year_game, "Года"
    elif pick == 3:
        return month_game, "Месяцы и числа"
    elif pick == 9:
        show_info(True)
        return pick_game()
    elif pick == 0:
        print("\nВ разработке\n")
        return pick_game()
    else:
        return start_game, "Полная игра"

    
def year_game(dates_and_answers):
    print("\nНачалась тренировка по годам")
    start_time = datetime.datetime.now()
    for i in range(len(dates_and_answers)):
        # Принимаем и обрабатываем ответ пользователя
        try:
            year_day_answer = int(input("{} : ".format(
                dates_and_answers[i][0].strftime("%Y"))))
        except ValueError as err:
            year_day_answer = 9
        if year_day_answer == 0:
            year_day_answer = 7
        dates_and_answers[i][3] = year_day_answer
        # Вычисляем и записываем правильный ответ
        correct_answer = datetime.datetime(dates_and_answers[i][0].year, 3, 14).isoweekday()
        dates_and_answers[i][1] = correct_answer
    end_time = datetime.datetime.now()
    session_time_seconds = (end_time - start_time).seconds
    return (dates_and_answers, session_time_seconds)


def month_game(dates_and_answers):
    print("\nНачалась тренировка по месяцам и числам")
    start_time = datetime.datetime.now()
    for i in range(len(dates_and_answers)):
        if calendar.isleap(dates_and_answers[i][0].year):
            leap_year = "В"
        else:
            leap_year = ""
        year_code = datetime.datetime(dates_and_answers[i][0].year, 3, 14).isoweekday()
        try:
            month_day_answer = int(input("MM.ДД: {}, код года {}, {}: ".format(
                dates_and_answers[i][0].strftime("%m.%d"), year_code, leap_year)))
        except ValueError:
            month_day_answer = 9
        if month_day_answer == 0:
            month_day_answer = 7
        dates_and_answers[i][3] = month_day_answer
        
    end_time = datetime.datetime.now()
    session_time_seconds = (end_time - start_time).seconds
    return (dates_and_answers, session_time_seconds)

def show_results(dates_and_answers, session_time_seconds, correct_answers,
                 session_number, game_type):
    print(f"\nСессия {session_number} по типу игры \"{game_type}\"")
    print("Среднее время на попытку = ", session_time_seconds / len(dates_and_answers))
    print(f"Правильных ответов: {correct_answers}/{len(dates_and_answers)}")
    print()
    for i in dates_and_answers:
        if i[4] == True:
            print(i[0], i[2], "Правильно")
        else:
            print(i[0], i[2], "Ошибка!")


def find_current_session_number(game_type):
    # Создается файл, если файла нет
    fle = Path("save_for_guess_weekday_game.txt")
    fle.touch(exist_ok=True)
    
    pattern = f"{game_type}"
    with open("save_for_guess_weekday_game.txt", mode="r") as file:
        file_content = file.read()
    session_number = len(re.findall(pattern, file_content)) + 1
    return session_number


def show_info(verbose=False):
    if verbose == False:
        print(f"V {VERSION}")
        print("Это игра, в которой нужно угадать день недели по году, месяцу и числу")
        print("Сгенерируются 10 дат")
        print("Ответы принимаются в цифровом виде, где:")
        print("1 - понедельник", "2 - вторник", "3 - среда", "4 - четверг", "5 - пятница",
              "6 - суббота", "7(0) - воскресенье", sep="\n")
        print("Cтатистика автоматически сохраняется в файл \"save_for_date_game.txt\"")
        print()
    else:
        print()
        print("Базовое значение по столетиям:", "1900 - среда", "2000 - вторник",
              "2100 - воскресенье", "2200 - пятница", "Этот паттерн повторяется циклично.",
              sep="\n")
        print()
        print("Даты по каждому месяцу, в которые день такой же, как базовый день года (ММ.ДД):",
              "1.3 (1,4 в высокосный год)", "2.28 (2.29 в высокосный год", "3.14", "4.4", "5.9",
              "6.6", "7.11", "8.8", "9.5", "10.10", "11.7", "12.12", sep="\n")
        print()
        print("Некоторые годы и их базовые значения:", "**0 - 0", "**12 - 1", "**24 - 2",
              "**36 - 3", "**48 - 4", "**60 - 5", "**72 - 6", "**84 - 0", "**96 - 1",
              "**28 - 0", "**56 - 0", sep="\n")
        print()


def play_again_prompt():
    print()
    try:
        int(input("Введите любую цифру, чтобы сыграть еще раз."))
    except ValueError:
        play_again = False
    else:
        play_again = True
    if play_again:
        main()
    
def main():
    # Задается промежуток для генерации даты
    # Начальная дата - дата введения Григорианского календаря в некоторых странах
    show_info()
    start_date = datetime.date(1918, 3, 1)
    end_date = datetime.date(2099, 1, 1)
    # Генерируются даты и ответы
    dates_and_answers = generate_dates_and_answers(start_date, end_date)
    # Пользователю предлагается выбрать игру
    game, game_type = pick_game()
    # Список наполняется ответами пользователя 
    dates_and_answers, session_time_seconds = game(dates_and_answers)
    # Проверяются ответы на правильность
    dates_and_answers = check_results(dates_and_answers)
    # Вычисляется количество правильных результатов
    correct_answers = count_correct_answers(dates_and_answers)
    # Находится номер сессии
    session_number = find_current_session_number(game_type)
    # Сохраняются данные
    save_to_file(dates_and_answers, session_time_seconds, session_number, correct_answers,
                 game_type, start_date, end_date, mode=None)
    # выводятся результаты
    show_results(dates_and_answers, session_time_seconds, correct_answers,
                 session_number, game_type)
    play_again_prompt()

main()
        
