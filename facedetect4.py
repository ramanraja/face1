# show faces in realtime streaming video; on key press, cut and save the face in file

import cv2
import time
import my_imutils
from videostream import VideoStream 
import argparse
import os.path

video_file = None
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",  required = False, help = "Path to the video file")
args = vars(ap.parse_args())
if not args['video']==None: video_file = args['video']
print  video_file

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
            time.sleep(5)

stream.stop()
time.sleep(2.0)
cv2.destroyAllWindows()
print "Bye !"