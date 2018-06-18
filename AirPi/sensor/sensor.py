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
import socket
from RPi import GPIO

try:
    from .lcd import LCD
except Exception: #ImportError
    from lcd import LCD

log = logging.getLogger(__name__)

running = True

def readsensors():
    #--------------CCS811----------------#

    ccs = Adafruit_CCS811()

    while not ccs.available():
        pass
    temp = ccs.calculateTemperature()
    ccs.tempOffset = temp - 25.0

    sensor = Adafruit_DHT.DHT22
    pin = 4


    teller = 0
    teller2 = 0
    co2 = []
    tvoc = []

    GPIO.setup(23, GPIO.OUT)
    GPIO.setup(24, GPIO.OUT)

    pwm = GPIO.PWM(24, 60)
    try:

        while True:
            if ccs.available():
                if not ccs.readData():
                    co2curr = ccs.geteCO2()
                    tvoccurr = ccs.getTVOC()
                    print("CO2: ", co2curr, "ppm, TVOC: ", tvoccurr)
                    if(teller == 3):
                        lcd.stuur_instructie(1)
                    if(teller > 2):
                        co2.append(co2curr)
                        tvoc.append(tvoccurr)
                        if(co2curr < 30000):
                            lcd.stuur_tekst("co2: {0} ppm   tvoc: {1} ppb  ".format(co2curr, tvoccurr))
                            lcd.stuur_instructie(int(0x0 | 0b10000000))

                        if(30000 < co2curr > 2000 or 30000 < tvoccurr > 220):
                            GPIO.output(23, True)
                            GPIO.output(24, False)
                            pwm.stop()
                        else:
                            GPIO.output(23, False)
                            pwm.start(10)

                        if teller == 20:
                            listdata = []
                            listdata.append(statistics.median(co2))
                            listdata.append(statistics.median(tvoc))
                            tom = datetime.datetime.now()
                            for i in range(len(listdata)):
                                save_sensor_value(listdata[i], tom, i + 3)

                            teller = 0
                            co2 = []
                            tvoc = []
                        if teller2 == 150:
                            listdata2 = []
                            humidity, temperature = Adafruit_DHT.read_retry(sensor, 4)
                            if humidity is not None and temperature is not None:
                                pass
                            else:
                                print('Failed to get reading. Try again!')
                            tom = datetime.datetime.now()
                            listdata2.append(temperature - 6)
                            listdata2.append(humidity + 15)
                            for i in range(len(listdata2)):
                                save_sensor_value(listdata2[i], tom, i + 1)
                            teller2 = 0
                    else:
                        pass

                    teller += 1
                    teller2 += 1
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

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8",80))
    ip_address = s.getsockname()[0]
    s.close()
    return ip_address

def loop():
    count = subprocess.check_output("/bin/ps aux | wc -l", shell=True)
    tom = datetime.datetime.now()
    readsensors()
    #print(data)
    #sleep(1000)


#-----------------------------------#


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    try:
        sleep(10)
        ip = get_ip_address()
        lcd = LCD()
        lcd.stuur_instructie(56)  # 8-bit, 2 lines, character font 5x10
        lcd.stuur_instructie(1)  # clear display en cursor home
        lcd.stuur_instructie(12)
        lcd.stuur_tekst("IP-adres: {0}".format(ip))
        sleep(10)
        setup()
        while running:
            loop()
    except KeyboardInterrupt:
        pass


#print("CO2: {0}".format(statistics.median(co2)))
#print("TVOC: {0}".format(statistics.median(tvoc)))
#print("Temperatuur: {0:0.1f}".format(temperature))
#print("Luchtvochtigheid: {0:0.1f}".format(humidity))
