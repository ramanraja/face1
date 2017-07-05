# Kairos with speech; Prompter class and speak from cache added
# GPIO class added: button with edge detection and LED indicator  

'''
TODO:
switch off preview

read things from config file 
remote config through bluetooth buttons
try wlan0 with your mobile as the wifi hot spot 
move chek_network and self healing code into the Network class
check_network to connect to jsontest.com and get_ip_address
get_local_ip and get_public_ip methods in Network class

Make bluetooth status work !
convert all print to G.trace, trace2 for bluetooth
try ethernet, then wlan and then usb automatically
blue tooth: select camera, exit, reset network, select eth/wlan/usb
For pytts: How to enable audio caching?
'''
#-------------------------------------------------------------------

class G:

    def __init__(self, debug=True, serial=None):
        self.debug = debug
        self.serial = serial
        print self.serial

    def trace (self, msg):
        if self.debug:
 	    print msg
   
    def trace2 (self, msg):
        print msg
        #if(self.serial is not None): # TODO
	#   self.serial.write('%s\n'.format(msg).encode())
#-------------------------------------------------------------------
class Hardware:

    button1 = 13    # pin 33
    #button2 = 19   # pin 35
    #button3 = 26   # pin 37
    button4 = 23    # pin 16 
    red_led   =  21    # pin 40
    green_led =  16    # pin 36
    blue_led  =  20    # pin 38

    def __init__(self):
     GPIO.cleanup()  # precaution ?
	GPIO.setmode(GPIO.BCM)   
	GPIO.setup(self.button1, GPIO.IN, pull_up_down = GPIO.PUD_UP) # active LOW   
	#GPIO.setup(self.button2, GPIO.IN, pull_up_down = GPIO.PUD_UP) 
	#GPIO.setup(self.button3, GPIO.IN, pull_up_down = GPIO.PUD_UP) 
	GPIO.setup(self.button4, GPIO.IN, pull_up_down = GPIO.PUD_UP) 
	GPIO.setup(self.green_led, GPIO.OUT)
	GPIO.setup(self.red_led, GPIO.OUT)
	GPIO.setup(self.blue_led, GPIO.OUT)
	GPIO.output(self.green_led, False)
	GPIO.output(self.red_led, False)
	GPIO.output(self.blue_led, False)

    def cleanup(self):
	  GPIO.output(self.green_led, False)
	  GPIO.output(self.red_led, False)
	  GPIO.output(self.blue_led, False)
	  GPIO.cleanup()

    def on(self, led):
	  GPIO.output(led, True)

    def off(self, led):
	  GPIO.output(led, False)

    def detectEdge (self, button):
    # detect a rising edge within one second of pressing the button
        state = GPIO.input(button)
        GPIO.output(self.green_led, state)
        if(state): 
	    return False      
	for i in range(50):
            state = GPIO.input(button)
            GPIO.output(self.green_led, state)
	    if (state):
		return True
	    time.sleep(0.02)
        return False
#-------------------------------------------------------------------
import sys
from requests.exceptions import ConnectionError
from subprocess import call

class Network:
    def __init__(self, networkInterface='usb0'):
	self.interface = networkInterface

    def reset(self):
	g.trace2 ('Resetting network interface ' +self.interface +' ...')
        rc = call (["sudo", "dhclient", self.interface])
        print "Done resetting. Return code:", rc

    def restart(self):
    	g.trace2('Restarting network...')
    	rc = call (["sudo", "/etc/init.d/networking", "restart"])
    	print "Done restarting. Return code:", rc

    #def checkConnectivity(self):
    #return True  # TODO: have a generic cheker here
#-------------------------------------------------------------------

import pyttsx
from gtts import gTTS
import os
import platform

class TTS :
    ENGINE_PYTTS = 1
    ENGINE_GOOGLE = 2
    
    def __init__(self, ttsEngine=ENGINE_PYTTS):
        self.engine_type = ttsEngine
        if (self.engine_type == self.ENGINE_PYTTS):
            self.engine = pyttsx.init()
        self.os = platform.system().lower()
        print 'Platform OS: ', self.os    
        
    def speak (self, textInput, cacheFileName="/home/pi/cv1/text2speech.mp3"):
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

from random import randint
import os.path

class Prompter:
    person = {
        "unknown" : ["Hello, new friend ! I think we have never met before... This is Lisa, from service desk.",
            "Welcome to Verizon face identification system.. To begin an exciting employee journey, please register yourself first.",
            "Hello, good morning.. Please download the V Zee bot app, and register yourself for the service."],
        "rajaraman" : "Hello, Raja Raman.. Good morning. Your work station number is W K 2 34. Thank you.",
        "nikhilesh" : ["Hi, dude ! IIT Nikhileysh.",
            "Hi, Nikhileysh. I am told you bought a pair of golden socks."],
        "mythily" : ["Hi, Doctor my thili. Are you still moody melancholy?",
            "Hello, My thili. you have put on some weight recently."],
        "Xamma" : "That is our mother. But Ammaa does not always mean Jaya Lalitha.",
        "vaidy" : "Hello, vye the kal yana soondaram. Your work station number is W K 7 O 8. Thank you.",
        "dinesh" : "Hello, Dhineysh Raaj.. Workstation number W K 4 37 has been reserved for you. Thank you.",
        "richard" : "Good morning, Richard. Please proceed to work station number 5 7 8. Thank you.",
        "anil" : "Good morning, Anil Kumaar. Welcome back to India.. Cabin number CN 2 2 5 has been reserved for you. \
        If you need assistance, please contact the smart office... Have a nice day."                         
        }
        
    status = {
        "take_snap" : "Welcome to Verizon face identification system. I will take a picture of your face. \
	  at the count of three... One... Two... Three..",
        "shutdown" : "Your bot is shutting down..Good bye!",
        "kairos_started" : "Kairos is starting.",
	"recognizer_inited" : "Face identifier created.",
	"net_inited" : "Network created.",
	"try_network" : "trying to connect.",
	"net_success" : "Network connected successfully.",
	"camera_OK" : "My camera is ready..",
	"main_loop" : "Entering main loop",
        "reset_network" : "Resetting the network..",
	"cache_all" : "I am caching all fixed audio snippets. Please wait"
        }
        
    error = {
        "not_identified" : "The person's face is not in my memory",
        "no_face" : "I think there is an error.. There is no human face in the picture",
        "no_gallery" : "Could not find that gallery. Please check the gallery name",
        "net_error" : "Could not connect to the network.",
        "cloud_error" : "I am unable to contact the cloud server.",
        "speech_engine_error" : "My speech engine has stopped working.",
        "speech_not_enabled" : "I am not speech enabled.",
        "audio_file_error" : "The sound clip is not there",
        "bluetooth_error" : "There is a problem with blue tooth connectivity.",
        "bluetooth_not_on" : "Please switch on my blue tooth.",
        "camera_error" : "Attention. My camera is not working!",
        "init_failed" : "Initial setup failed. I am giving up.."    
     }
    
    def __init__(self, speechEnabled=True, ttsEngine=TTS.ENGINE_GOOGLE, audioFolder="."):
        self.speechEnabled = speechEnabled
        if speechEnabled:
            self.tts = TTS(ttsEngine)         
            if not audioFolder.endswith('/'):
                audioFolder = audioFolder+'/'
            self.audio_folder = audioFolder
            self.audio_extn = '.mp3'
            self.scratch_pad_file =  self.audio_folder +'scratch_file' +self.audio_extn
            print 'Audio folder: ' +self.audio_folder
  
    def notifyStatus (self, statusName):
        print self.status[statusName]  
        if not self.speechEnabled: 
            return
        fname = self.audio_folder  +'status_' +statusName +self.audio_extn
        if os.path.isfile(fname): 
            self.tts.speakFromCache(fname)
        else :
            self.tts.speak(self.status[statusName], fname)
      
    def notifyError (self, errorName):
        print self.error[errorName]  
        if not self.speechEnabled: 
            return
        fname = self.audio_folder  +'error_' +errorName +self.audio_extn
        if os.path.isfile(fname): 
            self.tts.speakFromCache(fname)
        else :
            self.tts.speak(self.error[errorName], fname)      
            
    def announceName (self, name, confidence):
        if (confidence==0):
            if (name==FaceRecognizer.UNKNOWN_FACE):
                self.greet('unknown')
            else:
                self.notifyError('no_face')
        else:    
            self.greet(name)
         
    def greet (self, personName, selectRandom=True):
        personName = personName.lower()
        if (personName not in self.person): # TODO: avoid editing this program every time!
            greeting = 'Hello, ' +personName +'... How are you today ?'
            self.tts.speak (greeting, self.scratch_pad_file)
            print greeting
            return
        
        if (isinstance(self.person[personName], str)):  # it is a string, not a list
            fname = self.audio_folder  +'id_' +personName +self.audio_extn
            self.tts.speak (self.person[personName], fname)
            print (self.person[personName])
            return
        if (not selectRandom):
            fname = self.audio_folder  +'id_' +personName +'_0' +self.audio_extn
            self.tts.speak (self.person[personName][0], fname)
            print (self.person[personName][0])
        else:
            r = randint(0, len(self.person[personName])-1)
            fname = self.audio_folder  +'id_' +personName +'_' +str(r) +self.audio_extn
            self.tts.speak (self.person[personName][r], fname)
            print (self.person[personName][r])
            
    def playSound (self, audioFileName): 
        audioFileName = self.audio_folder +audioFileName
        if os.path.isfile(audioFileName): 
            self.tts.speakFromCache(audioFileName)
        else:
            self.notifyError('audio_file_err')

    def cacheAll (self):
	self.notifyStatus("cache_all")
	for stat in self.status.keys():
	    self.notifyStatus(stat)
	for err in self.error.keys():
	    self.notifyError(err)
#---------------------------------------------------------------------------------

import requests
import json

class FaceRecognizer :
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
'''
*******************************************************************************
import cv2
import my_imutils
import time    

class FaceCamera :
    def __init__(self, width=400, display=True):
        self.resize_width = width   # width of captured image  
        self.display_enabled = display  # to show the frame on the GUI or not
        self.tmp_file_name = 'temp_image.jpg'
        
        print 'Initializing camera...'
        self.camera = cv2.VideoCapture(0)  # -1
        time.sleep(0.25)
        
    def open (self):
        #grabbed = self.camera.isOpened()
        (grabbed, frame) = self.camera.read()
        if  grabbed: 
            print 'Camera is open'
            return True
        else:
            print "No camera found !"
            return False
    
    def preview (self):
        if not self.display_enabled:
            return;
        (grabbed, frame) = self.camera.read()
        cv2.imshow("Your Face", frame)
                
    def getFrame (self):
        (grabbed, frame) = self.camera.read()
        frame = my_imutils.resize(frame, self.resize_width)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(self.tmp_file_name, frame)
        return self.tmp_file_name
        
    def release (self):
        self.camera.release();
***************************************************************************
'''
#----------------------------------------------------------------------------------------
import cv2
import my_imutils
import time    
from picamera import PiCamera
from picamera.array import PiRGBArray

class PiFaceCamera :
    def __init__(self, width=400, display=True):
        self.resize_width = width       # width of captured image  
        self.display_enabled = display  # to show the frame on the GUI or not
        self.tmp_file_name = 'temp_image.jpg'
        
        print 'Initializing camera...'
        self.camera = PiCamera()
	self.resolution = (640,480)
	self.camera.resolution = self.resolution 
	#self.camera.framerate = 10
	#self.camera.rotation = 180
	self.imgarray = PiRGBArray(self.camera, size=self.resolution)
        time.sleep(2.5)  # warm up
        
    def open (self):
        #time.sleep(2.5)
	try:
            self.camera.capture(self.imgarray, 'bgr') # just a trial shot
	    self.imgarray.truncate(0)
            print 'Pi Camera is ready'
            #prompter.notifyStatus("camera_OK")
	    return True
 	except:
            print "No camera found !"
            #prompter.notifyStatus("camera_error")
        return False
    
    def startPreview (self):
        if not self.display_enabled:
	    g.trace2('Camera preview is not enabled')
	    return
        self.camera.preview_fullscreen=False
        self.camera.preview_window=(100,100, self.resolution[0],self.resolution[1])
        self.camera.start_preview()
                
    def stopPreview (self):
        if self.display_enabled:
            self.camera.stop_preview()

    def getFrame (self):
        self.camera.capture(self.imgarray, 'bgr')
	# convert it to np.ndarray before processing
        image = my_imutils.resize(self.imgarray.array, self.resize_width)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(self.tmp_file_name, image)
	self.imgarray.truncate(0)  # prepare for the next grab
        return self.tmp_file_name
        
    def release (self):
        self.camera.close();
#---------------------------------------------------------------------------------

import cv2
import os.path
import warnings
import  serial
import time
import RPi.GPIO as GPIO
import requests.packages.urllib3

def main_loop():
    hardware.on(Hardware.green_led)
    while (True):
        #k = cv2.waitKey(100)  # do not & with 0xff 
        #if k==27: 
            #break
        if not check_bluetooth(): 
	    break
        if hardware.detectEdge(Hardware.button4):
	    hardware.off(Hardware.green_led)
	    hardware.on(Hardware.red_led)
	    take_snapshot()
	    hardware.off(Hardware.red_led)
	    hardware.on(Hardware.green_led)
        time.sleep(0.1)


def bringup_network(maxAttempts=5, delay=5):
    for i in range(maxAttempts):
        g.trace2("Trying to connect to network..")
    	prompter.notifyStatus("try_network")	
    	if (check_connectivity()):
    	    return True
        net.reset()
        time.sleep(delay)
    g.trace2("Trying reset the network..")
    prompter.notifyStatus("reset_network")
    net.restart()
    if (check_connectivity()):
    	return True
    return False


def check_connectivity():
    gals = recognizer.listGalleries()
    print gals
    #if gals[0]==FaceRecognizer.NETWORK_ERROR
    if (gals[1]==0):
	return False
    return True


def take_snapshot():
    print 'Click!'
    #prompter.notifyStatus('take_snap')
    prompter.playSound('camera-shutter.mp3')
    fileName = cam.getFrame()
    (name, confidence) = recognizer.identify(fileName)
    prompter.announceName(name, confidence)


def check_bluetooth():
    try:
        s = ser.readline()
        if len(s) > 0: 
	    return process(s[0])
    except serial.SerialTimeoutException:
        print('Serial error (BT ?)')
        time.sleep(0.5)
    return True


def process(cmdchar):
   if(cmdchar=='q'): 
        return False
   if(cmdchar=='n'): 
        net.reset()
        return True
   if(cmdchar=='d'): 
        if (autoShutdown):
            shutdown_pi()
	return False    # if not auto shutdown, just exit the program
   if(cmdchar=='s'): 
        take_snapshot()
	return True
   print 'processing: Unknown command'
   return True


def cleanup():
    cam.release()   
    prompter.notifyStatus('shutdown')     
    cv2.destroyAllWindows()     
    hardware.cleanup() 
    time.sleep(3)
   

def shutdown_pi (restart=False):
    cleanup()
    print "RPi is Shutting Down !!!............"
    if restart:
        command = "/usr/bin/sudo /sbin/shutdown -r now"   # -r will restart
    else:
        command = "/usr/bin/sudo /sbin/shutdown now"      
    import subprocess
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    print output
#-------------------------------------------------------------------

gallery = 'MyGallery3'
imageWidth = 400
showPreview = True
audioFolder = '/home/pi/cv1/audio_cache'
enableSpeech = True # False 
ttsEngine = TTS.ENGINE_GOOGLE # TTS.ENGINE_PYTTS  #
networkInterface =  'usb0'  # 'eth0'  # 'wlan0'  
autoShutdown = True 

print ('Kairos is starting...')
warnings.filterwarnings("ignore")
#requests.packages.urllib3.disable_warnings() # SSL certificate warning

ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=0)  # RPi BT module
#ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0) # Arduino via USB cable
seropen = ser.isOpen()
if seropen:
    ser.close()
ser.open()
seropen = ser.isOpen()
print 'serial is open: ',seropen

g = G(True, ser)
g.trace2 ('Kairos has started.')
g.trace2 ('serial BT connection is open')

'''
ser.write('Hello android1\r\n'.encode())
ser.flush()
'''
hardware = Hardware()
g.trace2 ('GPIO initialized')

if (not os.path.isdir(audioFolder)):
    os.mkdir(audioFolder)
try:    
    prompter = Prompter(enableSpeech, ttsEngine, audioFolder)
    
    prompter.notifyStatus("kairos_started")
except:
    g.trace2 ('Could not initialize speech module')
    raise SystemExit(1)

#prompter.cacheAll()
#prompter.notifyStatus("")

recognizer = FaceRecognizer(gallery)
prompter.notifyStatus("recognizer_inited") 

net = Network(networkInterface)
prompter.notifyStatus("net_inited")

netready = False
if bringup_network(2, 10): 
    netready = True
    g.trace2('Kairos connected through: '+networkInterface)
    prompter.notifyStatus("net_success")
else:
    g.trace2('Network failure on: '+networkInterface) 
    prompter.notifyError("net_error")

g.trace2('Initializing Pi Camera...')
cam = PiFaceCamera(imageWidth, showPreview)

camready = False 
if (cam.open()):
    camready = True
    g.trace2('Pi Camera is ready')
    prompter.notifyStatus("camera_OK")
    cam.startPreview()
else:
    g.trace2('Failed to initialize Pi Camera')
    prompter.notifyError("camera_error")
    #raise SystemExit(1)
 

if netready & camready:
    print 'Press button to take a snapshot. ^C to exit'
    g.trace2('Entering main loop')
    prompter.notifyStatus("main_loop")
    try :
        main_loop()
    except (KeyboardInterrupt):
        g.trace2('--Keyboard interrupt--')  # the loop terminates
else:
    g.trace2("Quitting.. Initialization failed")
    prompter.notifyError("init_failed")
    
#time.sleep(3)
cleanup()
g.trace2('Bye !')
