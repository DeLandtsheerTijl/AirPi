import Adafruit_DHT
from time import sleep
from Adafruit_CCS811 import Adafruit_CCS811
from datetime import time
import statistics
import datetime
import logging
import signal
import subprocess
from time import sleep
import mysql.connector as mariadb

log = logging.getLogger(__name__)

running = True

def readsensors():
    #--------------CCS811----------------#

    ccs = Adafruit_CCS811()

    while not ccs.available():
        pass
    temp = ccs.calculateTemperature()
    ccs.tempOffset = temp - 25.0

    teller = 0
    co2 = []
    tvoc = []

    try:
        while (teller < 150):
            if ccs.available():

                if not ccs.readData():
                    print("CO2: ", ccs.geteCO2(), "ppm, TVOC: ", ccs.getTVOC())
                    if(teller > 2):
                        co2.append(ccs.geteCO2())
                        tvoc.append(ccs.getTVOC())
                    else:
                        pass
                    teller += 1
                else:
                    print("ERROR! {0}".format(time()))
                    while (1):
                        pass
            sleep(2)
    except IOError as e:
        "I/O error({0}): {1}".format(e.errno, e.strerror)
        co2.append(1000)
        tvoc.append(1000)

    #-----------------------------------#

    #--------------DHT22----------------#

    sensor = Adafruit_DHT.DHT22
    pin = 4
    humidity, temperature = Adafruit_DHT.read_retry(sensor, 4)


    if humidity is not None and temperature is not None:
        pass
    else:
        print('Failed to get reading. Try again!')

    return [temperature, humidity, statistics.median(co2), statistics.median(tvoc)]

    #-----------------------------------#

#------------savesensor_todb--------#
def save_sensor_value(data, timeofmeasurement, sensorid):
    try:
        conn = mariadb.connect(database='dbairpi', user='airpi-sensor', password='CBy7rXGmB9.')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tbldata (sensordata, timeofmeasurement, sensorid) VALUES (%s, %s, %s)", (data, timeofmeasurement, sensorid))
        conn.commit()
        log.debug("Saved sensor {}={} to database".format(data, timeofmeasurement, sensorid))
        return True
    except Exception as e:
        log.exception("DB update failed: {!s}".format(e))

#-----------------------------------#

#---------------setup---------------#

def setup():
    def shutdown(*args):
        global running
        running = False
        # try:
        #     sys.exit(0)
        # except KeyError as ex:
        #     pass

    signal.signal(signal.SIGTERM, shutdown)

#-----------------------------------#

#-------------loop------------------#

def loop():
    count = subprocess.check_output("/bin/ps aux | wc -l", shell=True)
    tom = datetime.datetime.now()
    data = readsensors()
    #print(data)
    #sleep(1000)
    for i in range(len(data)):
        save_sensor_value(data[i], tom, i+1)


#-----------------------------------#


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    try:
        setup()
        while running:
            loop()
    except KeyboardInterrupt:
        pass


#print("CO2: {0}".format(statistics.median(co2)))
#print("TVOC: {0}".format(statistics.median(tvoc)))
#print("Temperatuur: {0:0.1f}".format(temperature))
#print("Luchtvochtigheid: {0:0.1f}".format(humidity))
