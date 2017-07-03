# Face recognition (see all the notes at the bottom)
# http://hanzratech.in/2015/02/03/face-recognition-using-opencv.html
# http://vision.ucsd.edu/content/yale-face-database
# http://hanzratech.in/2015/02/03/face-recognition-using-opencv.html#sthash.XMlaosZO.dpuf
# http://disq.us/url?url=http%3A%2F%2Fwww.lfd.uci.edu%2F%7Egohlke%2Fpythonlibs%2F%23opencv%3ASvnDmGsHRkRNEHz3Cl87-S3Gbu0&cuid=3387583

import cv2, os
import numpy as np
from PIL import Image

#-----------------------------------------------------------------------------------
def get_images_and_labels(path):

    # Append all the absolute image paths in a list image_paths 
    # We will not read the image with the .sad extension in the training set 
    # Rather, we will use them to test our accuracy of the training 
    
    image_paths = [os.path.join(path, f) for f in os.listdir(path) if not f.endswith('.sad')] 
    
    images = []
    labels = []
    for image_path in image_paths:
        image_pil = Image.open(image_path).convert('L')  # convert to gray scale
        image = np.array(image_pil, 'uint8')   # convert image to numpy array
        # get the image label
        nbr = int(os.path.split(image_path)[1].split(".")[0].replace("subject", ""))
        faces = faceCascade.detectMultiScale(image)
        
        # If face is detected, save the face and labels  
        for (x, y, w, h) in faces:
            images.append(image[y: y + h, x: x + w]) 
            labels.append(nbr) 
            cv2.imshow("Adding faces to traning set...", image[y: y + h, x: x + w]) 
            cv2.waitKey(50)
    return images, labels
#-----------------------------------------------------------------------------------
cascadePath = "haarcascade_frontalface_default.xml"  
faceCascade = cv2.CascadeClassifier(cascadePath)
recognizer = cv2.createLBPHFaceRecognizer()

# Load the Yale Dataset
path = './yalefaces'    
images, labels = get_images_and_labels(path)
cv2.destroyAllWindows() 

# Train
recognizer.train(images, np.array(labels))

# Test
# Append the images with the extension .sad into image_paths  
image_paths = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.sad')]  

for image_path in image_paths:
    predict_image_pil = Image.open(image_path).convert('L')  
    predict_image = np.array(predict_image_pil, 'uint8')  
    faces = faceCascade.detectMultiScale(predict_image)  
    
    for (x, y, w, h) in faces:
        nbr_predicted, conf = recognizer.predict(predict_image[y: y + h, x: x + w]) 
        nbr_actual = int(os.path.split(image_path)[1].split(".")[0].replace("subject", ""))  
        if nbr_actual == nbr_predicted:
            print "{} is Correctly Recognized with confidence {}".format(nbr_actual, conf) 
        else:  
            print "{} is Incorrectly Recognized as {}".format(nbr_actual, nbr_predicted)  
        cv2.imshow("Recognizing Face", predict_image[y: y + h, x: x + w])  
        cv2.waitKey(1000)
#------------------------------------------------------------------------------
'''
Note 1:
If the line
nbr_predicted, conf = recognizer.predict(predict_image[y: y + h, x: x + w])
throws an error that int object is not iterable (may happen in opencv 3.1)
then remove the variable conf.        
http://disq.us/url?url=http%3A%2F%2Fstackoverflow.com%2Fquestions%2F35790673%2Fopencv-3-python%3Atzk9YnurNmHARYSAPL_vqHiCNlU&cuid=3387583

Aliter:
Replace that line with the following block:
# for openCV >= 3.0.0 
result = cv2.face.MinDistancePredictCollector()
recognizer.predict(predict_image[y: y + h, x: x + w],result, 0)
nbr_predicted = result.getLabel()
conf = result.getDist()

Note 2:
If you get the error:
AttributeError: 'module' object has no attribute 'face'
Then use the wheel from  
http://disq.us/url?url=http%3A%2F%2Fwww.lfd.uci.edu%2F%7Egohlke%2Fpythonlibs%2F%23opencv%3ASvnDmGsHRkRNEHz3Cl87-S3Gbu0&cuid=3387583 
and install on Windows by:
'pip install opencv_python-3.1.0+contrib_opencl-cp35-cp35m-win32.whl'
Then use recognizer = cv2.face.createLBPHFaceRecognizer()

The reason this no longer works is because the face recognition module has been moved out of the core 
OpenCV library from version 3. It now exists in a separate sub-library called 'opencv_contrib' which is 
less well supported and harder to get up and running.
The Github page for the contributions module is here:
https://disq.us/url?url=https%3A%2F%2Fgithub.com%2FItseez%2Fopencv_contrib%3AaXWTlb6edgjpoSbo-KTzJ1BuutQ&cuid=3387583
See also:
http://disq.us/url?url=http%3A%2F%2Fanswers.opencv.org%2Fquestion%2F45782%2Fbuilding-opencv_contrib-for-opencv-3-windows-gui%2F%3A5JCdrAA68DDqUOPUASuPaQZ_Swc&cuid=3387583
http://disq.us/url?url=http%3A%2F%2Fanswers.opencv.org%2Fquestion%2F56859%2Fopencv-300-facerecognizer-and-python-bindings%2F%3Az6m2YVFPorQSgN48z-7gkoLI8c0&cuid=3387583
EDIT: Did eventually get this to work myself on windows 8.1. Building the whole OpenCV library as static 
(unticking 'BUILD_SHARED_LIBS' in cmake) was the final step in making it happen. The default python bindings 
appear to work now. Also don't forget to copy across your new 20+ megabyte .pyd file to the 
python site-packages directory.
http://disq.us/url?url=http%3A%2F%2Fwww.quora.com%2FWhat-are-the-best-face-detection-APIs%3AKYtIiLSTxA7w5Xz9pp50oBMbmr4&cuid=3387583

Note 3:
If you get the error:
'Fisherfaces method all input samples (training images) must be of equal size!' 
Then resize the face images in get_images_and_labels(path) before returning:

final_images = []
largest_image_size = 0
largest_width = 0
largest_height = 0

for image in images:
if image.size > largest_image_size:
largest_image_size = image.size
largest_width, largest_height = image.shape

for image in images:
image = cv2.resize(image, (largest_width, largest_height), interpolation=cv2.INTER_CUBIC)
final_images.append(image)

return final_images, labels
'''        
        