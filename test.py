import os
import json

# Проверить наличие конфигурационного файла
if os.path.isfile('config.json'):
    print("конфигурационный файл найден")

    # попытаться прочитать файл и вычленить переменные
    print("пытаемся прочитать файл и вычленить переменные")
    with open('config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
        #print("config=", config)

    # проверить содержимое переменных на валидность
    if 'ip' not in config:
        print("ERROR: айпи нет")
        exit(1)
    if 'login' not in config:
        print("ERROR: логина нема")
        exit(1)
    if 'password' in config:
        if len(config["password"]) < 5 :
            print("ERROR: пароль короче 5 символов")
            exit(1)
    else:
        print("ERROR: пароля нема")
        exit(1)

    # попытаться соединиться
    ip = config["ip"]
    l = config["login"]
    p = config["password"]
    print(f'ПОДКЛЮЧЕНИЕ К СЕРВЕРУ (ip: "{ip}" | Login: {l}, Password: *******)')
else:
    print("Файл config.json не найден")
    exit(1)

print('работа программы завершена')
