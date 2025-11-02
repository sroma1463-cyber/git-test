import os
import json

# Проверить наличие конфигурационного файлы
if os.path.isfile('config.json'):
    print("конфигурационный файл найден")

    # попытаться прочитать файл и вычленить переменные
    print("пытаемся прочитать файл и вычленить переменные")
    with open('config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
        #print("config=", config)

    # проверить содержимое переменных на валидность
    if 'ip' in config:
        print("айпи есть")
    else:
        print("айпи нет")
        exit(1)
    if 'login' in config:
        print("логин есть")
    else:
        print("логина нема")
        exit(1)
    if 'password' in config:
        print("пароль есть")
    else:
        print("пароля нема")
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
