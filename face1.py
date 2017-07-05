# Take a snapshot with USB/Picamera and find the faces in it

import cv2
import time
import my_imutils
from videostream import VideoStream 

#Load a cascade file for detecting faces
face_cascade = cv2.CascadeClassifier('../XML/haarcascades/haarcascade_frontalface_alt.xml')
print face_cascade
#if face_cascade is None:
#   print "Could not find cascade training set"
#   raise SystemExit(1)
    
stream = VideoStream()
stream.start()
time.sleep(2.0)
frame = stream.read()
if frame is None:
    print "No camera !"
    raise SystemExit(1)   
         
for i in range(3):
    frame = stream.read()
    frame = my_imutils.resize(frame, 480)
    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)
    nfaces = len(faces)
    print "Found "+str(nfaces)+" face(s)"
    for (x,y,w,h) in faces:
          cv2.rectangle(frame, (x,y),(x+w,y+h),(0,0,255),2)    
    cv2.imshow("Frame", frame)
    if (len(faces) > 0):
          cv2.imwrite("face{0}.jpg".format(i), frame)
    print "Press any key... (Esc to quit)"
    if cv2.waitKey(0) & 0xff == 27: break
    
stream.stop()    
time.sleep(2)  # need time to join the thread; otherwise it hangs
cv2.destroyAllWindows()
print "Bye !"