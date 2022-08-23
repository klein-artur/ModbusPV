import sqlite3
from sqlite3 import Error

DATABASE = r"db/data/database.db"

def createTable(conn, sql):
    try:
        c = conn.cursor()
        c.execute(sql)
    except Error as e:
        print(e)

def createForecastFactors(conn):
    sql = """INSERT INTO forecastFactor (month, hour, factor)
    values (?, ?, ?)
    """

    cursor = conn.cursor()

    for month in range(12):
        for hour in range(24):
            cursor.execute(sql, [month + 1, hour, 1.0])
        

def getDatabaseConnection():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)

        createReadingsTable = """ CREATE TABLE IF NOT EXISTS readings (
                                        id integer PRIMARY KEY,
                                        grid_output real,
                                        battery_charge real,
                                        pv_input real,
                                        battery_state real,
                                        timestamp integer
                                    ); """

        createForecastTable = """ CREATE TABLE IF NOT EXISTS forecasts (
                                        timestamp integer PRIMARY KEY,
                                        forecast real
                                    )"""

        createForecastFactorTable = """ CREATE TABLE IF NOT EXISTS forecastFactor (
                                        id integer PRIMARY KEY AUTOINCREMENT,
                                        month integer,
                                        hour integer,
                                        factor real,
                                        numberOfInputs integer,
                                        UNIQUE(month, hour)
                                    )"""

        createTable(conn, createReadingsTable)
        createTable(conn, createForecastTable)
        createTable(conn, createForecastFactorTable)

    except Error as e:
        print(e)

    try:
        createForecastFactors(conn)
    except:
        pass

    return conn

def insertReading(reading, forecasts):
    sql = '''   INSERT INTO readings(grid_output, battery_charge, pv_input, battery_state, timestamp) 
                VALUES(?, ?, ?, ?, ?) '''

    conn = getDatabaseConnection()
    cur = conn.cursor()
    cur.execute(sql, [reading["gridOutput"], reading["batteryCharge"], reading["pvInput"], reading["batteryState"], reading["timestamp"]])

    if forecasts is not None:
        for timestamp, forecast in forecasts.items():
            forecastUpdateSql = "insert or replace into forecasts (timestamp, forecast) values (?, ?);"
            cur.execute(forecastUpdateSql, [timestamp, forecast])

    updateForecastSql = ''' update forecastFactor set 
                                factor = (factor * numberOfInputs + (
                                    select avg(pv_input) from readings where "timestamp" between (
                                        select "timestamp" from forecasts where "timestamp" between ?-3600 and ?
                                    ) and ? 
                                ) / (
                                    select forecast from forecasts where "timestamp" between ?-3600 and ?
                                ) 
                                ) / (numberOfInputs + 1),
                                numberOfInputs = numberOfInputs + 1
                                where "month" = strftime('%m', DATETIME(?, 'unixepoch')) and "hour" = strftime('%H', DATETIME(?, 'unixepoch'))'''

    cur.execute(updateForecastSql, [reading["timestamp"], reading["timestamp"], reading["timestamp"], reading["timestamp"], reading["timestamp"], reading["timestamp"], reading["timestamp"]])

    conn.commit()

    conn.close()
    