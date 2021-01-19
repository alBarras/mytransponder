print('Firebase Script Started!')
import RPi.GPIO as GPIO
from time import sleep
import json
import os.path
from os import path

timeBetweenUploads = 2  #10
timeLedOn = 1

jsonPath = '/run/dump1090-fa/aircraft.json'

#firebase (to upload data)
def initializeFirebase():
    from firebase import firebase
    fb_url = 'https://mytransponder-ppl-default-rtdb.firebaseio.com'    #firebase real time database url
    fb_dirStr = 'detectedAircrafts'
    fb_dir = '/'+fb_dirStr+'/'    #direction in database
    fb = firebase.FirebaseApplication(fb_url)   #make actual connection
    # result = fb.put(fb_dir,'varName','varValue')    #change a value

#LED (feedback)
GPIO.setmode(GPIO.BCM)  #set the purpose of the GPIO pins
GPIO.setup(17,GPIO.OUT,initial=GPIO.LOW)    #set pin as output
GPIO.setup(27,GPIO.OUT,initial=GPIO.LOW)    #set pin as output

#define function
noSigStr = 'NoSignal'
def getAndUploadAircraftsData():
    print('\n--- New JSON Reading ---')
    fb.delete(fb_dir,'')    #if there is any data in the realtime database, it will be deleted
    aircraft_json = json.load(open(jsonPath))   #reload the JSON file from the default location (the R820T2 SDR & DVB-T USB must be connected in order the file to exist)
    count = 0
    for plane in aircraft_json["aircraft"]:
        count = count + 1
        print('   '+str(count)+'.- Aircraft Found')
        #identifier
        try:
            ident = plane["flight"]
        except:
            ident = '---'+str(count)
        print('      ident: '+ident)
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
        #squawk
        try:
            squawk = plane["squawk"]
        except:
            squawk = noSigStr
        print('      squawk: '+str(squawk))

        if lat!=noSigStr and long!=noSigStr:    #only if the XY position is known, upload it
            uploadStr = 'ident: '+ident+', lat: '+str(lat)+', long: '+str(long)+', alt: '+str(altitude)+', squawk: '+str(squawk)
            print('         will upload -> '+uploadStr)
            result = fb.put(fb_dir,count,uploadStr)
    if count==0:
        print('   No Aircraft Found')

#endless loop (actual action)
allInitialized = False
while True:
    GPIO.output(17,GPIO.HIGH)    #turn LED on
    if allInitialized:
        getAndUploadAircraftsData()
    else:
        if path.exists(jsonPath):   #check first if the json file has been created (it takes up to 5min, normally less than 1min)
            GPIO.output(27,GPIO.HIGH)
            initializeFirebase()
            allInitialized = True
        else:
            print('\n--- Waiting for JSON file ---')
    sleep(timeLedOn)
    GPIO.output(17,GPIO.LOW) #turn LED off
    sleep(timeBetweenUploads-timeLedOn) #wait for next upload



# import RPi.GPIO as GPIO
# from time import sleep
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(17,GPIO.OUT,initial=GPIO.LOW)
# while True:
#    GPIO.output(17,GPIO.HIGH)
#    sleep(1)
#    GPIO.output(17,GPIO.LOW)
#    sleep(1)
