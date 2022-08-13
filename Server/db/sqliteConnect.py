import sqlite3
from sqlite3 import Error

DATABASE = r"Server/db/data/database.db"

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

        sql__create_readings_table = """ CREATE TABLE IF NOT EXISTS readings (
                                        id integer PRIMARY KEY,
                                        grid_output real,
                                        battery_charge real,
                                        pv_input real,
                                        battery_state real,
                                        timestamp integer
                                    ); """

        createTable(conn, sql__create_readings_table)

        return conn
    except Error as e:
        print(e)

    return conn

def insertReading(reading):
    sql = '''   INSERT INTO readings(grid_output, battery_charge, pv_input, battery_state, timestamp) 
                VALUES(?, ?, ?, ?, ?) '''

    conn = getDatabaseConnection()
    cur = conn.cursor()
    cur.execute(sql, [reading["gridOutput"], reading["batteryCharge"], reading["pvInput"], reading["batteryState"], reading["timestamp"]])
    conn.commit()

    conn.close()
    