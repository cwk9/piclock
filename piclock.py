import serial
import time
import datetime
import threading

class Alarm:
   'Common base class for all alarms'
   alarmcount = 0
   def __init__(self, alarmtime, alarmdate, alarmrepeat, alarmlength):
      self.alarmtime = alarmtime
      self.alarmdate = alarmdate
      self.alarmrepeat = alarmrepeat
      self.alarmlength = alarmlength
      Alarm.alarmcount += 1

#    @alarmrepeat.setter
#    def value(self, v):
#        if not (): raise Exception("Value must be daily, weekdays")
#        self._value = v

   def totalAlarms(self):
     print Alarm.alarmcount

   def displayAlarm(self):
      print "Time : ", self.alarmtime,  ", Date: ", self.alarmdate,  ", Repeat: ", self.alarmrepeat,  ", Length: ", self.alarmlength

newalarm = Alarm("14:00", "Feb 30", "False", "60")
newalarm2 = Alarm("17:32", "Feb 03", "True", "60")

newalarm.displayAlarm()
newalarm2.displayAlarm()