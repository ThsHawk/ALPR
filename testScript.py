import cv2
import numpy as np
import easyocr
import imutils

import time
import kagglehub

# Download latest version
path = kagglehub.dataset_download("andrewmvd/car-plate-detection")
dataSetPath = path + "/images/"

timeList = []
carNumber = 0
while(carNumber < 433):
##---
        print("Carro " + str(carNumber))
        timestamp = time.monotonic_ns()
##---


        img = cv2.imread(dataSetPath + "Cars" + str(carNumber) + ".png") #read image

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #convert image to gray
        bfilter = cv2.bilateralFilter(gray, 11, 17, 17) #Noise reduction

        edged = cv2.Canny(bfilter, 30, 200) #Edge detection

        keypoints = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) #Find contours
        contours = imutils.grab_contours(keypoints) #Grab contours
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10] #Sort contours

        #Loop over our contours to find the best possible approximate contour of 10 contours
        location = None
        for contour in contours:
            approx = cv2.approxPolyDP(contour, 10, True)
            if len(approx) == 4:
                location = approx
                break

        carNumber += 1
        if location is None: continue
        #Verify if the contour fit in retangular aproximation
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / float(h)
        if not aspect_ratio >= 2 and aspect_ratio <= 5: continue

        mask = np.zeros(gray.shape, np.uint8) #create blank image with same dimensions as the original image
        cv2.drawContours(mask, [location], 0,255, -1) #Draw contours on the mask image
        cv2.bitwise_and(img, img, mask=mask) #Take bitwise AND between the original image and mask image

        (x,y) = np.where(mask==255) #Find the co-ordinates of the four corners of the document
        (x1, y1) = (np.min(x), np.min(y)) #Find the top left corner
        (x2, y2) = (np.max(x), np.max(y)) #Find the bottom right corner
        cropped_image = gray[x1:x2+1, y1:y2+1] #Crop the image using the co-ordinates

        reader = easyocr.Reader(['en'], gpu=False) #create an easyocr reader object with english as the language
        result = reader.readtext(cropped_image) #read text from the cropped image

        #text = result[0][-2] #Extract the text from the result
        #print("Placa encontrada: " + text)

##---
        timestamp = time.monotonic_ns() - timestamp
        timeList.append(timestamp)
        print("Execução realizada em:" + str(timestamp / 1000000000))
##---

average = sum(timeList) / len(timeList)
print("Média aritmética: " + str(average / 1000000000) + "s")
