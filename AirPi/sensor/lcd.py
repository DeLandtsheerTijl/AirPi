from time import sleep
from RPi import GPIO

lcd_rs = 21
lcd_en = 12
lcd_d0 = 17
lcd_d1 = 27
lcd_d2 = 22
lcd_d3 = 5
lcd_d4 = 6
lcd_d5 = 13
lcd_d6 = 19
lcd_d7 = 26

class LCD:
    GPIO.setmode(GPIO.BCM)
    def __init__(self):
        self.lcd_rs = lcd_rs
        self.lcd_en = lcd_en
        self.lcd_d0 = lcd_d0
        self.lcd_d1 = lcd_d1
        self.lcd_d2 = lcd_d2
        self.lcd_d3 = lcd_d3
        self.lcd_d4 = lcd_d4
        self.lcd_d5 = lcd_d5
        self.lcd_d6 = lcd_d6
        self.lcd_d7 = lcd_d7

        GPIO.setup(self.lcd_en, GPIO.OUT)
        GPIO.setup(self.lcd_rs, GPIO.OUT)
        GPIO.setup(self.lcd_d0, GPIO.OUT)
        GPIO.setup(self.lcd_d1, GPIO.OUT)
        GPIO.setup(self.lcd_d2, GPIO.OUT)
        GPIO.setup(self.lcd_d3, GPIO.OUT)
        GPIO.setup(self.lcd_d4, GPIO.OUT)
        GPIO.setup(self.lcd_d5, GPIO.OUT)
        GPIO.setup(self.lcd_d6, GPIO.OUT)
        GPIO.setup(self.lcd_d7, GPIO.OUT)

    def stuur_instructie(self, instr):
        GPIO.output(self.lcd_en, GPIO.HIGH)
        GPIO.output(self.lcd_rs, GPIO.LOW)
        self.set_GPIO_bits(instr)
        sleep(0.005)
        GPIO.output(self.lcd_en, GPIO.LOW)

    def stuur_teken(self, waarde):
        ascii = ord(waarde)
        GPIO.output(self.lcd_en, GPIO.HIGH)
        GPIO.output(self.lcd_rs, GPIO.HIGH)
        self.set_GPIO_bits(ascii)
        sleep(0.005)
        GPIO.output(self.lcd_en, GPIO.LOW) # Bij low wordt data verwerkt.

    def stuur_tekst(self, tekst):
        secondline = False

        for i in range(len(tekst)):
            self.stuur_teken(tekst[i])
            if (tekst[i] == " ") and (" " not in tekst[(i + 1):16]) and (tekst[15] != " ") and secondline == False:
                instructie = int(0x40 | 0b10000000)  # een ddram moet je bit 7 toevoegen
                self.stuur_instructie(instructie)  # volgende lijn. set ddram cursor position 0x40
                secondline = True
            if (i == 15 and secondline == False):
                instructie = int(0x40 | 0b10000000)  # een ddram moet je bit 7 toevoegen
                self.stuur_instructie(instructie)  # volgende lijn. set ddram cursor position 0x40
                secondline = True

    def set_GPIO_bits(self, byte):
        list_digits = [lcd_d0, lcd_d1, lcd_d2, lcd_d3, lcd_d4, lcd_d5, lcd_d6, lcd_d7]
        for i in range(0,8):
            if((byte & (2**i)) == 0):
                GPIO.output(list_digits[i], GPIO.LOW)
            else:
                GPIO.output(list_digits[i], GPIO.HIGH)


def get_temperature():
    # open het 'w1_slave' bestand voor de sensor:
    # haal er er de juiste regel uit:


    # haal de waarde van t uit de regel:
    # ...
    # zet om naar int en deel door 1000 alvorens de waarde te returnen
    # return ...

    myfile = open('/sys/bus/w1/devices/w1_bus_master1/28-0416c0a80aff/w1_slave')
    for line in myfile:
        try:
            karakter = line.find("=")
            temperature = float(line[karakter + 1:])/1000
            return temperature
        except:
            pass
    myfile.close()

def main():
    GPIO.setmode(GPIO.BCM)
    try:
        lcd = LCD()
        lcd.stuur_instructie(56) # 8-bit, 2 lines, character font 5x10
        lcd.stuur_instructie(15) # display aan, cursor aan, cursor blink aan
        lcd.stuur_instructie(1) # clear display en cursor home

        #lcd.stuur_tekst("Geef een tekst in: ")
        #test = input("Geef een tekst in: ")
        #lcd.stuur_instructie(1)
#
        #lcd.stuur_tekst(test)
        #lcd.stuur_instructie(12)

        lcd.stuur_instructie(12)
        #temp = get_temperature()
        test = "test test test test"
        lcd.stuur_instructie(1)

        #lcd.stuur_tekst("De temperatuur is: {0}C.".format(str(round(temp, 2))))
        lcd.stuur_tekst(test)


    except KeyboardInterrupt:
        pass
    finally:
        GPIO.setwarnings(False)  # get rid of warning when no GPIO pins set up

if __name__ == '__main__':
    main()

