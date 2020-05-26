from random import choice
from task2 import Task2
from common import database, proceeding_input, comments, beautiful_mistakes
from bot import bot

class Task3(Task2):
    def run_task(self, answer):
        self.answer = answer
        self.is_running_first_part = True 
        super(Task3, self).run_task(answer) # получает Parent Task для Task3
    
    def done(self):
        if self.is_running_first_part:
            self.is_running_first_part = False
            self.ask_modified()
        else:
            super(Task3, self).done()

    def ask_modified(self): # получить "новую" характеристику
        while True:
            lists_of_characteristics = list(database.values())
            ls_change = choice(lists_of_characteristics)  # список характеристик
            char_to_change = choice(ls_change)
            num = ls_change.index(char_to_change)  # индекс элемента - понимаем: место, способ или тп
            for small_ls in lists_of_characteristics:
                for h in small_ls:  # по характеристикам
                    elem = small_ls[num]
                    if elem not in self.available:
                        self.available.append(
                            elem)  #это на что можно поменять char_to_change
            new_char = choice(self.available)  #выбрали на что меняем
            self.answer_chars = database[self.answer].copy()
            self.answer_chars[num] = new_char  # список значений измененного звука

            if self.answer_chars in database.values() and database[self.answer][num] != new_char:
                break
                
        self.ask_user(f'{", ".join(self.answer_chars)}\nЭто звук: ', database.keys())
        bot.register_next_step_handler_by_chat_id(self.chat_id, self.process_user_answer_two)

    def process_user_answer_two(self, message):
        raw_answer_two = message.text   
        user_answer_two = proceeding_input(raw_answer_two)
        self.answer_two = user_answer_two
        klist = list(database.keys())
        vlist = list(database.values())
        correct_sound = klist[vlist.index(self.answer_chars)]
        if user_answer_two not in database.keys():
            if user_answer_two == 'не знаю' or user_answer_two == '.':
                pass
            else:
                bot.send_message(self.chat_id, comments[17]) 
                return self.ask_modified()
        if user_answer_two == correct_sound:  # ключу который соответствует значению answer_chars
            self.send_sound(self.answer)
            bot.send_message(self.chat_id, 'Верно!')
            self.points += 2
        else:
            bot.send_message(self.chat_id, f'Правильный ответ: {correct_sound}' )
            if correct_sound not in self.mistakes:
                self.mistakes.append(correct_sound) 
        
        if self.count == 5:
            self.points //= 2 # вызывается таск2, там баллы +2 -> здесь мне это не подходит
        self.done()
