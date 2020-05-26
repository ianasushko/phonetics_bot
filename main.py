import re
from bot import bot
from common import comments, ask_user
from task1 import Task1
from task2 import Task2
from task3 import Task3
from task4 import Task4

sessions = {}

@bot.middleware_handler(update_types=['message']) # все проходит через обработку сообщений 
def cancel_handler(bot_instance, message): # прерывать выполнение задания
    if message.text == '/cancel':
        chat_id = message.chat.id
        if chat_id in sessions:
            sess = sessions[chat_id] # если такой чат-ид существует
            bot.clear_step_handler_by_chat_id(chat_id) # отменяет
            message.chat.id = -1000 # so that it never gets to other handlers - doesnt ex
            sess.choose_task()

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    if chat_id not in sessions:
        sessions[chat_id] = Session(chat_id)

class Session:
    def __init__(self, chat_id):
        self.tasks = [Task1(chat_id), Task2(chat_id), Task3(chat_id), Task4(chat_id)]
        self.chat_id = chat_id
        bot.send_message(chat_id, ''.join(comments[:5]))
        self.choose_grading_system()
    
    def choose_grading_system(self):
        ask_user(self.chat_id, ''.join(comments[5:10]), ['1', '2', '3'])
        bot.register_next_step_handler_by_chat_id(self.chat_id, self.process_grading_system) # когда приходит сообщение c этим chat_id, вызвать process_grading_system

    def process_grading_system(self, message):
        num = message.text 
        self.nums = re.findall('[123]', num)  #список только цифирка (минус опечатки)
        if len(self.nums) == 0:
            self.choose_grading_system()
        self.choose_task()
    
    def choose_task(self):
        task_numbers = [ str(i+1) for i in range(len(self.tasks)) ]
        ask_user(self.chat_id, ''.join(comments[10:17]), task_numbers)
        bot.register_next_step_handler_by_chat_id(self.chat_id, self.process_task)
    
    def process_task(self, message):
        number_of_task = message.text # номер выбранного задания
        if number_of_task.isdigit() and int(number_of_task) >= 1 and int(number_of_task) <= len(self.tasks): 
            task = self.tasks[int(number_of_task)-1]
            task.run_task_five_times(self.nums)
            task.after_task_run(self.choose_task)
        #   break # здесь файл с ошибками
        else:
            self.choose_task()

if __name__=='__main__':
    bot.polling() # все время проверяет на сообщения 
