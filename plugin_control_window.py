# Проверено: win10, python 3.10
# плагин позволяет взаимодействовать с активным окном
# закрыть окно, свернуть окно, открыть в полноэкранном режиме
#  реализованы комбинации клавиш: alt+tab, alt+shift+tab (для переключения между окнами)
# ctrl+tab (для вкладок), ctrl+shift+tab, ctrl+w (для закрытия вкладок в браузере)

from vacore import VACore

def start(core:VACore):
    manifest = {
        "name": "Работа с активным окном",
        "version": "1.0",
        "require_online": False,

        "commands": {
            "закрыть окно|закрой окно": clsActiveWindow,
            "сверни окно|свернуть окно|свернуть": minActiveWindow,
            "обычное окно|вернуть размер окна|обычная окно|обычный размер": restActiveWindow,
            "окно на полный экран|растянуть окно|полно экранный режим|на полный экран|на полные экран": maxActiveWindow,
            "прошлое окно|предыдущее окно": altTabActiveWindow,
            "последнее активное окно|окно назад|первое активное окно|первое окно|окно далее|следующее окно|следующие окно": shiftAltTabActiveWindow,
            "следующая вкладка|вкладка далее|следующее вкладка": ctrtTabActiveWindow,
            "предыдущая вкладка|вкладка назад": ctrlShiftTabActiveWindow,
            "закрыть вкладку|закрой вкладку": CtrlWActiveWindow
        }
    }
    return manifest

def check_script(param_script):
    try:
        param_script()
    except Exception:
        core.play_voice_assistant_speech("Не могу закрыть")

def clsActiveWindow(core:VACore, phrase:str):
    check_script(closeActiveWindow)
def minActiveWindow(core:VACore, phrase:str):
    check_script(minimizeActiveWindow)
def restActiveWindow(core:VACore, phrase:str):
    check_script(restoreActiveWindow)
def maxActiveWindow(core:VACore, phrase:str):
    check_script(maximizeActiveWindow)
def altTabActiveWindow(core:VACore, phrase:str):
    check_script(pressAltTab)
def shiftAltTabActiveWindow(core:VACore, phrase:str):
    check_script(pressShiftAltTab)
def ctrtTabActiveWindow(core:VACore, phrase:str):
    check_script(pressCtrlTab)
def ctrlShiftTabActiveWindow(core:VACore, phrase:str):
    check_script(pressCtrlShiftTab)
def CtrlWActiveWindow(core:VACore, phrase:str):
    check_script(pressCtrlW)

# -------------плагин----------------  
import platform, ctypes, time

WM_CLOSE = 0x0010
SW_MINIMIZE = 6
SW_RESTORE  = 9
SW_MAXIMIZE = 3
# kayboard 
VK_ALT     = 0x12
VK_TAB     = 0x09
VK_SHIFT   = 0x10
VK_CONTROL = 0x11
KEY_W      = 0x57

def closeActiveWindow():
    # закрывает активное окно
    if platform.system() == "Windows":
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        return ctypes.windll.user32.PostMessageA(hwnd, WM_CLOSE, 0, 0)
    else:
        raise OSError('не поддерживает данную платформу')

def minimizeActiveWindow():
    # сворачивает активное окно
    if platform.system() == "Windows":
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        return ctypes.windll.user32.ShowWindow(hwnd, SW_MINIMIZE)
    else:
        raise OSError('не поддерживает данную платформу')

def restoreActiveWindow():
    # развернуть активное окно
    # после полного экрана
    if platform.system() == "Windows": 
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        return ctypes.windll.user32.ShowWindow(hwnd, SW_RESTORE)
    else:
        raise OSError('не поддерживает данную платформу')

def maximizeActiveWindow():
    # активное окно на весь экра
    if platform.system() == "Windows":
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        return ctypes.windll.user32.ShowWindow(hwnd, SW_MAXIMIZE) 
    else:
        raise OSError('не поддерживает данную платформу')


def pressAltTab():
    if platform.system() == "Windows": 
        ctypes.windll.user32.keybd_event(VK_ALT,  0, 0, 0)  # down Alt
        ctypes.windll.user32.keybd_event(VK_TAB,  0, 0, 0) # down Tab
        ctypes.windll.user32.keybd_event(VK_ALT,  0, 2, 0) # up   Alt
        ctypes.windll.user32.keybd_event(VK_TAB,  0, 2, 0) # up   Tab
    else:
        raise OSError('не поддерживает данную платформу')

def pressShiftAltTab():
    if platform.system() == "Windows": 
        ctypes.windll.user32.keybd_event(VK_ALT,   0, 0, 0) # down Alt
        ctypes.windll.user32.keybd_event(VK_SHIFT, 0, 0, 0) # down Shift
        ctypes.windll.user32.keybd_event(VK_TAB,   0, 0, 0) # down Tab
        ctypes.windll.user32.keybd_event(VK_ALT,   0, 2, 0) # up   Alt
        ctypes.windll.user32.keybd_event(VK_TAB,   0, 2, 0) # up   Tab
        ctypes.windll.user32.keybd_event(VK_SHIFT, 0, 2, 0) # up   Shift
    else:
        raise OSError('не поддерживает данную платформу')

def pressCtrlTab():
    if platform.system() == "Windows": 
        ctypes.windll.user32.keybd_event(VK_CONTROL, 0, 0, 0) # down CONTROL
        ctypes.windll.user32.keybd_event(VK_TAB,     0, 0, 0) # down Tab
        ctypes.windll.user32.keybd_event(VK_TAB,     0, 2, 0) # up   Tab
        ctypes.windll.user32.keybd_event(VK_CONTROL, 0, 2, 0) # up   CONTROL
    else:
        raise OSError('не поддерживает данную платформу')

def pressCtrlShiftTab():
    if platform.system() == "Windows": 
        ctypes.windll.user32.keybd_event(VK_CONTROL, 0, 0, 0) # down CONTROL
        ctypes.windll.user32.keybd_event(VK_SHIFT,   0, 0, 0) # down Shift
        ctypes.windll.user32.keybd_event(VK_TAB,     0, 0, 0) # down Tab
        ctypes.windll.user32.keybd_event(VK_TAB,     0, 2, 0) # up   Tab
        ctypes.windll.user32.keybd_event(VK_CONTROL, 0, 2, 0) # up   CONTROL
        ctypes.windll.user32.keybd_event(VK_SHIFT,   0, 2, 0) # up   Shift
    else:
        raise OSError('не поддерживает данную платформу')

def pressCtrlW():
    if platform.system() == "Windows": 
        ctypes.windll.user32.keybd_event(VK_CONTROL, 0, 0, 0) # down CONTROL
        ctypes.windll.user32.keybd_event(KEY_W,      0, 0, 0) # down w
        ctypes.windll.user32.keybd_event(VK_CONTROL, 0, 2, 0) # up   CONTROL
        ctypes.windll.user32.keybd_event(KEY_W,      0, 2, 0) # up   w
    else:
        raise OSError('не поддерживает данную платформу')


