import sqlite3
from sqlite3 import Error

DATABASE = r"db/data/database.db"

def createTable(conn, sql):
    try:
        c = conn.cursor()
        c.execute(sql)
    except Error as e:
        print(e)
        

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

        createTable(conn, createReadingsTable)
        createTable(conn, createForecastTable)

        return conn
    except Error as e:
        print(e)

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

    conn.commit()

    conn.close()
    