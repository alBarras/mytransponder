print('Firebase Script Started!')
import RPi.GPIO as GPIO
from time import sleep
import json
import os.path
from os import path

useLeds = True  #set to False if the GPIO pins are used for other purposes like attaching an screen

timeBetweenUploads = 5  #10
timeLedOn = 1

jsonPath = '/run/dump1090-fa/aircraft.json'

#LED (feedback)
if useLeds:
    GPIO.setmode(GPIO.BCM)  #set the purpose of the GPIO pins
    GPIO.setup(17,GPIO.OUT,initial=GPIO.LOW)    #set pin as output  (RED LED: indicates new lecture, regardless if connected to internet or not)
    GPIO.setup(27,GPIO.OUT,initial=GPIO.LOW)    #set pin as output  (GREEN LED: indicates the system is up and running with full connection to internet)
    GPIO.setup(22,GPIO.OUT,initial=GPIO.LOW)    #set pin as output  (HITE LED : indicates at least one aircraft has been found)

def uploadEmptyAircraft():
    ident = "999"
    lat = "999"
    lon = "999"
    alt = "999"
    squawk = "999"
    uploadStr = 'ident: '+ident+', lat: '+lat+', lon: '+lon+', alt: '+alt+', squawk: '+squawk
    print('   No aircraft with XY positioning found, will upload only -> '+uploadStr)
    #result = fb.put(fb_dir,count,uploadStr)
    new_aircraft = root.child('detectedAircrafts').push({
        'ident': ident,
        'lat': lat,
        'lon': lon,
        'alt': alt,
        'squawk': squawk
    })

#define function
noSigStr = 'NoSig'
def getAndUploadAircraftsData():
    print('\n--- New JSON Reading ---')
    fb.delete(fb_dir,'')    #if there is any data in the realtime database, it will be deleted
    aircraft_json = json.load(open(jsonPath))   #reload the JSON file from the default location (the R820T2 SDR & DVB-T USB must be connected in order the file to exist)
    count = 0
    somethingUploaded = False
    arduinoStr = ''
    for plane in aircraft_json["aircraft"]:
        count = count + 1
        print('   '+str(count)+'.- Aircraft Found')
        #try to get identifier
        try:
            ident = str(plane["flight"])
        except:
            ident = '-------'
        print('      ident: '+ident)
        #try to get XY position
        try:
            lat = str(plane["lat"])
            lon = str(plane["lon"])
        except:
            lat = noSigStr
            lon = noSigStr
        print('      lat: '+lat+', lon: '+lon)
        #try to get altitude
        try:
            alt = str(plane["alt_baro"])
        except:
            alt = noSigStr
        print('      alt: '+alt)
        #try to get squawk
        try:
            squawk = str(plane["squawk"])
        except:
            squawk = noSigStr
        print('      squawk: '+squawk)
        #ACTUAL NEW AIRCRAFT FOUND (the info got from it is enough and reliable)
        if lat!=noSigStr and lon!=noSigStr:    #only if the XY position is known, upload it
            if not somethingUploaded:
                somethingUploaded = True
                if useLeds:
                    GPIO.output(22,GPIO.HIGH)
            arduinoStr = arduinoStr + 't'+str(lat) +'g'+ str(lon) + 'i'+str(ident)+str(squawk) + '_';
            uploadStr = 'ident: '+ident+', lat: '+lat+', lon: '+lon+', alt: '+alt+', squawk: '+squawk
            print('         will upload (for Android) -> '+uploadStr)
            # result = fb.put(fb_dir,count,uploadStr)
            new_aircraft = root.child('detectedAircrafts').push({
                'ident': ident,
                'lat': lat,
                'lon': lon,
                'alt': alt,
                'squawk': squawk
            })
    if count==0:
        print('   No Aircraft Found')
    if not somethingUploaded:
        uploadEmptyAircraft()
        arduinoStr = 'none'
    #for Arduino
    #"t10.3g13.5iANE87574006_t-2.3g-3.2iLOL12347001_" = Aircraft1: latitude10.3 & longitude13.5 & ident+squawk ANE87574006, Aircraft2: latitude-2.3 & longitude-3.2 & ident+squawk LOL12347001
    #"none" if no aircraft has been detected
    print('         will upload (for Arduino) -> '+arduinoStr)
    uploadArduino = fb.put("/params","allLatLong",arduinoStr)

#endless loop (actual action)
allInitialized = False
lastLecture = True
while True:
    #just user feedback
    if useLeds:
        GPIO.output(17,GPIO.HIGH)    #turn LED on, regardless if connected to internet or not
    #actual functionality
    if allInitialized:
        lastLecture = not lastLecture
        fb.put('/params','lastrasplecture',str(lastLecture))    #to check that the device is online from the android app
        getAndUploadAircraftsData()
    #initializing system
    else:
        if path.exists(jsonPath):   #check first if the json file has been created (it takes up to 5min, normally less than 1min)
            try:    #check also that we can contact firebase
                from firebase import firebase
            except:
                print('\n--- Waiting for Internet ---')
            else:
                #firebase (to upload data)
                fb_url = 'https://mytransponder-ppl-default-rtdb.firebaseio.com'    #firebase real time database url
                fb_dir = '/detectedAircrafts/'    #direction in database
                fb = firebase.FirebaseApplication(fb_url, authentication = None)   #make actual connection      #result = fb.put(fb_dir,'varName','varValue')    #change a value
                import firebase_admin
                from firebase_admin import credentials
                cred = credentials.Certificate("/home/pi/mytransponder/mytransponder-ppl-firebase-adminsdk-c1kdd-0a85ee915d.json")
                firebase_admin.initialize_app(cred, {
                    'databaseURL' : 'https://mytransponder-ppl-default-rtdb.firebaseio.com'
                })
                from firebase_admin import db
                root = db.reference()

                allInitialized = True
                fb.put('/params','lastrasplecture',str(lastLecture))    #to check that the device is online from the android app
                if useLeds:
                    GPIO.output(27,GPIO.HIGH)
        else:
            print('\n--- Waiting for JSON file ---')
    #waiting time between lectures
    if useLeds:
        sleep(timeLedOn)
        GPIO.output(17,GPIO.LOW) #turn LED off
        GPIO.output(22,GPIO.LOW)
        sleep(timeBetweenUploads-timeLedOn) #wait for next upload
    else:
        sleep(timeBetweenUploads) #wait for next upload
