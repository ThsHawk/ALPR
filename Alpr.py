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
    def __init__(self, frame):
        #read image
        self.img = frame

    def recognize(self):
        #convert image to gray
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        bfilter = cv2.bilateralFilter(gray, 11, 17, 17) #Noise reduction

        cv2.imwrite("./imgDebug/filteredInput.jpg", bfilter)

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

        if location is None: return None

        #Verify if the contour fit in retangular aproximation
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / float(h)
        if not aspect_ratio >= 2 and aspect_ratio <= 5: return None

        #create blank image with same dimensions as the original image
        mask = np.zeros(gray.shape, np.uint8)
        #Draw contours on the mask image
        cv2.drawContours(mask, [location], 0,255, -1)
        #Take bitwise AND between the original image and mask image
        cv2.bitwise_and(self.img, self.img, mask=mask)

        #Find the co-ordinates of the four corners of the document
        (x,y) = np.where(mask==255)
        #Find the top left corner
        (x1, y1) = (np.min(x), np.min(y))
        #Find the bottom right corner
        (x2, y2) = (np.max(x), np.max(y))
        #Crop the image using the co-ordinates
        cropped_image = gray[x1:x2+1, y1:y2+1]

        cv2.imwrite("./imgDebug/cropped_image.jpg", cropped_image)

        #create an easyocr reader object with english as the language
        reader = easyocr.Reader(['pt'])
        #read text from the cropped image
        result = reader.readtext(cropped_image)
        if result is None: return None
        
        #Extract the text from the result
        plate_text = []
        for (bbox, recognized_text, confidence) in result:
            if confidence > 0.5: plate_text.append(recognized_text)
        if plate_text is None: return None
        #Extraxt the code license of plate info
        for text in plate_text:
            if len(text)==7: return text.upper()       
        return None