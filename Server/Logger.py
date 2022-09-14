from datetime import datetime

def log(message=None):
    current = ''
    with open("logfile.log", 'r+') as logfile:
        current = logfile.read()
        logfile.close()

    with open("logfile.log", "w+") as logfile:
        if message is not None:
            logfile.write(f'{datetime.now()} -- {message}\n{current}')
        else:
            logfile.write(f'\n\n{current}')
        logfile.close()