def get_api():
    with open('/apikeys.txt', 'r', encoding='utf-8') as file:
        weatherapi, token = file.readline(), file.readline()
    return [weatherapi, token]