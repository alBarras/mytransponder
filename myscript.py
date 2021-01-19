print('Firebase Script Started!')
import RPi.GPIO as GPIO
from time import sleep
from firebase import firebase
import json

#json (to get data)
aircraft_json = json.load(open('/run/dump1090-fa/aircraft.json'))   #load the JSON file from the default location (the R820T2 SDR & DVB-T USB must be connected in order the file to exist)

#firebase (to upload data)
fb_url = 'https://mytransponder-ppl-default-rtdb.firebaseio.com'    #firebase real time database url
fb_dirStr = 'detectedAircrafts'
fb_dir = '/'+fb_dirStr+'/'    #direction in database
fb = firebase.FirebaseApplication(fb_url)   #make actual connection
# result = fb.put(fb_dir,'varName','varValue')    #change a value

#LED (feedback)
GPIO.setmode(GPIO.BCM)  #set the purpose of the GPIO pins
GPIO.setup(17,GPIO.OUT,initial=GPIO.LOW)    #set pin as output

#define function
noSigStr = 'NoSignal'
def getAircraftsData():
    print('\n--- New JSON Reading ---')
    fb.delete(fb_dir,'')    #if there is any data in the realtime database, it will be deleted
    count = 0
    for plane in aircraft_json["aircraft"]:
        count = count + 1
        print('   '+str(count)+'.- Aircraft Found')
        #identifier
        try:
            squawk = planes["squawk"]
        except:
            squawk = count
        print('      squawk: '+str(squawk))
        #XY position
        try:
            lat = plane["lat"]
            long = plane["lon"]
        except:
            lat = noSigStr
            long = noSigStr
        print('      long: '+str(long)+', lat: '+str(lat))
        #altitude
        try:
            altitude = plane["alt_baro"]
        except:
            altitude = noSigStr
        print('      altitude: '+str(altitude))

        if lat!=noSigStr and long!=noSigStr:
            uploadStr = 'squawk: '+str(squawk)+', lat: '+str(lat)+', long: '+str(long)+', alt: '+str(altitude)
            print('         will upload -> '+uploadStr)
            result = fb.put(fb_dir,count,uploadStr)

#endless loop (actual action)
while True:
   GPIO.output(17,GPIO.HIGH)    #turn LED on
   getAircraftsData()
   sleep(1)
   GPIO.output(17,GPIO.LOW) #turn LED off
   sleep(20) #wait for 2 seconda
