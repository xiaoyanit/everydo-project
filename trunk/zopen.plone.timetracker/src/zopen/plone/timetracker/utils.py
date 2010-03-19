def parseHour(hours):
    """ 3.14 or 3:30 """
    splitted = hours.split(':')
    if len(splitted) == 1:
        return float(hours)
    elif len(splitted) ==2:
        return float(splitted[0]) + int(splitted[1]) / 60.0
    else:
        raise 'Wrong hour!'

