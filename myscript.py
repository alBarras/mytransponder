import RPi.GPIO as GPIO
from time import sleep
from firebase import firebase
import json

#json (to get data)
aircraft_json = json.load(open('/run/dump1090-fa/aircraft.json'))   #load the JSON file from the default location

#firebase (to upload data)
fb_url = 'https://mytransponder-ppl-default-rtdb.firebaseio.com'    #firebase real time database url
fb_dir = '/lol/'    #direction in database
fb = firebase.FirebaseApplication(fb_url)   #make actual connection
result = fb.put(fb_dir,'a','11')    #change a value

#LED (feedback)
GPIO.setmode(GPIO.BCM)  #set the purpose of the GPIO pins
GPIO.setup(17,GPIO.OUT,initial=GPIO.LOW)    #set pin as output

#define function
def getAircraftsData():
    count = 0
    for plane in aircraft_json["aircraft"]:
        count = count + 1
        #identifier
        try:
            squawk = planes["squawk"]
        except:
            squawk = count
        #XY position
        try:
            lat = plane["lat"]
            long = plane["lon"]
        except:
            lat = "no signal"
            long = "no signal"
        #altitude
        try:
            altitude = plane["alt_baro"]
        except:
            altitude = "no signal"

        result = fb.put(fb_dir,'test','squawk: '+squawk+', lat: '+lat+', long: '+long+', alt: '+altitude)
        break

#endless loop (actual action)
while True:
   GPIO.output(17,GPIO.HIGH)    #turn LED on
   getAircraftsData()
   GPIO.output(17,GPIO.LOW) #turn LED off
   sleep(5) #wait for 2 seconda
