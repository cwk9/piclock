#Alarm clock for raspberry pi using serial display and a single switch.

import datetime
import threading
import sys
import configparser
import serial
#pydub needs to be installed not in standard library.
from pydub import AudioSegment
from pydub.playback import play

#Read config file
config = configparser.ConfigParser()
config.read('pyclock.conf')

#
ispi = config['IS_PI']['pi'] == 'no'
if ispi == 'no':
    #import RPi.GPIO as GPIO
    #GPIO.setmode(GPIO.BCM)
    #GPIO.setup(7, GPIO.IN)
    port = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=3.0)
    lcdbacklight = "high"
    alarmstatus = "OFF"
    pastalarmstatus = "OFF"

print (lcdbacklight)

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