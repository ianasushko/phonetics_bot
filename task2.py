from common import Task, database, proceeding_input, comments, beautiful_mistakes
from bot import bot

class Task2(Task):
    def run_task(self, answer):
        self.answer = answer
        self.get_user_answer()

    def get_user_answer(self):
        chars = ', '.join(database[self.answer])
        self.ask_user(f'{chars}\nЭто: ', database.keys())
        bot.register_next_step_handler_by_chat_id(self.chat_id, self.process_user_answer)

    def process_user_answer(self, message): 
        raw_user_answer = message.text   
        user_answer = proceeding_input(raw_user_answer)
        if user_answer not in database.keys() and user_answer != 'не знаю' and user_answer != '.':
            bot.send_message(self.chat_id, comments[17]) 
            return self.get_user_answer()
        if user_answer == self.answer:
            self.send_sound(self.answer)
            bot.send_message(self.chat_id, 'Верно!')
            self.points += 2
        else:
            bot.send_message(self.chat_id, f'Правильный ответ: {self.answer}' )
            if self.answer not in self.mistakes:
                self.mistakes.append(self.answer)

        self.done()

    def error(self):
        number_errors = len(self.mistakes)
        points = 10 - 2 * number_errors
        if number_errors > 0:
            text = beautiful_mistakes(number_errors) + '\n'
            for m in self.mistakes:
                for k, v in database.items():
                    if k == m:
                        text += f'{k} — {", ".join(v)}\n' 
            bot.send_message(self.chat_id, text)
