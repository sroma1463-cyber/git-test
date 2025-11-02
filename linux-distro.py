def get_distro():
    try:
        with open("/etc/os-release", "r") as f:
            lines = f.readlines()

        info = {}
        for line in lines:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                info[key] = value.strip('"')

        return f"{info['NAME']} {info['VERSION_ID']}"
    except FileNotFoundError:
        return "ERROR: Can't describe Linux Distro !"

print(f"Linux Distro is: {get_distro()}")
