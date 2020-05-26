from random import choice
from common import Task, proceeding_input, comments, beautiful_mistakes, RUS_LAT, printed_signs
from bot import bot
import traceback
import sys

class Task4(Task):
    def choose_answer(self):
        if len(self.used) >= 7:
            runame = choice(self.used)
        else:
            runame = choice(list(RUS_LAT.keys()))
            while runame in self.used:
                runame = choice(list(RUS_LAT.keys()))
            self.used.append(runame)
        latname = choice(list(RUS_LAT.values()))
        return runame, latname

    def continue_task(self):
        if self.count < 10:
            self.count += 1
            if self.count < 5:
                self.run_first_part(self.get_answer())
            else:
                self.run_second_part(self.get_answer())
        else: 
            self.done_five_times()

    def run_first_part(self, answer):
        self.answer = answer
        self.runame = answer[0] # потому что answer - tuple
        self.ask_latname()

    def ask_latname(self): 
        self.ask_user(f'{self.runame}\nЛатинское название: ', RUS_LAT.values()) 
        bot.register_next_step_handler_by_chat_id(self.chat_id, self.process_latname)

    def process_latname(self, message):
        user_answer_one = message.text
        latname = proceeding_input(user_answer_one)
        if latname not in RUS_LAT.values():
            if latname == 'не знаю' or latname == '.':
                pass
            else:
                bot.send_message(self.chat_id, comments[17])
                return self.ask_latname()
        if latname == 'не знаю' or latname == '.':
            bot.send_message(self.chat_id, f'Правильный ответ: {RUS_LAT[self.runame]}')
            if self.runame not in self.mistakes:
                self.mistakes.append(self.answer)
        elif RUS_LAT[self.runame] == latname:
            bot.send_message(self.chat_id, 'Верно!')
            self.points += 1
        else:
            bot.send_message(self.chat_id, f'Неверно! Правильный ответ: {RUS_LAT[self.runame]}')
            if latname not in self.mistakes:
                self.mistakes.append(self.answer)
        
        self.done()

    def run_second_part(self, answer):
        self.answer = answer
        self.rname, self.lname = answer
        self.match_ru_lat_names()

    def match_ru_lat_names(self):
        self.ask_user(f'Верно ли соотношение: {self.lname} — {self.rname}? ', ['да', 'нет']) 
        bot.register_next_step_handler_by_chat_id(self.chat_id, self.process_answer)

    def process_answer(self, message):
        raw_answer = message.text
        user_answer_two = proceeding_input(raw_answer)
        if user_answer_two == 'не знаю' or user_answer_two == '.':
            if RUS_LAT[self.rname] == self.lname:
                bot.send_message(self.chat_id, 'Это соотношение верно!')
            else:
                bot.send_message(self.chat_id, 'Это соотношение неверно!')
        elif user_answer_two == 'да':
            if RUS_LAT[self.rname] == self.lname:
                bot.send_message(self.chat_id, 'Верно!')
                self.points += 1
            else:
                bot.send_message(self.chat_id, 'Неверно!')
                if self.rname not in self.mistakes:
                    self.mistakes.append(self.answer)
        elif user_answer_two == 'нет':
            if RUS_LAT[self.rname] != self.lname:
                bot.send_message(self.chat_id, 'Верно!')
                self.points += 1
            else:
                bot.send_message(self.chat_id, 'Неверно!')
                if self.rname not in self.mistakes:
                    self.mistakes.append(self.answer)
        else:
            bot.send_message(self.chat_id, comments[17]) 
            return self.match_ru_lat_names()

        self.done()
 
    def error(self):
        number_errors = len(self.mistakes)
        if number_errors > 0:
            text = beautiful_mistakes(number_errors) + '\n'
            for m in self.mistakes:
                text += f'{m} — {RUS_LAT[m]}\n'
            bot.send_message(self.chat_id, text)  

