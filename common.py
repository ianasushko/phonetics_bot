from random import choice, shuffle
import json
import os

from telebot import types
from bot import bot

dirpath = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(dirpath, 'comments.txt')
with open(path) as file: # открыть в главной ф
    comments = file.readlines()

dirpath = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(dirpath, 'sounds.json')

BIG_DICT = json.load(open(path))

C_PLACE = BIG_DICT['C_PLACE']
C_WAY = BIG_DICT['C_WAY']
C_SOUNDNESS = BIG_DICT['C_SOUNDNESS']
C_EXTRA_ARTICULATION = BIG_DICT['C_EXTRA_ARTICULATION']
RUS_LAT = BIG_DICT['RUS_LAT']
ALL_CONSONANTS = BIG_DICT['ALL_CONSONANTS']
ALT_NAMES = BIG_DICT['ALT_NAMES']

# {'звук':[4 характеристики]}
dicts = [C_PLACE, C_WAY, C_EXTRA_ARTICULATION, C_SOUNDNESS]
database = {}
for d in dicts:
    for char, sounds in d.items():
        for s in sounds:  # (звуки)
            if s not in database:
                database[s] = []
            database[s].append(char)

def check_alternative_names(user_input): #ALT_NAMES={'щелевой':['фрикативный']}
    for char_name, alt_names in ALT_NAMES.items():
        if user_input in alt_names:
            return char_name    
        
def proceeding_input(raw_text):
    corrected = raw_text.lower().replace('ё', 'е').strip()
    return corrected

def printed_signs():
    need_signs = input('Нужны ли Вам обозначения звуков - введите да/нет: ') 
    need_signs = proceeding_input(need_signs)
    while need_signs != 'да' and need_signs != 'нет' and need_signs != '':
        print(''.join(comments[17]))
        need_signs = input()
    if need_signs == 'да':
        shuffle(ALL_CONSONANTS)
        list_of_consonants = ' , '.join(ALL_CONSONANTS)
        print(list_of_consonants)

def beautiful_mistakes(errors):
    if errors == 1:
        shown = 'Вы допустили ' + str(errors) + ' ошибку. Запомните:'
    elif errors > 4:
        shown = 'Вы допустили ' + str(errors) + ' ошибок. Запомните:'
    else:
        shown = 'Вы допустили ' + str(errors) + ' ошибки. Запомните:'
    return shown

def ask_user(chat_id, question, options=None):
    MAX_PER_ROW = 35
    if options is not None:
        # Берет список опций, представляет в ряд
        # каждый ряд MAX_PER_ROW характеристик
        # расстояние между кнопками - 4 символа
        kb_buttons = [ types.KeyboardButton(o) for o in options ]
        markup = types.ReplyKeyboardMarkup()
        row_char_count = 0 #считает длину настоящего ряда в характеристиках
        current_row = [] #  содержит кнопки которые пойдут в настоящий ряд

        for option, btn in zip(options, kb_buttons): # название опции и кнопка
            c = len(option) + (4 if len(current_row) != 0 else 0) # с - длина настоящей опции
                              # (+ пробел перед ней, если не первая в ряду
            if row_char_count + c > MAX_PER_ROW: # если добавляемая опция превысит размер ряда
                if len(current_row) != 0: # ...и она не первая в настоящем ряду
                    markup.row(*current_row) # кладет опции на панель
                    current_row = [btn] # превысившую размер в reset.панели опцию на новый
                    row_char_count = c
                else:
                    markup.row(btn) # положить в собсвтенный ряд
            else:
                current_row.append(btn) # если не привысит, продолжить добавлять
                row_char_count += c
        if len(current_row) != 0: # если что-то осталось в настоящем ряду, добавить 
            markup.row(*current_row)
        bot.send_message(chat_id, question, reply_markup=markup)
    else:
        bot.send_message(chat_id, question)  

class Task:
    def __init__(self, chat_id): # 1 раз
        self.chat_id = chat_id
        self.past_mistakes = []
        self.final_callback_fn = None
        self.reset()

    def reset(self):
        if hasattr(self, 'mistakes'):
            self.past_mistakes += self.mistakes
            print(self.past_mistakes)
        self.used = []
        self.mistakes = []
        self.points = 0
        self.available = []
    
    def ask_user(self, question, options=None):
        if options is not None:
            options = ['не знаю', *options]
        ask_user(self.chat_id, question, options)
    
    def send_sound(self, sound):
        try:
            sound_path = os.path.join(dirpath, 'sounds', sound + '.ogg')
            sound_file = open(sound_path, 'rb')
            bot.send_voice(self.chat_id, sound_file)
        except FileNotFoundError:
            pass

    def put_mark(self, nums):  # 5/5, 10 или 100%
        text = '' # все, что нужно будет послать сообщением
        for n in nums:
            if n == '1':
                m1 = int(self.points / 2) 
                mark1 = str(m1) + '/5'
                text += f'Вы выполнили {mark1} заданий.'
            if n == '2':
                if self.points >= 8:
                    text += f'Поздравляю! Ваша оценка {self.points}'
                else:
                    text += f'Ваша оценка {str(self.points)}. В следующий раз справитесь лучше!'
            if n == '3':
                m3 = self.points * 10
                text += f'Задание выполнено на {str(m3)}%'
        bot.send_message(self.chat_id, text)
    
    def choose_answer(self):
        answer = choice(list(database.keys()))
        while answer in self.used:
            answer = choice(list(database.keys()))
        for k, v in database.items():
          if database[answer][:2] == v[:2]:
            self.used.append(k)
        return answer
    
    def get_answer(self):
        if len(self.past_mistakes) > 0:
            idx = choice(range(len(self.past_mistakes)))
            return self.past_mistakes.pop(idx) # удаляет и возвращает заданию
        else:
            return self.choose_answer()
    
    def continue_task(self):
        if self.count < 5:
            self.run_task(self.get_answer())
            self.count += 1
        else:
            self.done_five_times()

    def run_task_five_times(self, grading_nums):
        self.count = 0
        self.grading_nums = grading_nums
        self.continue_task()
    
    def after_task_run(self, callback_fn):
        self.final_callback_fn = callback_fn

    def done(self):
        self.continue_task()
    
    def done_five_times(self):
        self.error()
        self.put_mark(self.grading_nums)
        self.reset()
        if self.final_callback_fn is not None:
            self.final_callback_fn()
