"""Тренер угадывания дней недели по сгенерированной дате"""

import datetime
import calendar
import random
import re
from pathlib import Path
from functools import cached_property


VERSION = "1.2"

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


class DateData:
    def __init__(self, start_date=datetime.date(1918, 3, 1),
                 end_date=datetime.date(2099, 12, 31),
                 generate_century=True,
                 generate_year=True,
                 generate_month_and_date=True,
                 weekdays_quantity=7):
        self.start_date = start_date
        self.end_date = end_date
        self.generate_century = generate_century
        self.generate_year = generate_year
        self.generate_month_and_date = generate_month_and_date
        self.weekdays_quantity = weekdays_quantity
        self.is_correct = None
        self._user_answer = None

        days_between_dates = (end_date - start_date).days

        def generate_date():
            """Generate a date"""
            random_number_of_days = random.randrange(days_between_dates + 1)
            return start_date + datetime.timedelta(days=random_number_of_days)

        # condition for generating only full year(century and year)
        if self.generate_century == True and self.generate_year == True and self.generate_month_and_date == False:
            self.date = datetime.date(generate_date().year, 3, 14)

        # condition for genereting pure year(without century)
        elif self.generate_century == False and self.generate_year == True and self.generate_month_and_date == False:
            # making sure we get a value that satisfies possible weekdays restriction
            while True:
                self.date = datetime.date(generate_date().year % 100 + 2100, 3, 14)
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
    def user_answer(self, value):
        try:
            self._user_answer = int(value)
        except ValueError:
            self._user_answer = None
        if value == 0:
            self._user_answer = 7
        if self.weekday == self._user_answer:
            self.is_correct = True
        else:
            self.is_correct = False


class SessionData:
    def __init__(self, dates, game_type, time_milliseconds):
        self.dates = dates
        self.start_date = dates[0].start_date
        self.end_date = dates[0].end_date
        self.total_answers = len(dates)
        self.time_milliseconds = time_milliseconds
        self.game_type = game_type
        self.single_attempt_average_time = self.time_milliseconds / self.total_answers

    @cached_property
    def session_number(self):
        # Создается файл, если файла нет
        fle = Path("save_for_guess_weekday_game.txt")
        fle.touch(exist_ok=True)

        pattern = re.escape(f"{self.game_type}")
        with open("save_for_guess_weekday_game.txt", mode="r", encoding='utf-8') as file:
            file_content = file.read()
        return len(re.findall(pattern, file_content)) + 1

    @cached_property
    def correct_answers(self):
        """Вычисляется количество правильных ответов"""
        correct_answers = 0
        for i in self.dates:
            if i.is_correct:
                correct_answers += 1
        return correct_answers

def timer(func):
    """Декоратор, замеряет время выполнения функции."""

    def wrapper(*args, **kwargs):
        start_time = datetime.datetime.now()
        dates_and_answers = func(*args, **kwargs)
        end_time = datetime.datetime.now()
        wrapper.time_milliseconds = ((end_time - start_time)
                                     / datetime.timedelta(milliseconds=1))
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
        return pick_a_game()
    elif pick == 0:
        print("\nВ разработке\n")
        return pick_a_game()
    elif pick == 99:
        return None

    session = SessionData(game(), games_types[pick], game.time_milliseconds)
    return session


@timer
def full_game(questions=10):
    """
Полная игра
Пользователю выводится полная дата,
в ответе пользователь указывает на какой день недели приходится эта дата
    Возвращается кортеж с списком вопросов и ответов, длительность угадывания в секундах
    """
    print(f"\nНачалась {games_types[1]}")
    dates_and_answers = []
    for i in range(questions):
        question = DateData()
        question.user_answer = input("{}: ".format(question.date.strftime("%Y.%m.%d")))
        dates_and_answers.append(question)
    return dates_and_answers


@timer
def year_game(questions=10):
    print(f"\nНачалась \"{games_types[2]}\"")
    dates_and_answers = []
    for i in range(questions):
        question = DateData(generate_month_and_date=False)
        question.user_answer = input("{}: ".format(question.date.strftime("%Y")))
        dates_and_answers.append(question)
    return dates_and_answers


@timer
def month_game(questions=10):
    print(games_types[3])
    print(f"\nНачалась \"{games_types[3]}\"")
    dates_and_answers = []
    for i in range(questions):
        question = DateData()
        if calendar.isleap(question.date.year):
            leap_year = "B"
        else:
            leap_year = ""
        year_code = datetime.date(question.date.year, 3, 14).isoweekday()
        if year_code == 7:
            year_code = 0
        question.user_answer = input("MM.ДД: {}, код года {}, {}: ".format(
            question.date.strftime("%m.%d"), year_code, leap_year))
        dates_and_answers.append(question)
    return dates_and_answers


@timer
def partial_years_game(questions=10):
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
        question = DateData(generate_century=False, generate_month_and_date=False, weekdays_quantity=weekdays_quantity + 1)
        question.user_answer = input("{} : ".format(question.date.strftime("%Y")))
        if question.user_answer is None or question.user_answer > weekdays_quantity:
            question.user_answer = weekdays_quantity + 1
        dates_and_answers.append(question)
    return dates_and_answers


def show_results(session):
    print(f"\nСессия {session.session_number} по типу игры \"{session.game_type}\"")
    print("Среднее время на попытку = ", f"{(session.time_milliseconds / len(session.dates)) / 1000:.2f}")
    print(f"Правильных ответов: {session.correct_answers}/{len(session.dates)}")
    print()
    for i in session.dates:
        print(i.date, i.weekday_str, end=" ")
        if i.is_correct:
            print("Правильно")
        else:
            print("Ошибка!")
    print()


def save_to_file(session):
    """ Сохраняются данные в файл"""
    single_attempt_average_time = session.time_milliseconds / session.total_answers
    time_now = datetime.datetime.now()
    dates_str = ''
    for i in session.dates:
        dates_str += str(i.date) + " " + str(i.weekday_str) + " " + str(i.is_correct) + "\n"

    save_data = f"""Тип игры: {session.game_type}
Попытка №{session.session_number}
Правильных ответов: {session.correct_answers}/{session.total_answers}
Среднее время на одну дату: {single_attempt_average_time / 1000:.2f} сек
Время суммарно: {session.time_milliseconds / 1000:.2f} сек
Дата и время: {time_now:%Y.%m.%d  %H:%M}
Временные рамки: {session.start_date:%Y}-{session.end_date:%Y} года
{dates_str}

"""
    with open("save_for_guess_weekday_game.txt", mode="a", encoding='utf-8') as file:
        file.write(save_data)
        print("Saved...")


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
        print("Статистика автоматически сохраняется в файл \"save_for_date_game.txt\"")
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
    session = pick_a_game()
    if session is None:
        return
    save_to_file(session)
    show_results(session)
    main()


show_info(1)
main()
