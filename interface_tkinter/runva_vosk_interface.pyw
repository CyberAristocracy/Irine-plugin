# Грфический интерфейс к Irine-Assistant написанный на tkinter
# https://github.com/janvarev/Irene-Voice-Assistant
# https://github.com/Lolipol/Irine-plugin

import datetime
import argparse
import os
import queue
import sounddevice as sd
import vosk
import sys
import traceback
import json
# ------------------
import time
import tkinter as tk
import textwrap as tw
import sys
import threading

from vacore import VACore
mic_blocked = False

def block_mic():
    global mic_blocked
    #print("Blocking microphone...")
    mic_blocked = True
# Уменьшает текст по введенному количеству символов
def parseText(text, max_length):
    text = tw.dedent(text).strip()
    return tw.fill(text, max_length)
# Уменьшает текст Виджета1 под размер Виджета2
def parseTextAtWidth(text, widthWidget1, widthWidget2, indentX=0):
    widthText = widthWidget2 - indentX*2 # каким должен быть размер текста 
    
    if widthWidget1 > widthText:
        char_width = widthWidget1 / len(text)
        print(widthText / char_width)
        print(widthText / char_width * char_width)
        return  parseText(text, widthText / char_width)
    return text


class App(tk.Tk):
    settings = {
        'height':   390,                     # высота окна
        'isTitle':  False,                   # включать втроенный заголовок, отключает созданный
        'textTitle':  'Голосовой ассистент', # текст заголовка
        'locatedWin': 'DR',                  # угол экрана, D - DOWN, U - UP, R - RIGHT, L - LEFT порядок не важен
        'indentX': 10,                       # отступ от ближайшего края дисплея    по X
        'indentY': 45,                       # отступ от ближаейшего  края дисплея  по Y
        'maxCountMessage': 100,              # максимальное количество сохраненных сообщений  
        'isScrollbar': False,                # включает или выключает встроенную прокрутку
        'isShowStartLocatedWin': True,       # начинает с начальной позиции после сворачивания
        'isTopLeave': True,                  # окно всегда поверх остальных окон
     
        'bgTitle': '#3a4047',                # цвет фона собственного заголовка
        'widthTitleButton': 4,               # ширина кнопок заголовка, размер 
        'fgTitleText': '#828d94',            # цвет текста заголовка
        'fontTitle': ('default', 10, 'bold'),# шрифт текста загловка, ('Шрифт', размер, 'normal bold  italic underline')
        'indentTextTitle': 10,               # отступ текста заголовка от левого края
        'textCloseButton': '❌',             # текст кнопки закрытия
        'bgCloseButton': '#3a4047',          # цвет фона кнопки закрытия
        'fgCloseButton': '#828d94',          # цвет текста кнопки закрытия
        'fontCloseButton': ('default', 10, 'bold'), # шрифт текста кнопки закрытия, ('Шрифт', размер, 'normal bold  italic underline')
        'bgEnterClose': '#e81123',           # цвет фона кнопки закрытия при наведении
        'fgEnterClose': 'white',             # цвет текста кнопки закрытия при наведении
        'textMinimizeButton': '_',           # текст кнопки сворачивания
        'bgMinimizeButton': '#3a4047',       # цвет фона кнопки сворачивания
        'fgMinimizeButton': '#828d94',       # цвет текста кнопки сворачивания
        'fontMinimizeButton': ('default', 10, 'bold'), # шрифт текста кнопки сворачивания, ('Шрифт', размер, 'normal bold  italic underline')
        'bgEnterMinimize': '#4c535b',        # цвет фона кнопки сворачивания при наведении
        'fgEnterMinimize': 'white',          # цвет текста кнопки сворачивания при наведении
        
        'bgMainFrame': '#18191d',            # цвет фона пространства сообщений
        'maxLengthMessage': 30,              # максимальное количество символов в строчке сообщения
        'indentXMessegeBox': 16,             # отступ от края экрана к сообщению по горизонтале
        'indentYMessegeBox': 5,              # отступ от края экрана к сообщению по вертикале
        'indentXTextMessege': 10,            # отсуп  от от края блока к тексту сообщения по горизонтале 
        'indentYTextMessege': 5,             # отсуп  от от края блока к тексту сообщения по вертикале 
        'bgMessageBox': '#18191d',           # цвет бокса сообщения, он размером со ширину окна и обычного того же цвета, что фрейм
        'bgRightMessage': '#2a2f33',         # цвет фона сообщения ассистента
        'fgRightMessage': 'white',           # цвет текста сообщения ассистента     
        'bgLeftMessage':'#33393f',           # цвет фона сообщения пользователя
        'fgLeftMessage':'white',             # цвет текста сообщения пользователя
        'fontMessage': ("default", 10),      # шрифт сообщений, ('Шрифт', размер, 'normal bold  italic underline')

        'widthScrollbar': 13,                # ширина прокрутки

        'bgInputFrame': '#282e33',           # цвета фона области ввода
        'textRunButton': 'O',                # текст кнопки запуска микрофона
        'textPauseButton': 'I I',            # текст кнопки паузы микрофона
        'fgEntryInnitFrame':  'white',       # цвет текста поля ввода
        'bgEntryInnitFrame': '#282e33',      # цветфона текста поля ввода
        'bgSelectEntryInnitFrame': '#a33c32',# цвет фона при выделении
        'fontEntryInnitFrame': ("default", 11), #  шрифт поля ввода, ('Шрифт', размер, 'normal bold  italic underline')
        'fgMicroButton': '#808080',          # цвет текста кнопки включения микрофона
        'bgMicroButton': '#282e33',          # цвет фона кнопки включения микрофона
        'fgEnterMicroButton': 'white',       # цвет текста при наведении на кнопку микрофона
        'bgEnterMicroButton': '#282e33',     # цвет фона при наведении на кнопку микрофона
        'fontMicroButton': ('default', 12),  # шрифт кнопки микрофона
        'indentXEntryInnitFrame': 20,        # отступ от края окна до поля ввода
        'indentXTextMicroButton': 10,        # отступ от горизонтальных краев до текста кнопки включения микрофона
        'indentYTextMicroButton': 5,         # отступ от вертикальных краев до текста кнопки включения микрофона

        'textLoading': 'Загрузка...',        # текст загрузки
        'bgLoading': '#3a4047',              # фон загрузки
        'fgLoading': '#828d94',              # цвет текста загрузки
        'fontLoading': ('default', 20),      # шрифт закрузки
        # ------------------
        'isHideAfrerTime': True,             # скрывать после определенного времени
        'timeHide': 10,                      # количество секунд после которого окно сворачивается 
        'timeWaiting': 5,                    # количество секунд ожидания ответа
        'isShowSayAssistantName': True,      # открывает окно после произношения "Ирина" (или любого другого Имени ассистента)
        'isShowCommand': True,               # показывать окно после произношения обычных команд 'Ирина привет' (или любого другого Имени ассистента)
        'isSoundStart': False,                # прогигрывает звук после произношения "Ирина" (или любого другого Имени ассистента)
        'pathSoundStart': os.path.join('media','micro_up.wav'), # путь к звуку прогнориуему после произношения "Ирина" (или любого другого Имени ассистента)
        'isSoundEnd': False,                 # прогигрывает звук после отсуствия ответа произношения "Ирина" (или любого другого Имени ассистента)
        'pathSoundEnd': os.path.join('media','micro_down.wav') # путь к звуку прогнориуему после отсуствия ответа произношения "Ирина" (или любого другого Имени ассистента)

    }

    def __init__(self, rec, core, dump_fn):
        tk.Tk.__init__(self)

        # Необходимые компоненты для выполнения бесконечного цыкла...
        self.rec = rec
        self.core = core
        self.dump_fn = dump_fn
        # Переменная для ввода с клавиатуры...
        self.text_input_keyboard = ''
        self.is_text_input_keyboard = False
        # Переменные для запуска команды "Ирина"
        self.is_start_command = False
        self.start_start_command = -1
        self.time_start_assistant = -1
        self.end_start_command = self.settings['timeHide'] # Время сколько ждет ответа
        if self.settings['isTopLeave']:
            self.attributes('-topmost', 1)
        if self.settings['isTitle']:
            self.title(self.settings['textTitle'])
        else:
            self.overrideredirect(True)
        self.resizable(False, False) # Отключает изменение размера окна

        self.widthDisplay = self.winfo_screenwidth()
        self.heightDisplay = self.winfo_screenheight()

        self.height = self.settings['height']
        self.width =  int(self.height * 96 / 113)
        # Отступ от пуск
        locatedWin = self.settings['locatedWin'].upper()
        self.x = 0
        self.y = 0
        # проверка, что значение из существующих иначе DR
        if locatedWin not in ['DL', 'DR', 'RD', 'LD', 'UL', 'UR', 'LU', 'RU']:
            locatedWin = 'DR'
        if 'D' in locatedWin:
            self.y  = self.heightDisplay - self.height - self.settings['indentY']
        elif 'U'  in locatedWin:
            self.y  = self.settings['indentY']
        if 'R' in locatedWin:
            self.x = self.widthDisplay - self.width - self.settings['indentX']
        elif 'L' in locatedWin:
            self.x = self.settings['indentX']

        self.geometry(f"{self.width}x{self.height}")
        self.geometry(f'+{self.x}+{self.y}')
        # иницилизация заголовка
        if not self.settings['isTitle']:
            titleFrame = TitleFrame(self, bg=self.settings['bgTitle'])
        # иницилизация главного фрейма
        mainFrame = ScrollableFrame(self)
        mainFrame.set_background(self.settings['bgMainFrame'])
        if self.settings['isScrollbar']:
            mainFrame.width_scrollbar = self.settings['widthScrollbar']
            mainFrame.place_scrollbar()

        self.messageList = MessageList(
            mainFrame, 
            self.settings['maxCountMessage'],
            self.settings['maxLengthMessage'],
            self.settings['indentXMessegeBox'],
            self.settings['indentYMessegeBox'],
            self.settings['indentXTextMessege'],
            self.settings['indentYTextMessege'],
            self.settings['bgMessageBox'],
            self.settings['bgRightMessage'],
            self.settings['fgRightMessage'],
            self.settings['bgLeftMessage'],
            self.settings['fgLeftMessage'],
            self.settings['fontMessage']
        )
        # ловля все print
        sys.stdout = TextRedirector(self.messageList, "stdout")
        # иницилизация фрейма для ввода данных
        inputFrame = InputFrame(self, self.create_message, self.print_test, bg=self.settings['bgInputFrame']) 
        # загрузка
        loadFrame = Loading(
            self, text=self.settings['textLoading'], 
            bg=self.settings['bgLoading'], 
            fg=self.settings['fgLoading'], 
            font=self.settings['fontLoading']
        )
        loadFrame.start()
        # До дорисовки выполняет все долгие функции
        self.core.init_with_plugins()
        self.start_start_command = time.time()
        self.after(100, self.main_global)
        loadFrame.stop()
        if not self.settings['isTitle']:
            titleFrame.pack(fill=tk.X, side=tk.TOP)
        mainFrame.pack(fill=tk.BOTH, expand='true')
        inputFrame.pack(fill=tk.X, side=tk.BOTTOM )
        
    def hide(self):
        self.withdraw()

    def show(self):
        # чтобы поднять наверх
        if self.settings['isShowStartLocatedWin']:
            self.geometry(f'+{self.x}+{self.y}')
        self.deiconify()
        if not self.settings['isTopLeave']:
            self.attributes('-topmost', 1)
            self.attributes('-topmost', 0)

    def quit(self):
        self.destroy()

    def print_test(self):
        print('Привет дорогой мир!')

    def create_message(self, text):
        if not text: return
        self.text_input_keyboard = text
        self.is_text_input_keyboard = True
    # Костыль чтобы сделать другой поток
    def main_global(self):
        thread = threading.Thread(target=self.main, daemon=True) # 
        thread.start()
    def main(self):
        global mic_blocked, q
        while  True:
            if self.is_text_input_keyboard:
                mic_blocked = True
                if self.is_start_command:
                    self.messageList.addRight(self.text_input_keyboard)
                    self.core.execute_next(self.text_input_keyboard, None)
                    self.is_start_command = False
                else:
                    self.core.run_input_str(self.text_input_keyboard, block_mic)
                mic_blocked = False
                self.is_text_input_keyboard = False
                self.start_start_command = time.time()
                continue
            data = q.get()
            if self.rec.AcceptWaveform(data):
                recognized_data = self.rec.Result()
                recognized_data = json.loads(recognized_data)
                voice_input_str = recognized_data["text"].strip()

                if voice_input_str.split(' ')[-1] in self.core.voiceAssNames and not self.is_start_command:
                    if self.settings['isShowSayAssistantName']:
                        self.show()
                    if self.settings['isSoundStart']:
                        core.play_wav(self.settings['pathSoundStart'])
                    self.messageList.addRight(voice_input_str)
                    self.is_start_command = True
                    self.time_start_assistant = time.time()
                    self.start_start_command = time.time()
                    continue
                # Если не пустая строка, то выполняет команду
                if self.is_start_command and voice_input_str != '':
                    if self.settings['isShowSayAssistantName']:
                        self.show()
                    block_mic()
                    self.messageList.addRight(voice_input_str)
                    self.core.execute_next(voice_input_str, None)
                    self.is_start_command = False
                    self.start_start_command = time.time()
                    mic_blocked = False
                    continue
                # если время закончилось полсе того как сказал "Ирина"
                # скрывает приложение
                if self.time_start_assistant != -1 and time.time() - self.time_start_assistant > self.settings['timeWaiting']:
                    if self.settings['isSoundEnd']:
                        core.play_wav(self.settings['pathSoundEnd'])
                    print('Закончилось время ожидания ответа')
                    print(f'Ожидание: {time.time() - self.time_start_assistant}')
                    self.time_start_assistant = -1
                    self.is_start_command = False
                    mic_blocked = False
                    

                if time.time() - self.start_start_command > self.end_start_command and self.state() == 'normal':
                    
                    self.is_start_command = False
                    mic_blocked = False
                    if self.settings['isHideAfrerTime']:
                        print('Долго не взаимодействовали')
                        print(f'Ожидание: {time.time() - self.start_start_command}')
                        print('Окно свернуто')
                        self.hide()
                    continue
            # Код из runva_vosk
                if voice_input_str != "" and not mic_blocked and not self.is_start_command:
                    if self.settings['isShowCommand']:
                        self.show()
                    self.start_start_command = time.time()
                    self.core.run_input_str(voice_input_str, block_mic)
                    mic_blocked = False
            else:
                pass
            self.core._update_timers()
            if self.dump_fn is not None:
                self.dump_fn.write(data)

class Loading(tk.Label):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

    def start(self):
        self.place(relheight =1.0, relwidth=1.0)
    def stop(self):
        self.destroy()

# Заглушка для ловли print
class TextRedirector(object):
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag
        self.next_user_text = False

    def write(self, str):
        if str.strip() == '': return
        # Печатать слов пользователя
        if self.next_user_text:
            self.widget.addRight(str)
            self.next_user_text = False
            return    
        # Ловля слов пользователя
        if 'Input:' in str:
            self.next_user_text = True
            return
        elif  'Input (in context):' in str:
            self.next_user_text = True
            return
        elif  'Input (cmd in context):' in str:
            self.next_user_text = True
            return
        elif  'Input (cmd):' in  str:
            self.next_user_text = True
            return
        else:
            self.next_user_text = False
        self.widget.addLeft(str)
        # time.sleep(0.2)
    def flush(self):
        pass


class TitleFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        widthTitleButton = self.master.settings['widthTitleButton']
        self.title = tk.Label(
            self, 
            bg=self['bg'],
            fg=self.master.settings['fgTitleText'],
            text=self.master.settings['textTitle'], 
            font=self.master.settings['fontTitle']
        )
        self.closeButton = HoverButton(
            self,
            text=self.master.settings['textCloseButton'],
            command=self.master.destroy,
            bg=self.master.settings['bgCloseButton'],
            fg=self.master.settings['fgCloseButton'],
            font=self.master.settings['fontCloseButton'],
            activebackground=self.master.settings['bgEnterClose'],
            activeforeground=self.master.settings['fgEnterClose'],
            width=widthTitleButton,
            highlightthickness=0,
            bd=0,
        )

        self.minimizeButton = HoverButton(
            self,
            text=self.master.settings['textMinimizeButton'],
            command=self.master.hide,
            bg=self.master.settings['bgMinimizeButton'],
            fg=self.master.settings['fgMinimizeButton'],
            activebackground=self.master.settings['bgEnterMinimize'],
            activeforeground=self.master.settings['fgEnterMinimize'],
            font=self.master.settings['fontMinimizeButton'],
            width=widthTitleButton,
            highlightthickness=0,
            bd=0,
        )
        
        self.title.pack(side=tk.LEFT, fill=tk.Y, padx=(self.master.settings['indentTextTitle'], 0))
        self.closeButton.pack(side=tk.RIGHT, fill=tk.Y)
        self.minimizeButton.pack(side=tk.RIGHT, fill=tk.Y)

        self.bind('<Button-1>', self.get_pos)
        self.title.bind('<Button-1>', self.get_pos)

    # Движение окна по мыши
    def get_pos(self, event):
        xwin = self.master.winfo_x()
        ywin = self.master.winfo_y()
        startx = event.x_root
        starty = event.y_root

        ywin = ywin - starty
        xwin = xwin - startx

        def move_window(event):
            self.master.geometry('+{0}+{1}'.format(event.x_root + xwin,
                                            event.y_root + ywin))

        startx = event.x_root
        starty = event.y_root
        self.bind('<B1-Motion>', move_window)
        self.title.bind('<B1-Motion>', move_window)
    def get_text_title(self):
        return self.title['text']
    def set_text_title(self, text):
        self.title['text'] = text
# Кнопка изменяющая цвет при наведении 
class HoverButton(tk.Button):
    def __init__(self, master, **kw):
        tk.Button.__init__(self,master=master,**kw)
        self.defaultBackground = self["background"]
        self.defaultForeground = self['foreground']
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self['background'] = self['activebackground']
        self['fg'] = self['activeforeground']

    def on_leave(self, e):
        self['background'] = self.defaultBackground
        self['fg'] = self.defaultForeground

class InputFrame(tk.Frame):
    def __init__(self, container, commandEnter, commandButton, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        self.textRun = self.master.settings['textRunButton']
        self.textPause = self.master.settings['textPauseButton']

        self.commandEnter=commandEnter
        self.commandButton = commandButton
        self.messegeStringVar = tk.StringVar()
        self.messageEntry = tk.Entry(
            self,
            textvariable=self.messegeStringVar,
            fg=self.master.settings['fgEntryInnitFrame'],
            bg=self.master.settings['bgEntryInnitFrame'],
            insertbackground=self.master.settings['fgEntryInnitFrame'],
            selectbackground=self.master.settings['bgSelectEntryInnitFrame'],
            font=self.master.settings['fontEntryInnitFrame'],
            justify=tk.LEFT,
            bd=0,
            highlightthickness=0, 
        )

        self.microButton = HoverButton(
            self,
            text=self.textRun,
            fg=self.master.settings['fgMicroButton'],
            bg=self.master.settings['bgMicroButton'],# 282e33
            activebackground=self.master.settings['bgEnterMicroButton'],
            activeforeground=self.master.settings['fgEnterMicroButton'],
            font=self.master.settings['fontMicroButton'],
            command=self.start_commandButton,
            bd=0,
            highlightthickness=0,
        )  
        self.messageEntry.pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
            padx=self.master.settings['indentXEntryInnitFrame']
        )
        self.microButton.pack(
            side=tk.RIGHT,
            fill=tk.X,
            ipadx=self.master.settings['indentXTextMicroButton'],
            ipady=self.master.settings['indentYTextMicroButton'],
        )
        self.messageEntry.bind('<Return>', self.start_commandEnter)

    def start_commandEnter(self, event):
        text = self.messegeStringVar.get()
        self.commandEnter(text)
        event.widget.delete(0, tk.END)

    def start_commandButton(self):
        self.swap()
        self.commandButton()

    def swap(self):
        if self.microButton['text'] == self.textRun:
            self.microButton['text'] = self.textPause
        else:
            self.microButton['text'] = self.textRun



# Лист сообщений...
class MessageList:
    def __init__(self, root, maxCountMessage, maxLengthMessage, indentXMessegeBox, indentYMessegeBox, indentXTextMessege, indentYTextMessege,  bgMessageBox, bgRight, fgRight, bgLeft, fgLeft, font_message):
        self.messageList = []
        self.root = root
        self.max_count = maxCountMessage
        self.max_length = maxLengthMessage
        self.bgMessageBox = bgMessageBox
        self.bgRight = bgRight
        self.fgRight = fgRight
        self.bgLeft = bgLeft
        self.fgLeft = fgLeft
        self.font = font_message
        self.indentXMessegeBox = indentXMessegeBox
        self.indentYMessegeBox = indentYMessegeBox
        self.indentXTextMessege = indentXTextMessege
        self.indentYTextMessege = indentYTextMessege
        
    def add(self, text, type_message='left'):
        if text.strip() == '': return
        text = parseText(text, self.max_length)
        self.messageList.append(
            tk.Frame(
                self.root.scrollable_frame, 
                bg=self.bgMessageBox, 
                bd=0
            )
        )
        self.messageList[-1].pack(
            pady=self.indentYMessegeBox, 
            padx=self.indentXMessegeBox, 
            fill=tk.X
        )
        if type_message=='right':
            bg = self.bgRight
            fg = self.fgRight
            side = tk.RIGHT
        elif type_message=='left':
            bg = self.bgLeft
            fg = self.fgLeft
            side = tk.LEFT
        message = tk.Label(
            self.messageList[-1],
            text=text,
            bd=0,
            bg=bg,
            fg=fg,
            justify=tk.LEFT,
            font=self.font
        )
        message.pack(
            side=side,
            ipadx=self.indentXTextMessege,
            ipady=self.indentYTextMessege
        )
        self.delite_message()
        self.root.scroll_down()

    def addLeft(self, text):
        self.add(text, 'left')

    def addRight(self, text):
        self.add(text, 'right')

    def delite_message(self):
        if len(self.messageList) > self.max_count:
            self.messageList.pop(0).destroy()



class ScrollableFrame(tk.Frame):
    def __init__(self, container,  *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.width_scrollbar = 0
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, border=0)
        self.scrollable_frame.bind(
            "<Configure>", 
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)

        self.bind('<Enter>', self._bound_to_mousewheel)
        self.bind('<Leave>', self._unbound_to_mousewheel)
        self.canvas.bind('<Configure>', self._frame_width)
        self.scroll_down()

    def _frame_width(self, event):
        canvas_width = event.width
        canvas_height = event.height
        if canvas_width - self.width_scrollbar > self.scrollable_frame.winfo_width():
            self.canvas.itemconfig(self.id, width=canvas_width)
        elif canvas_width - self.width_scrollbar < self.scrollable_frame.winfo_width():
            self.canvas.itemconfig(self.id, width=canvas_width)


    def set_background(self, bg='red'):
        self.canvas.configure(bg=bg)
        self.scrollable_frame.configure(bg=bg)

    def set_width(self, width):
        #self.configure(width=width-10)
        self.canvas.itemconfig(self.id, width=width)

    #! понять как работает эта штука
    def place_scrollbar(self):
        self.scrollbar.place(relx=1, rely=1, relheight=1, width=self.width_scrollbar, anchor="se")

    def _bound_to_mousewheel(self, event):
        if sys.platform == "linux" or sys.platform == "linux2":
            self.canvas.bind_all("<Button-4>", self._on_mousewheel)
            self.canvas.bind_all("<Button-5>", self._on_mousewheel)
        else:
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        if sys.platform == "linux" or sys.platform == "linux2":
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        else:
            self.canvas.unbind_all("<MouseWheel>")

    def scroll_down(self, pos=1):
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(pos)

    def _on_mousewheel(self, event):
        platform = sys.platform
        # Мак не проверялось
        if platform == 'darwin':
            delta = event.delta
        # linux проверка на replit.com
        elif platform == "linux" or platform == "linux2":
            if event.num == 5:
                delta = -1
            else:
                delta = 1
            # windows проверка в win10
        else:
            delta = event.delta // 120

        self.canvas.yview_scroll((-1) * delta, "units")
# ------------------- vosk ------------------
if __name__ == "__main__":
    q = queue.Queue()

    def int_or_str(text):
        """Helper function for argument parsing."""
        try:
            return int(text)
        except ValueError:
            return text

    def callback(indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        if not mic_blocked:
            q.put(bytes(indata))

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        '-l', '--list-devices', action='store_true',
        help='show list of audio devices and exit')
    args, remaining = parser.parse_known_args()
    if args.list_devices:
        print(sd.query_devices())
        parser.exit(0)
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[parser])
    parser.add_argument(
        '-f', '--filename', type=str, metavar='FILENAME',
        help='audio file to store recording to')
    parser.add_argument(
        '-m', '--model', type=str, metavar='MODEL_PATH',
        help='Path to the model')
    parser.add_argument(
        '-d', '--device', type=int_or_str,
        help='input device (numeric ID or substring)')
    parser.add_argument(
        '-r', '--samplerate', type=int, help='sampling rate')
    args = parser.parse_args(remaining)
    #args = {}

    try:
        if args.model is None:
            args.model = "model"
        if not os.path.exists(args.model):
            print ("Please download a model for your language from https://alphacephei.com/vosk/models")
            print ("and unpack as 'model' in the current folder.")
            parser.exit(0)
        if args.samplerate is None:
            device_info = sd.query_devices(args.device, 'input')
            # soundfile expects an int, sounddevice provides a float:
            args.samplerate = int(device_info['default_samplerate'])

        model = vosk.Model(args.model)

        if args.filename:
            dump_fn = open(args.filename, "wb")
        else:
            dump_fn = None


        
        with sd.RawInputStream(samplerate=args.samplerate, blocksize = 8000, device=args.device, dtype='int16',
                               channels=1, callback=callback) as stream:
            

            rec = vosk.KaldiRecognizer(model, args.samplerate)
            core = VACore()
            # чтобы обращаться к плагинам через интерфейс..
            core.interface = App(rec, core, dump_fn)
            core.interface.mainloop()  
                
    except KeyboardInterrupt:
        print('\nDone')
        parser.exit(0)
    except Exception as e:
        parser.exit(type(e).__name__ + ': ' + str(e))


