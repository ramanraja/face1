# show faces in realtime streaming video; if the person is close enough, trigger Kairos.

import cv2
import time
import my_imutils
from videostream import VideoStream 
import argparse
import os.path
import requests
import json
import pyttsx
from gtts import gTTS
import os
import platform
#---------------------------------------------------------------------------------
class TTS :
    ENGINE_PYTTS = 1
    ENGINE_GOOGLE = 2
    
    def __init__(self, ttsEngine=ENGINE_PYTTS):
        self.engine_type = ttsEngine
        if (self.engine_type == self.ENGINE_PYTTS):
            self.engine = pyttsx.init()
        self.os = platform.system().lower()
        print 'Platform OS: ', self.os    
        
    def speak (self, textInput, cacheFileName="tts/text2speech.mp3"):
        if (self.engine_type==self.ENGINE_PYTTS): # TODO: pytts does not have a disk file
            self.engine.say(textInput)
            self.engine.runAndWait()
        else:
            voice = gTTS(text=textInput, lang='en')
            voice.save(cacheFileName)
            if self.os =='windows':
                os.system('start ' +cacheFileName)   # Windows
            else:    
                #os.system('mpg321 ' +cacheFileName)  # Linux
                os.system('omxplayer -o local ' +cacheFileName)  # RPi
    
    def speakFromCache (self, cacheFileName):
        if self.os =='windows':
            os.system('start ' +cacheFileName)   # Windows
        else:    
            #os.system('mpg321 ' +cacheFileName)  # Linux
            os.system('omxplayer -o local ' +cacheFileName)  # RPi
           
#---------------------------------------------------------------------------------

class Kairos :
    NETWORK_ERROR = 'network_error'
    NO_FACE = 'error'
    UNKNOWN_FACE = 'unknown'
    STATUS_OK = 200
    
    def __init__(self, gallery):
        self.gallery = gallery
        self.baseurl = "https://api.kairos.com/recognize"
        self.headers = {
            "content-type":"application/json", 
            "app_id":"edb4a215", 
            "app_key":"3df74777b90859421ca9947444c6e7ea"}
        print 'Base URL: ', self.baseurl
        #print 'Headers: ', self.headers
        
    # TODO: make this asynchronous    
    def identify (self, filename):
        imgfile = open (filename, "rb")  
        img64 = imgfile.read().encode("base64") 
        imgfile.close()
        body = {"image":img64, "gallery_name":self.gallery}
	try:
            response = requests.post(self.baseurl, json=body, headers=self.headers)
	except:
	    return (self.NETWORK_ERROR, 0)
        print 'Status: ', response.status_code
	if (response.status_code != self.STATUS_OK):
	    return (self.NETWORK_ERROR, 0)
        return (self.process(response.json()))

    def process (self, jobject):
        print jobject
        if ('Errors' in jobject):
            print "ERROR: Could not detect any face in the picture!"
            return (self.NO_FACE, 0)  # do not remove this return statement !
        print 'Face detected'
        res = jobject['images'][0]['transaction']['status']
        if res == 'success':
            name = jobject['images'][0]['transaction']['subject_id']
            confidence = jobject['images'][0]['transaction']['confidence']   
            print 'Person identified: ', name, ' (', confidence, ')'
            return (name, int(round(100*confidence)))
        else:
            print 'Failed to identify the person in the picture'     
            return (self.UNKNOWN_FACE, 0)

    def listGalleries(self):
	listurl = "https://api.kairos.com/gallery/list_all"
	try:
	    response = requests.post(listurl, json={}, headers=self.headers)
	except:
	    return (self.NETWORK_ERROR, 0)
	if (response.status_code != self.STATUS_OK):
	    return (self.NETWORK_ERROR, 0)
        jresponse = response.json()
	print jresponse
        return (tuple(jresponse['gallery_ids']), 1)
#---------------------------------------------------------------------------------

gallery = 'MyGallery3'
video_file = None
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",  required = False, help = "Path to the video file")
args = vars(ap.parse_args())
if not args['video']==None: video_file = args['video']
print 'Video file: ', video_file

tts = TTS(TTS.ENGINE_GOOGLE)   # TTS.ENGINE_PYTTS 
kairos = Kairos(gallery)

source = 0  # camera
if video_file is not None:
    source = video_file

#Load a cascade file for detecting faces
xmlfile = '../XML/haarcascades/haarcascade_frontalface_alt.xml'
if not os.path.isfile(xmlfile):
   print "Could not find cascade training set"
   raise SystemExit(1)
face_cascade = cv2.CascadeClassifier(xmlfile)

fileName = "detected_face.jpg" 
stream = VideoStream(src=source)
stream.start()
time.sleep(2.0)
frame = stream.read()
if frame is None:
    print "No camera !"
    raise SystemExit(1)   

print "press any key to save file; ESC to quit.."          
while(True): 
    frame = stream.read()
    frame = my_imutils.resize(frame, 640)
    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)
    for (x,y,w,h) in faces:
         cv2.rectangle(frame, (x,y),(x+w,y+h),(0,0,255),2)  
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(2)  # & 0xff
    if key==27:
        break
    else:
        if w > 280:
            print "width: ",w, "  height: ",h
            cv2.imwrite(fileName, gray[y:y+h, x:x+h])
            print 'file saved as: ',fileName
            (name, confidence) = kairos.identify(fileName)
            print "Name: ", name, " confidence: ",confidence
            tts.speak("Hello, " +name) # +". Good morning")
            time.sleep(5)

stream.stop()
time.sleep(2.0)
cv2.destroyAllWindows()
print "Bye !"