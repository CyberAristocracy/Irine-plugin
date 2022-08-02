# Добавляет и загружает в core модель, расставляющую знаки препинания в тексте (https://github.com/snakers4/silero-models)
# Поддерживаемые языки: ['en', 'de', 'ru', 'es']. Расставляет следующие знаки препинания: '.,-!?—'
# Чтобы воспользоваться в плагине core.te_model.enhance_text(text, 'ru')
# ввернет обработанный текст
# требуется torch 1.10+
# модель весит 90 мб 


modelurl = 'https://models.silero.ai/te_models/v2_4lang_q.pt'

import os
from vacore import VACore
# функция на старте
def start(core:VACore):
    manifest = {
        "name": "Модель, расставляющая знаки препинания в тексте",
        "version": "1.0",
        "require_online": False,

        "default_options": {
        },
    }
    return manifest

def start_with_options(core:VACore, manifest:dict):
    import os 
    import torch
    local_file = 'te_model.pt'

    if not os.path.isfile(local_file):
        print("Downloading Silero model...")
        torch.hub.download_url_to_file(modelurl,
                                       local_file)


    core.te_model = torch.package.PackageImporter(local_file).load_pickle("te_model", "model")
    # core.te_model.enhance_text(text, 'ru')