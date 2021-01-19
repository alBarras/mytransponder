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
    GPIO.setup(17,GPIO.OUT,initial=GPIO.LOW)    #set pin as output
    GPIO.setup(27,GPIO.OUT,initial=GPIO.LOW)    #set pin as output

#define function
noSigStr = 'NoSignal'
def getAndUploadAircraftsData():
    print('\n--- New JSON Reading ---')
    fb.delete(fb_dir,'')    #if there is any data in the realtime database, it will be deleted
    aircraft_json = json.load(open(jsonPath))   #reload the JSON file from the default location (the R820T2 SDR & DVB-T USB must be connected in order the file to exist)
    count = 0
    somethingUploaded = False
    for plane in aircraft_json["aircraft"]:
        count = count + 1
        print('   '+str(count)+'.- Aircraft Found')
        #identifier
        try:
            ident = plane["flight"]
        except:
            ident = '-------'
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
            if not somethingUploaded:
                somethingUploaded = True
            uploadStr = 'ident: '+ident+', lat: '+str(lat)+', long: '+str(long)+', alt: '+str(altitude)+', squawk: '+str(squawk)
            print('         will upload -> '+uploadStr)
            result = fb.put(fb_dir,count,uploadStr)
    if count==0:
        print('   No Aircraft Found of Any Kind')
    if not somethingUploaded:
        uploadStr = 'No Aircraft Found'
        print('   No aircraft with XY positioning found, will upload only -> '+uploadStr)
        result = fb.put(fb_dir,count,uploadStr)

#endless loop (actual action)
allInitialized = False
while True:
    if useLeds:
        GPIO.output(17,GPIO.HIGH)    #turn LED on
    if allInitialized:
        getAndUploadAircraftsData()
    else:
        if path.exists(jsonPath):   #check first if the json file has been created (it takes up to 5min, normally less than 1min)
            try:    #check also that we can contact firebase
                from firebase import firebase
            except:
                print('\n--- Waiting for Internet ---')
            else:
                #firebase (to upload data)
                fb_url = 'https://mytransponder-ppl-default-rtdb.firebaseio.com'    #firebase real time database url
                fb_dirStr = 'detectedAircrafts'
                fb_dir = '/'+fb_dirStr+'/'    #direction in database
                fb = firebase.FirebaseApplication(fb_url, authentication = None)   #make actual connection      #result = fb.put(fb_dir,'varName','varValue')    #change a value
                allInitialized = True
                if useLeds:
                    GPIO.output(27,GPIO.HIGH)
        else:
            print('\n--- Waiting for JSON file ---')
    if useLeds:
        sleep(timeLedOn)
        GPIO.output(17,GPIO.LOW) #turn LED off
        sleep(timeBetweenUploads-timeLedOn) #wait for next upload
    else:
        sleep(timeBetweenUploads) #wait for next upload
