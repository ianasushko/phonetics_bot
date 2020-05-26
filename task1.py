from collections import Counter
from common import Task, database, proceeding_input, check_alternative_names, C_PLACE, C_WAY, comments, beautiful_mistakes
from bot import bot

class Task1(Task):
    def run_task(self, answer):
        self.answer = answer
        self.get_place()
    
    def get_place(self):
        self.send_sound(self.answer)
        self.ask_user(f'{self.answer}\nМесто артикуляции: ', C_PLACE.keys())
        bot.register_next_step_handler_by_chat_id(self.chat_id, self.process_place)

    def process_place(self, message):
        raw_place = message.text
        place = proceeding_input(raw_place)
        self.place = place
        if place not in C_PLACE.keys(): 
            if place == 'не знаю' or place == '':
                for k, v in C_PLACE.items():
                    if self.answer in v:
                        bot.send_message(self.chat_id, f'Место артикуляции: {k}')     
            else:
                alt_name = check_alternative_names(place)
                if alt_name is not None:
                    if alt_name.startswith('заднеязычный'):
                        correct_place = database[self.answer][0]
                        if correct_place.startswith('заднеязычный'):
                            self.place = correct_place
                    else:
                        self.place = alt_name
                else:
                    bot.send_message(self.chat_id, comments[17]) 
                    return self.get_place()
        self.get_way()

    def get_way(self):
        self.ask_user('Способ артикуляции: ', C_WAY.keys())
        bot.register_next_step_handler_by_chat_id(self.chat_id, self.process_way)                
    
    def process_way(self, message):
        raw_way = message.text
        way = proceeding_input(raw_way)
        self.way = way
        if way not in C_WAY.keys():
            if way == 'не знаю' or way == '':
                for k, v in C_WAY.items():
                    if self.answer in v:
                        bot.send_message(self.chat_id, f'Способ артикуляции: {k}')
            else:
                alt_name = check_alternative_names(way)
                if alt_name is not None:
                    self.way = alt_name
                else:
                    bot.send_message(self.chat_id, comments[17]) 
                    return self.get_way()
        
        if self.place == 'не знаю' or self.way == 'не знаю' or self.place == '.' or self.way == '.':
            if self.answer not in self.mistakes:
                self.mistakes.append(self.answer)
        else:
            appropriate_sounds = list(C_PLACE[self.place]) + list(C_WAY[self.way])
            count_place_way = Counter(appropriate_sounds)
            if self.answer in count_place_way:
                for key in count_place_way:
                    num_answer = count_place_way[key]
                    if key == self.answer:
                        if num_answer == 2:
                            bot.send_message(self.chat_id, 'Верно!')
                            self.points += 2
                        else:
                            bot.send_message(self.chat_id, 'Неверно!')
                            if self.answer not in self.mistakes:
                                self.mistakes.append(self.answer)
                        break
            else:
                bot.send_message(self.chat_id, 'Неверно!')
                if self.answer not in self.mistakes:
                    self.mistakes.append(self.answer)
                      
        self.done()
        
    def error(self): 
        number_errors = len(self.mistakes)
        if number_errors > 0:
            text = beautiful_mistakes(number_errors) + '\n'
            for m in self.mistakes:
                two_chars = database[m][0:2]
                chars = ', '.join(two_chars)
                text += f'{m} — {chars}\n'
            bot.send_message(self.chat_id, text)
