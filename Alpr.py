#DEPENDENCIES
#  easyocr
#  imutils
#  opencv-python
#  matplotlib

import cv2
#from matplotlib import pyplot as plt
import numpy as np
import easyocr
import imutils
import random

class Alpr:
    def __init__(self, path):
        #read image
        self.img = cv2.imread(path)

    def recognize(self):
        #convert image to gray
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        bfilter = cv2.bilateralFilter(gray, 11, 17, 17) #Noise reduction

        #Edge detection
        edged = cv2.Canny(bfilter, 30, 200)

        #Find contours
        keypoints = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        #Grab contours
        contours = imutils.grab_contours(keypoints)
        #Sort contours
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

        #Loop over our contours to find the best possible approximate contour of 10 contours
        location = None
        for contour in contours:
            approx = cv2.approxPolyDP(contour, 10, True)
            if len(approx) == 4:
                location = approx
                break

        #create blank image with same dimensions as the original image
        mask = np.zeros(gray.shape, np.uint8)
        #Draw contours on the mask image
        new_image = cv2.drawContours(mask, [location], 0,255, -1)
        #Take bitwise AND between the original image and mask image
        new_image = cv2.bitwise_and(img, img, mask=mask)

        #Find the co-ordinates of the four corners of the document
        (x,y) = np.where(mask==255)
        #Find the top left corner
        (x1, y1) = (np.min(x), np.min(y))
        #Find the bottom right corner
        (x2, y2) = (np.max(x), np.max(y))
        #Crop the image using the co-ordinates
        cropped_image = gray[x1:x2+1, y1:y2+1]

        #create an easyocr reader object with english as the language
        reader = easyocr.Reader(['en'])
        #read text from the cropped image
        result = reader.readtext(cropped_image)
        #Extract the text from the result
        return result[0][-2]

#font = cv2.FONT_HERSHEY_SIMPLEX #Font style
#res = cv2.putText(img, text=text, org=(approx[0][0][0], approx[1][0][1]+60), fontFace=font, fontScale=1, color=(0,255,0), thickness=2, lineType=cv2.LINE_AA) #put the text on the image
#res = cv2.rectangle(img, tuple(approx[0][0]), tuple(approx[2][0]), (0,255,0),3) #Draw a rectangle around the text

#plt.imshow(cv2.cvtColor(res, cv2.COLOR_BGR2RGB)) #show the final image with text