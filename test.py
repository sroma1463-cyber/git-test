with open('.env') as f: d = dict(l.strip().split('=') for l in f if '=' in l)
print(f"ПОДКЛЮЧЕНИЕ К СЕРВЕРУ Login: {d.get('LOGIN')}, Pass: {d.get('PASSWORD')}")
