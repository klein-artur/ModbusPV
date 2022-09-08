from datetime import datetime

def log(message=None):
    with open("logfile.log", "a+") as logfile:
        if message is not None:
            logfile.write(f'{datetime.now()} -- {message}\n')
        else:
            logfile.write('\n\n')