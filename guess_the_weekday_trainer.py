"""Тренер угадывания дней недели по заданной дате
Текущие режимы:
1. Полная игра
2. Тренировка \"Только года(1918-2099)\"
3. Тренировка \"Только месяцы и числа\"
4. Тренировка \"Только дни недели 1-7 (без столетий)\"
9. Вспомогательная информация
10. Статистика

Список функций:
generate_dates_and_answers
full_game
check_results
save_to_file
count_correct_answers
pick_a_game
year_game
month_game
show_results
find_current_session_number
show_info
play_again_prompt
main
"""

VERSION = "1.1"

import datetime
import calendar
import random
import re
from pathlib import Path
from dataclasses import dataclass, field

start_date = datetime.date(1918, 3, 1)
end_date = datetime.date(2099, 1, 1)

games_types = {
    1: "Полная игра",
    2: "Тренировка \"Только года(1918-2099)\"",
    3: "Тренировка \"Только месяцы и числа\"",
    4: "Тренировка \"Только дни недели 1-7 (без столетий)\"",
    5: "",
    6: "",
    8: "",
    9: "Вспомогательная информация",
    0: "Статистика",
    99: "Выход",
}

class Date_data:
    def __init__(self, start_time=datetime.datetime(1918,1,1),
                 end_time=datetime.datetime(2099,12,31),
                 century=True,
                 year=True,
                 month_and_date=True,
                 weekdays_quantity=7):
        self.start_time = start_time
        self.end_time = end_time
        self.century = century
        self.year = year
        self.month_and_date = month_and_date
        self.weekdays_quantity = weekdays_quantity

        # generating a date
        days_between_dates = (end_date - start_date).days
        def generate_date():
            random_number_of_days = random.randrange(days_between_dates + 1)
            return start_date + datetime.timedelta(days=random_number_of_days)
        
        # condition for generating only full year(century and year)
        if self.century == True and self.year == True and self.month_and_date == False:
            self.date = datetime.datetime(generate_date().year, 3, 14)
        #condition for genereting pure year(without century)
        elif self.century == False and self.year == True and self.month_and_date == False:
            # making sure we get a value that satisfies possible weekdays restriction
            while True:
                self.date = datetime.datetime(generate_date().year % 100 + 2100, 3, 14)
                if self.date.isoweekday() <= weekdays_quantity:
                    break
        else:
            self.date = generate_date()

        self.weekday = self.date.isoweekday()
        self.weekday_str = self.date.strftime("%A")
        
        
        
    @property
    def user_answer(self):
        return self._user_answer
    @user_answer.setter
    def user_answer(self, answer):
        try:
            self._user_answer = int(answer)
        except ValueError:
            self._user_answer = None
        if answer == 0:
            self._user_answer = 7
        if self.weekday == self._user_answer:
            self.iscorrect = True
        else:
            self.iscorrect = False
        
    
# Переделать таймер так, чтобы время игры сохранялось как атрибут функции, а не передавалось, как отдельное значение.
def timer(func):
    """Декоратор, замеряет время выполнения функции.

Изменяет возвращаемые данные декорированой функции - добавляет измеренное время как дополнительный элемент кортежа.
"""
    def wrapper(*args, **kwargs):
        start_time = datetime.datetime.now()
        dates_and_answers = func(*args, **kwargs)
        end_time = datetime.datetime.now()
        wrapper.time_seconds = (end_time - start_time).seconds
        return dates_and_answers    
    return wrapper
        



def pick_a_game():
    """Пользователь делает выбор"""
    show_info(0)
    try:
        pick = int(input("Выберите игру: "))
    except ValueError:
        pick = 99

    if pick == 1:
        game = full_game
    elif pick == 2:
        game = year_game
    elif pick == 3:
        game = month_game
    elif pick == 4:
        game = partial_years_game
    elif pick == 9:
        show_info(2)
        pick_a_game()
    elif pick == 0:
        print("\nВ разработке\n")
        return pick_a_game()
    elif pick == 99:
        return None, None, None
    game_type = games_types[pick]
    dates_and_answers = game()
    return dates_and_answers, game.time_seconds, game_type

@timer
def full_game(questions=10):
    """
Полная игра
Пользователю выводится полная дата,
в ответе пользователь указывает на какой день недели приходится эта дата
    Возвращается кортеж с списком вопросов и ответов, длительность угадывания в секундах
    """
    print("\nНачалась полная игра")
    dates_and_answers = []
    for i in range(questions):
        question = Date_data()
        question.user_answer = input("{}: ".format(question.date.strftime("%Y.%m.%d")))
        dates_and_answers.append(question)
    return dates_and_answers


@timer
def year_game(questions=10):
    print("\nНачалась тренировка \"Только года(1918-2099)\"")
    dates_and_answers = []
    for i in range(questions):
        question = Date_data(month_and_date=False)
        question.user_answer = input("{}: ".format(question.date.strftime("%Y")))
        dates_and_answers.append(question)
    return dates_and_answers


@timer
def month_game(questions=10):
    print("\nНачалась тренировка \"Только месяцы и числа\"")
    dates_and_answers = []
    for i in range(questions):
        question = Date_data()
        if calendar.isleap(question.date.year):
            leap_year = "B"
        else:
            leap_year = ""
        year_code = datetime.datetime(question.date.year, 3, 14).isoweekday()
        if year_code == 7:
            year_code = 0
        question.user_answer = input("MM.ДД: {}, код года {}, {}: ".format(
            question.date.strftime("%m.%d"), year_code, leap_year))
        dates_and_answers.append(question)
    return dates_and_answers
        

@timer
def partial_years_game(questions=10):
    """"""
    print(f"Началась тренировка {games_types[4]}")
    try:
        weekdays_quantity = int(input("Сколько дней недели включать в тренировку(1-7)? "))
    except ValueError:
        weekdays_quantity = 7
    if weekdays_quantity < 1 or weekdays_quantity > 7:
        weekdays_quantity = 7

    print(f"Дней включено в тренировку: {weekdays_quantity}")
    print("В целях обучения генерируются также годы, день которых не входит в дни для тренировки.")
    print("Для них правильным считается любой ответ(включая пустой) кроме дней входящих в дни для тренировки")

    dates_and_answers = []
    for i in range(questions):
        question = Date_data(century=False, month_and_date=False, weekdays_quantity=weekdays_quantity+1)
        question.user_answer = input("{} : ".format(question.date.strftime("%Y")))
        if question.user_answer is None:
            question.user_answer = weekdays_quantity + 1
        dates_and_answers.append(question)
    return dates_and_answers


def save_to_file(dates_and_answers, session_time_seconds, session_number, correct_answers,
                 game_type, start_date, end_date, mode=None):
    """ Сохраняются данные в файл"""

    total_answers = len(dates_and_answers)
    single_attempt_average_time = int(session_time_seconds / len(dates_and_answers))
    time_now = datetime.datetime.now()
    dates_and_answers_str = ''
    for i in dates_and_answers:
        dates_and_answers_str += str(i.date) + " " + str(i.weekday_str) + " " + str(i.iscorrect) + "\n"

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
        if i.iscorrect:
            correct_answers += 1
    return correct_answers


def show_results(dates_and_answers, session_time_seconds, correct_answers,
                 session_number, game_type):
    print(f"\nСессия {session_number} по типу игры \"{game_type}\"")
    print("Среднее время на попытку = ", session_time_seconds / len(dates_and_answers))
    print(f"Правильных ответов: {correct_answers}/{len(dates_and_answers)}")
    print()
    for i in dates_and_answers:
        print(i.date, i.weekday_str, end=" ")
        if i.iscorrect:
            print("Правильно")
        else:
            print("Ошибка!")
    print()


def find_current_session_number(game_type):
    # Создается файл, если файла нет
    fle = Path("save_for_guess_weekday_game.txt")
    fle.touch(exist_ok=True)

    pattern = f"{game_type}"
    with open("save_for_guess_weekday_game.txt", mode="r") as file:
        file_content = file.read()
    session_number = len(re.findall(pattern, file_content)) + 1
    return session_number


def show_info(info_section=0):
    if info_section == 0:
        print("Главное меню")
        print(f"1 - {games_types[1]}")
        print(f"2 - {games_types[2]}")
        print(f"3 - {games_types[3]}")
        print(f"4 - {games_types[4]}")
        print(f"9 - {games_types[9]}")
        print(f"0 - {games_types[0]}")
    elif info_section == 1:
        print(f"V {VERSION}")
        print("Это игра, в которой нужно угадать день недели по году, месяцу и числу")
        print("Сгенерируются 10 дат")
        print("Ответы принимаются в цифровом виде, где:")
        print("1 - понедельник", "2 - вторник", "3 - среда", "4 - четверг", "5 - пятница",
              "6 - суббота", "7(0) - воскресенье", sep="\n")
        print("Cтатистика автоматически сохраняется в файл \"save_for_date_game.txt\"")
        print()
    elif info_section == 2:
        print()
        print("Базовое значение по столетиям:", "1900 - среда", "2000 - вторник",
              "2100 - воскресенье", "2200 - пятница", "Этот паттерн повторяется циклично.",
              sep="\n")
        print()
        print("Даты по каждому месяцу, в которые день такой же, как базовый день года (ММ.ДД):",
              "1.3 (1,4 в высокосный год)", "2.28 (2.29 в высокосный год", "3.14", "4.4", "5.9",
              "6.6", "7.11", "8.8", "9.5", "10.10", "11.7", "12.12", sep="\n")
        print()
        print("Некоторые годы и их базовые значения:", "0 - 0", "12 - 1", "24 - 2",
              "36 - 3", "48 - 4", "60 - 5", "72 - 6", "84 - 0", "96 - 1",
              "28 - 0", "56 - 0", sep="\n")
        print()


def main():
    dates_and_answers, session_time_seconds, game_type = pick_a_game()
    if game_type is None:
        return

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
    main()


show_info(1)
main()
