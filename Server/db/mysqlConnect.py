from calendar import c
from xml.etree.ElementTree import TreeBuilder
import mysql.connector
from Logger import log
from .mysqlconfig import MYSQL_DATABASE
from .mysqlconfig import MYSQL_HOST
from .mysqlconfig import MYSQL_USER
from .mysqlconfig import MYSQL_PASSWORD
from time import time

class MySqlConnector:
    mydb = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )

    def __init__(self):
        self.__initDatabaseIfNeeded()

    def createForecastFactors(self, cursor):
        sql = """INSERT INTO forecastFactor (month, hour, factor, numberOfInputs)
        values (%s, %s, %s, %s);
        """

        for month in range(12):
            for hour in range(24):
                cursor.execute(sql, (month + 1, hour, 1.0, 1))

    def __initDatabaseIfNeeded(self):

        try:
            cursor = self.mydb.cursor()

            cursor.execute(""" CREATE TABLE IF NOT EXISTS readings (
                                            id integer PRIMARY KEY AUTO_INCREMENT,
                                            grid_output real,
                                            battery_charge real,
                                            pv_input real,
                                            battery_state real,
                                            acc_grid_output real,
                                            acc_grid_input real,
                                            timestamp integer
                                        ); """)

            cursor.execute(""" CREATE TABLE IF NOT EXISTS forecasts (
                                            timestamp integer PRIMARY KEY,
                                            forecast real
                                        );""")

            cursor.execute(""" CREATE TABLE IF NOT EXISTS forecastFactor (
                                            id integer PRIMARY KEY AUTO_INCREMENT,
                                            month integer,
                                            hour integer,
                                            factor real,
                                            numberOfInputs integer,
                                            CONSTRAINT UC_Forecast UNIQUE (month, hour)
                                        );""")

            cursor.execute("""CREATE TABLE IF NOT EXISTS deviceStatus (
                                            id integer PRIMARY KEY AUTO_INCREMENT,
                                            identifier text,
                                            state integer,
                                            timestamp integer,
                                            temperature_c real,
                                            temperature_f real,
                                            humidity real,
                                            consumption real
                                        );""")

            cursor.execute("""ALTER TABLE deviceStatus ADD COLUMN IF NOT EXISTS last_change integer;""")

            cursor.execute("""ALTER TABLE deviceStatus ADD COLUMN IF NOT EXISTS forced tinyint;""")

            cursor.close()

            self.mydb.commit()
        except mysql.connector.Error as e:
            log(f"MySQL Error: {e}")
            print(e)

        try:
            self.createForecastFactors(self.mydb.cursor(prepared=True))
            self.mydb.commit()
        except:
            pass

    def insertReading(self, reading, forecasts):
        sql = '''INSERT INTO readings(grid_output, battery_charge, pv_input, battery_state, timestamp, acc_grid_output, acc_grid_input) 
                VALUES(%s, %s, %s, %s, %s, %s, %s) '''

        cursor = self.mydb.cursor(prepared=True)

        cursor.execute(sql, (reading["gridOutput"], reading["batteryCharge"], reading["pvInput"], reading["batteryState"], reading["timestamp"], reading["accGridOutput"], reading["accGridInput"]))

        cursor.close()

        if forecasts is not None:
            for timestamp, forecast in forecasts.items():
                cursor = self.mydb.cursor(prepared=True)
                forecastUpdateSql = "insert into forecasts (timestamp, forecast) values (%s, %s) on duplicate key update forecast=%s;"
                cursor.execute(forecastUpdateSql, (timestamp, forecast, forecast))

                cursor.close()

                if timestamp < time() - 21600 and forecast > 0:
                    cursor = self.mydb.cursor(prepared=True)
                    cursor.execute('''
                        SELECT
                            avg(pv_input)
                        FROM
                            readings
                        WHERE
                            timestamp BETWEEN %s - 3600 AND %s
                        ''',
                        (timestamp, timestamp)
                    )
                    averageInput = cursor.fetchone()[0]
                    cursor.close()
                    if averageInput is not None:
                        cursor = self.mydb.cursor(prepared=True)
                        factorUpdateSQL = '''      
                                            UPDATE
                                                forecastFactor
                                            SET
                                                factor = (factor * numberOfInputs + %s / %s) / (numberOfInputs + 1), numberOfInputs = numberOfInputs + 1
                                                WHERE
                                                    month = DATE_FORMAT(FROM_UNIXTIME(%s), "%m")
                                                    AND hour = DATE_FORMAT(FROM_UNIXTIME(%s), "%H");
                                                    
                                        '''
                        
                        cursor.execute(factorUpdateSQL, (averageInput, forecast, timestamp, timestamp))
                        cursor.close()


        cursor.close()

        self.mydb.commit()

    def getCurrentDeviceStates(self):
        sql = ''' 
        select deviceStatus.* from deviceStatus,
            (select identifier, max(`timestamp`) as `timestamp` from deviceStatus group by identifier) max_states
                where deviceStatus.identifier = max_states.identifier
                and deviceStatus.timestamp = max_states.timestamp;
        '''
        cursor = self.mydb.cursor()
        cursor.execute(sql)

        rows = cursor.fetchall()

        result = []

        for row in rows:
            result.append(
                {
                    "identifier": row[1],
                    "state": row[2],
                    "timestamp": row[3],
                    "temperature_c": row[4],
                    "temperature_f": row[5],
                    "humidity": row[6],
                    "consumption": row[7],
                    "lastChange": row[8],
                    "forced": row[9]
                }
            )

        cursor.close()

        return result

    def getCurrentPVStateMovingAverage(self):
        sql = 'select avg(subtable.grid_output), avg(subtable.battery_charge), avg(subtable.battery_state) from (select * from readings order by `timestamp` desc limit 10) as subtable;'

        cur = self.mydb.cursor()
        cur.execute(sql)

        row = cur.fetchone()

        cur.close()

        return {
                "gridOutput": row[0],
                "batteryCharge": row[1],
                "batteryState": row[2]
            }

    def getCurrentDeviceStatus(self, identifier):
        sql = 'select * from deviceStatus where identifier = %s order by `timestamp` desc limit 1;'

        cursor = self.mydb.cursor()
        cursor.execute(sql, [identifier])

        row = cursor.fetchone()

        if row is None:
            return None

        cursor.close()

        return {
                "identifier": row[1],
                "state": row[2],
                "timestamp": row[3],
                "temperature_c": row[4],
                "temperature_f": row[5],
                "humidity": row[6],
                "consumption": row[7],
                "lastChange": row[8],
                "forced": row[9]
            }

    def saveCurrentDeviceStatus(self, identifier, state=None, temperature_c=None, temperature_f=None, humidity=None, consumption=None, lastChange=None, forced=None):
        sql = 'insert into deviceStatus(identifier, state, timestamp, temperature_c, temperature_f, humidity, consumption, last_change, forced) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)'

        cur = self.mydb.cursor(prepared=True)

        current = self.getCurrentDeviceStatus(identifier)

        toSaveState = state
        if toSaveState is None:
            toSaveState = current['state'] if current is not None else None

        toSaveTemperature_c = temperature_c
        if toSaveTemperature_c is None:
            toSaveTemperature_c = current['temperature_c'] if current is not None else None

        toSaveTemperature_f = temperature_f
        if toSaveTemperature_f is None:
            toSaveTemperature_f = current['temperature_f'] if current is not None else None

        toSaveHumidity = humidity
        if toSaveHumidity is None:
            toSaveHumidity = current['humidity'] if current is not None else None

        toSaveConsumption = consumption
        if toSaveConsumption is None:
            toSaveConsumption = current['consumption'] if current is not None else None

        toSaveLastChange = lastChange
        if toSaveLastChange is None:
            toSaveLastChange = current['lastChange'] if current is not None else None

        toSaveForced = forced
        if toSaveForced is None:
            toSaveForced = current['forced'] if current is not None else None

        cur.execute(
            sql, 
            (
                identifier, 
                toSaveState, 
                int(time()), 
                toSaveTemperature_c, 
                toSaveTemperature_f, 
                toSaveHumidity, 
                toSaveConsumption,
                toSaveLastChange,
                toSaveForced
            )
        )

        cur.close()

        self.mydb.commit()