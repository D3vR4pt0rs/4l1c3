import datetime


def check_time():
    opts = {"hey": ('Доброе утро', 'Добрый день', 'Добрый вечер', 'Доброй ночи')}

    now = datetime.datetime.now()
    now += datetime.timedelta(hours=3)
    if 4 < now.hour <= 12:
        greet = opts["hey"][0]
    elif 12 < now.hour <= 16:
        greet = opts["hey"][1]
    elif 16 < now.hour <= 24:
        greet = opts["hey"][2]
    elif 0 <= now.hour <= 4:
        greet = opts["hey"][3]
    return greet
