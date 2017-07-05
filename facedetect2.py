# Cut and save faces from realtime streaming video

import cv2
import time
import my_imutils
from videostream import VideoStream 
import argparse

video_file = None
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",  required = False, help = "Path to the video file")
args = vars(ap.parse_args())
if not args['video']==None: video_file = args['video']
print  video_file
dest_dir = "."

source = 0  # camera
if video_file is not None:
    source = video_file
    
#Load a cascade file for detecting faces
face_cascade = cv2.CascadeClassifier('../XML/haarcascades/haarcascade_frontalface_alt.xml')
 
stream = VideoStream(src=source)
stream.start()
time.sleep(2.0)
frame = stream.read()
if frame is None:
    print "No camera !"
    raise SystemExit(1)   
          
i = 0          
while(True):     
    frame = stream.read()
    frame = my_imutils.resize(frame, 480)
    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)
    for (x,y,w,h) in faces:
         copy = frame.copy()[y:y+h, x:x+h]  #  [y1:y2, x1:x2]  
         cv2.imwrite(dest_dir+"face{0}.jpg".format(i), copy)
         cv2.rectangle(frame, (x,y),(x+w,y+h),(0,0,255),2)  
         i += 1 
    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) & 0xff == 27: 
         break
    time.sleep(0.5)

stream.stop()
time.sleep(2.0)
cv2.destroyAllWindows()
print "Bye !"