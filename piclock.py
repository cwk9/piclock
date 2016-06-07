#Alarm clock for raspberry pi using serial display and a single switch.

import datetime
import time
import threading
import sys
import configparser
#pydub needs to be installed not in standard library.
from pydub import AudioSegment
from pydub.playback import play

#Read config file
config = configparser.ConfigParser()
config.read('pyclock.conf')

#Set Raspberry Pi related stuff
ispi = config['IS_PI']['pi']
if ispi == 'yes':
    import RPi.GPIO as GPIO
    import serial
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(7, GPIO.IN)
    port = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=3.0)
    lcdbacklight = "high"
    alarmstatus = "OFF"
    pastalarmstatus = "OFF"

    #Clear screen function
    def clearscr():
        port.write('\xFE')
        time.sleep(0.01)
        port.write('\x01')
        time.sleep(0.01)

    #For sending custom LCD commands
    def lcdcmd():
        port.write('\xFE')
        time.sleep(0.1)

    #Function for setting the LCD brightness
    def lcdbright(b):
        if b == "off":
            port.write('\x7C')
            time.sleep(0.1)
            port.write('\x80')
            time.sleep(0.1)
            print("lcd off")
        if b == "high":
            port.write('\x7C')
            time.sleep(0.1)
            port.write('\x9D')
            print("lcd high")
        if b == "medium":
            port.write('\xFE')
            time.sleep(0.1)
            port.write('\x96')
            print("lcd medium")
        if b == "low":
            port.write('\xFE')
            time.sleep(0.1)
            port.write('\x8C')
        print("lcd low")

    #Output text to the LCD screen.
    def wrlcd(l, text):
        if l == 1:
            port.write('\xFE')
            time.sleep(0.01)
            port.write('\x80')
            time.sleep(0.01)
        elif l == 2:
            port.write('\xFE')
            time.sleep(0.01)
            port.write('\xC0')
            time.sleep(0.01)
        else:
            print("Error: line not selected")
            port.write(text)
            time.sleep(0.01)

    #Check button and switch status
    def checkinput():
        global alarmstatus
        while inlcdmenu == False:
            if (GPIO.input(7)):
                alarmstatus = "OFF"
            else:
                alarmstatus = "ON"
                time.sleep(1)  # slow down checking to one second

#Load alarm wave sound
wavname = "alarm.wav"
alarmwav = AudioSegment.from_wav(config['ALARMWAVS']['alwav'])

#What we do when an alarm is triggered
def ring_ring():
    sys.stdout.write('ring ring\n')
    play(alarmwav)
    sys.stdout.flush()

#Create an alarm clock object for every alarm in the config file.
def createclocks():
    # Create our clock objects
    clocks = [Clock() for i in range(len(config.items('ALARMS')))]
    # Set the alarm and start the clock.
    alcount = 0
    for cl in clocks:
        cl.set_alarm(config['ALARMS'][str(alcount)].split(":")[0], config['ALARMS'][str(alcount)].split(":")[1])
        alcount = alcount + 1
        cl.run()

#Our clock object. The core of the program.
class Clock:

    def __init__(self):
        self.alarm_time = None
        self._alarm_thread = None
        self.update_interval = 1
        self.event = threading.Event()

    def run(self):
        while True:
            self.event.wait(self.update_interval)
            if self.event.isSet():
                break
            now = datetime.datetime.now()
            if self._alarm_thread and self._alarm_thread.is_alive():
                alarm_symbol = '+'
            else:
                alarm_symbol = ' '
            sys.stdout.write("\r%02d:%02d:%02d %s"
                % (now.hour, now.minute, now.second, alarm_symbol))
            #sys.stdout.flush()

    def set_alarm(self, hour, minute):
        now = datetime.datetime.now()
        alarm = now.replace(hour=int(hour), minute=int(minute))
        delta = int((alarm - now).total_seconds())
        if delta <= 0:
            alarm = alarm.replace(day=alarm.day + 1)
            delta = int((alarm - now).total_seconds())
        if self._alarm_thread:
            self._alarm_thread.cancel()
        self._alarm_thread = threading.Timer(delta, ring_ring)
        self._alarm_thread.daemon = True
        self._alarm_thread.start()

createclocks()