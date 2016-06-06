import datetime
import threading
import sys
import configparser

#Read config file
config = configparser.ConfigParser()
config.read('pyclock.conf')

def ring_ring():
    sys.stdout.write('ring ring\n')
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

clock1 = Clock()
clock2 = Clock()

clock1.set_alarm(sys.argv[1], sys.argv[2])
clock2.set_alarm(sys.argv[3], sys.argv[4])

#clock1.set_alarm(config['ALARMS']['alarm1'])
print ((config['ALARMS']['alarm1']).split(":"))

clock1.run()
clock2.run()