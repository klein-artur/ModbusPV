from cgitb import reset
import sqlite3
from time import time
from Logger import log
from sqlite3 import Error

DATABASE = r"db/data/database.db"

def runSql(conn, sql):
    try:
        c = conn.cursor()
        c.execute(sql)
    except Error as e:
        log(f"SQLite Error: {e}")
        print(e)

def checkIfColumnExists(conn, table, column):
    sql = f"pragma table_info({table});"

    cursor = conn.cursor()
    columns = map(lambda line: line[1], cursor.execute(sql).fetchall())
    
    return column in columns

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

        createDeviceInfoTable = """ CREATE TABLE IF NOT EXISTS deviceStatus (
                                        id integer PRIMARY KEY AUTOINCREMENT,
                                        identifier text,
                                        state integer,
                                        timestamp integer
                                    )
        """

        runSql(conn, createReadingsTable)
        runSql(conn, createForecastTable)
        runSql(conn, createForecastFactorTable)
        runSql(conn, createDeviceInfoTable)

        if not checkIfColumnExists(conn, "readings", "acc_grid_output"):
            addAccGridOutputSql = "alter table readings add acc_grid_output real not null default(0.0);"
            runSql(conn, addAccGridOutputSql)

        if not checkIfColumnExists(conn, "readings", "acc_grid_input"):
            addAccGridInputSql = "alter table readings add acc_grid_input real not null default(0.0);"
            runSql(conn, addAccGridInputSql)
        
        if not checkIfColumnExists(conn, "deviceStatus", "temperature_c"):
            addAccGridInputSql = "alter table deviceStatus add temperature_c real;"
            runSql(conn, addAccGridInputSql)
        
        if not checkIfColumnExists(conn, "deviceStatus", "temperature_f"):
            addAccGridInputSql = "alter table deviceStatus add temperature_f real;"
            runSql(conn, addAccGridInputSql)
        
        if not checkIfColumnExists(conn, "deviceStatus", "temperature_f"):
            addAccGridInputSql = "alter table deviceStatus add temperature_f real;"
            runSql(conn, addAccGridInputSql)
        
        if not checkIfColumnExists(conn, "deviceStatus", "humidity"):
            addAccGridInputSql = "alter table deviceStatus add humidity real;"
            runSql(conn, addAccGridInputSql)

    except Error as e:
        log(f"SQLite Error: {e}")
        print(e)

    try:
        createForecastFactors(conn)
    except:
        pass

    return conn

def insertReading(reading, forecasts):
    sql = '''   INSERT INTO readings(grid_output, battery_charge, pv_input, battery_state, timestamp, acc_grid_output, acc_grid_input) 
                VALUES(?, ?, ?, ?, ?, ?, ?) '''

    conn = getDatabaseConnection()
    cur = conn.cursor()
    cur.execute(sql, [reading["gridOutput"], reading["batteryCharge"], reading["pvInput"], reading["batteryState"], reading["timestamp"], reading["accGridOutput"], reading["accGridInput"]])

    if forecasts is not None:
        for timestamp, forecast in forecasts.items():
            forecastUpdateSql = "insert or replace into forecasts (timestamp, forecast) values (?, ?);"
            cur.execute(forecastUpdateSql, [timestamp, forecast])

            if timestamp < time() - 21600 and forecast > 0:
                factorUpdateSQL = '''      
                                    UPDATE
                                        forecastFactor
                                    SET
                                        factor = (factor * numberOfInputs + (
                                                SELECT
                                                    avg(pv_input)
                                                FROM
                                                    readings
                                                WHERE
                                                    "timestamp" BETWEEN ? - 3600 AND ?) / ?) / (numberOfInputs + 1), numberOfInputs = numberOfInputs + 1
                                        WHERE
                                            "month" = strftime ("%m", DATETIME (?, "unixepoch"))
                                            AND "hour" = strftime ("%H", DATETIME (?, "unixepoch"));
                                            
                                '''
                
                cur.execute(factorUpdateSQL, [timestamp, timestamp, forecast, timestamp, timestamp])

    conn.commit()

    conn.close()

def getCurrentDeviceStates():
    sql = 'select * from (select * from deviceStatus order by "timestamp" desc) group by identifier;'
    conn = getDatabaseConnection()
    cur = conn.cursor()
    cur.execute(sql)

    rows = cur.fetchall()

    result = []

    for row in rows:
        result.append(
            {
                "identifier": row[1],
                "state": row[2],
                "timestamp": row[3],
                "temperature_c": row[4],
                "temperature_f": row[5],
                "humidity": row[6]
            }
        )

    conn.close()

    return result


def getCurrentPVStateMovingAverage():
    sql = 'select avg(grid_output), avg(battery_charge) from (select * from readings order by "timestamp" desc limit 20)'

    conn = getDatabaseConnection()
    cur = conn.cursor()
    cur.execute(sql)

    row = cur.fetchone()

    conn.close()

    return {
            "gridOutput": row[0],
            "batteryCharge": row[1]
        }


def getCurrentDeviceStatus(identifier):
    sql = 'select * from deviceStatus where identifier == ? order by "timestamp" desc limit 1;'

    conn = getDatabaseConnection()
    cur = conn.cursor()
    cur.execute(sql, [identifier])

    row = cur.fetchone()

    conn.close()

    return {
            "identifier": row[1],
            "state": row[2],
            "timestamp": row[3],
            "temperature_c": row[4],
            "temperature_f": row[5],
            "humidity": row[6]
        }


def saveCurrentDeviceStatus(identifier, state=None, temperature_c=None, temperature_f=None, humidity=None):
    sql = 'insert into deviceStatus(identifier, state, timestamp, temperature_c, temperature_f, humidity) values(?, ?, ?, ?, ?, ?)'

    conn = getDatabaseConnection()

    cur = conn.cursor()
    cur.execute(sql, [identifier, state, int(time()), temperature_c, temperature_f, humidity])

    conn.commit()
    conn.close()