from datetime import datetime

logpath = "."

def log(message=None):
    current = ''

    try:
        with open(f"{logpath}/logfile.log", 'r+') as logfile:
            current = logfile.read()
            logfile.close()
    except:
        print("No logfile existent yet.")

    with open(f"{logpath}/logfile.log", "w+") as logfile:
        if message is not None:
            logfile.write(f'{datetime.now()} -- {message}\n{current}')
        else:
            logfile.write(f'\n\n{current}')
        logfile.close()