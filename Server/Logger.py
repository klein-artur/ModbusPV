from datetime import datetime
import os

logpath = ""

def log(message=None):
    current = ''

    try:
        with open(f"{logpath}logfile.log", 'r+') as logfile:
            current = logfile.read()
            logfile.close()
    except Exception as e:
        print(f"No logfile existent yet or error occured: {e}")

    with open(f"{logpath}logfile.log", "w+") as logfile:
        if message is not None:
            logfile.write(f'{datetime.now()} -- {message}\n{current}')
        else:
            logfile.write(f'\n\n{current}')
        logfile.close()