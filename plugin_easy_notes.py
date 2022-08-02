# Простое приложение заметок
# Файлы по умолчанию хранятся в папке temp 
# Формат хранение: JSON
# если есть te_models раставляет знаки препинания

from vacore import VACore
import os, json

def start(core:VACore):
    manifest = { 
        "name": "Простая версия заметок", 
        "version": "1.0",                 
        "require_online": False,          

        "commands": { 
            "заметка|заметку|заметку|заметки": start_note,
            "найти заметку":say_find_note, 
            "удалить заметку": say_remove_one_note, 
            "удалить все заметки": ask_remove_all_note,
            'создать заметку': say_create_note, 
            'узнать количество заметок|количество заметок': count_notes,
            'перебрать заметки|перебор заметок': through_notes,
            'последняя заметка': (through_notes, 'past'),
        },
        "default_options": {
            "path": os.path.join('temp', 'notes.json')
        },
    }
    return manifest

path = os.path.join('temp', 'notes.json')
notes = {}
name = ''
text = ''

# Путь где хранится json-файл заметок
def start_with_options(core:VACore, manifest:dict):
    global path
    path = manifest["options"]['path']

# функция замены знаков препинания
def replace_text(core, text):
    if hasattr(core, 'te_model'):
        return core.te_model.enhance_text(text, 'ru')
    else:
        sim_dict = {
            'что ': ', что ',
            'котор': ', котор',
            ' а ': ', а ',
            'но ': ', но ',
        }
        for kay, sim in sim_dict.items():
            text = text.replace(kay, sim)
            text = text.replace(' ' + kay, sim)
        return text


# открытие json
def open_notes(path):
    if not os.path.isfile(path):
        write_notes(path, {'.': "."})
    with open(path, 'r+', encoding='utf-8') as f:
        notes = json.load(f)
    return notes

# запись json
def write_notes(path, notes):
    with open(path, 'w+', encoding='utf-8') as f:
        json.dump(notes, f)

# начало
def start_note(core:VACore, phrase: str):
    global notes, path
    notes = open_notes(path)
    core.play_voice_assistant_speech('Вы хотите найти, удалить, перебрать, создать заметку или узнать количество заметок?')
    core.context_set(menu_main)

# отмена
def cannel(core:VACore, phrase: str):
    if phrase in ["отмена", 'выход', 'ввыйте']:
        core.play_voice_assistant_speech('отмена')
        return True
    return False

# Найти заметку
def say_find_note(core:VACore, phrase: str):
    global notes, path
    if not notes: notes = open_notes(path)
    core.play_voice_assistant_speech('Скажите название заметки')
    core.context_set(find_note)

def find_note(core:VACore, phrase: str, param=None):
    global notes, path
    if cannel(core, phrase): return 0
    name = phrase.strip()
    if param: name = param
    if name in notes:
        core.play_voice_assistant_speech('Читаю заметку')
        print(notes[name])
        core.play_voice_assistant_speech(notes[name])
    else:
        core.play_voice_assistant_speech('Заметка не найдена')
    core.play_voice_assistant_speech('Продолжить поиск?')
    core.context_set(create_yes_not_menu(say_find_note)) 



# Создание заметки
def say_create_note(core:VACore, phrase: str):
    global notes, path
    if not notes: notes = open_notes(path)
    core.play_voice_assistant_speech('Скажите название заметки')
    core.context_set(create_name)

def create_name(core:VACore, phrase: str):
    if cannel(core, phrase): return 0 
    global name
    name = phrase.strip()
    core.play_voice_assistant_speech('Скажите текст заметки. Слово стоп остановит запись.')
    core.context_set(create_note, duration=60)

def create_note(core:VACore, phrase: str):
    global text
    if cannel(core, phrase): 
        text = ''
        return 0
    if phrase in ['стоп', 'конец']:
        global notes, path, name
        notes[name] = replace_text(core, text)
        text = ''
        write_notes(path, notes)
        core.play_voice_assistant_speech('Заметка создана')
    else:
        text += phrase.strip() + ' '
        core.context_set(create_note, duration=60)



# заглушка
def note_not(core:VACore, phrase: str):
    core.play_voice_assistant_speech('нет так нет')

# Удаление заметки
def say_remove_note(core:VACore, phrase: str):
    global notes, path
    if not notes: notes = open_notes(path)
    core.play_voice_assistant_speech('Удалить одну заметку?')
    core.context_set(remove_menu)

def say_remove_one_note(core:VACore, phrase: str):
    core.play_voice_assistant_speech('Скажите имя заметки')
    core.context_set(remove_one_note)

def remove_one_note(core:VACore, phrase: str, param=None): 
    if cannel(core, phrase): return 0 
    global notes, path
    if not notes: notes = open_notes(path)
    name = phrase.strip()
    if param: name = param
    if name in notes:
        del notes[name]
        write_notes(path, notes)
        core.play_voice_assistant_speech('Удалено')
    else:
        core.play_voice_assistant_speech('Заметка не найдена')
    core.play_voice_assistant_speech('Продолжить удаление?')
    core.context_set(create_yes_not_menu(say_remove_one_note)) 

def ask_remove_all_note(core:VACore, phrase: str):
    core.play_voice_assistant_speech('Уверены что хотите удалить все заметки?')
    core.context_set(remove_all_menu)

def remove_all_note(core:VACore, phrase: str):
    if cannel(core, phrase): return 0 
    global notes, path
    if not notes: notes = open_notes(path)
    notes = {'.': "."}
    write_notes(path, notes)
    core.play_voice_assistant_speech('Удалено')


# Подсчет
def count_notes(core:VACore, phrase: str):
    from utils.num_to_text_ru import num2text
    if cannel(core, phrase): return 0 
    global notes
    if not notes: notes = open_notes(path)
    core.play_voice_assistant_speech('У вас ' + num2text(len(notes) - 1) + ' заметок')

# Перебрать заметки
# Прошлая, следующая, читать, удалить, отмена
def say_through_notes(core:VACore, phrase: str): 
    core.play_voice_assistant_speech('Скажите далее, назад, читать, удалить или отмена')
    through_notes(core, '')

id_through = 1
keys_notes = []
def through_notes(core:VACore, phrase: str, param=0):
    if cannel(core, phrase): return 0 
    global notes, keys_notes, id_through
    if not notes: notes = open_notes(path)
    keys_notes = list(notes.keys())
    if len(keys_notes) == 1: return core.play_voice_assistant_speech('Нет заметок')
    len_kays = len(keys_notes) - 1
    if param == 'past':
        id_through = len_kays
    else:
        id_through = id_through + param
    if id_through == -1 or id_through == 0: id_through = len_kays
    if id_through > len_kays: id_through = 1
    name = keys_notes[id_through]
    print(name)
    core.play_voice_assistant_speech(name)
    core.play_voice_assistant_speech('что дальше?')
    core.context_set(through_menu)

def say_note(core:VACore, phrase: str):
    global notes, path, id_through, kays
    name = keys_notes[id_through]
    if name in notes:
        core.play_voice_assistant_speech('Читаю заметку')
        print(notes[name])
        core.play_voice_assistant_speech(notes[name])
    else:
        core.play_voice_assistant_speech('Заметка не найдена')
    core.play_voice_assistant_speech('что дальше?')
    core.context_set(through_menu)

def delite_note(core:VACore, name=None): 
    global notes, path, id_through, kays
    name = keys_notes[id_through]
    if name in notes:
        del notes[name]
        write_notes(path, notes)
        core.play_voice_assistant_speech('Удалено')
    else:
        core.play_voice_assistant_speech('Заметка не найдена')
    core.play_voice_assistant_speech('что дальше?')
    core.context_set(through_menu)



# Меню
menu_main =       {"найти|найти заметку": say_find_note, "удалить|удалить заметку": say_remove_note, 'создать|создать заметку': say_create_note, 
                   'узнать количество|количество': count_notes, 'отмена': note_not, 'перебрать заметки|перебор заметок|перебать': say_through_notes}
remove_menu =     {"да|ага|одну": say_remove_one_note,"нет|не|не надо|не одну": ask_remove_all_note, 'отмена': note_not}
remove_all_menu = {"да|ага|удалить|удали": remove_all_note,"нет|не|не надо": note_not}
def create_yes_not_menu(fun1, fun2=note_not):
    return {"да|ага|удалить|удали": fun1 , "нет|не|не надо": fun2}

through_menu = {'следующая|далее': (through_notes, 1), 'прошлая|назад|предыдущая': (through_notes, -1), 'читать': say_note, 'удалить': delite_note, 'отмена|конец': note_not}
