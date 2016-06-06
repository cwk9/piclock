import datetime
import threading
import sys
import configparser
from pydub import AudioSegment
from pydub.playback import play

#Read config file
config = configparser.ConfigParser()
config.read('pyclock.conf')

#Load alarm wave soudn
wavname = "alarm.wav"
alarmwav = AudioSegment.from_wav(config['ALARMWAVS']['alwav'])

def ring_ring():
    sys.stdout.write('ring ring\n')
    play(alarmwav)
    sys.stdout.flush()

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

#Create our clock objects
clocks = [ Clock() for i in range(len(config.items('ALARMS')))]

alcount = 0
for cl in clocks:
    cl.set_alarm(config['ALARMS'][str(alcount)].split(":")[0],config['ALARMS'][str(alcount)].split(":")[1])
    alcount = alcount + 1
    cl.run()
