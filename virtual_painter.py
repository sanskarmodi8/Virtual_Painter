import mediapipe as mp
import cv2
import numpy as np
import time
import os
import hand_tracking_module as htm

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

imgcanvas = np.zeros((720,1280,3), np.uint8) #canvas on which we will draw having 3 channels with 0-255 range of values

brushThickness = 35
eraserThickness = 100

n=0

xp,yp = 0,0

drawcolor = (0,255,0)

# following code block is for importing images from a folder and storing them in a list
folderpath = "images"
mylist = os.listdir(folderpath)
print(mylist)
overlayList = []
for imPath in mylist:
    image = cv2.imread(f'{folderpath}/{imPath}')
    print(f'{folderpath}/{imPath}')
    overlayList.append(image)
header = overlayList[0]

detector = htm.handDetector(detectionCon=0.75)

while True:
    success, img = cap.read()
    
    img = cv2.flip(img, 1)
    
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    
    # count the number of open fingers 
    n=0
    if len(lmList)!=0:
        x1, y1 = lmList[8][1],lmList[8][2]# tip of index finger
        x2, y2 = lmList[12][1],lmList[12][2]# tip of middle finger
        fingers = []
        if lmList[4][2] <= lmList[3][2] and lmList[8][1]>lmList[4][1]:
            fingers.append("Thumb")
            print("Thumb is open")
        if lmList[8][2] < lmList[7][2]:
            fingers.append("Index Finger")
            print("Index Finger is open")
        if lmList[12][2] < lmList[11][2]:
            fingers.append("Middle Finger")
            print("Middle Finger is open")
        if lmList[16][2] < lmList[15][2]:
            fingers.append("Ring Finger")
            print("Ring Finger is open")
        if lmList[20][2] < lmList[19][2]:
            fingers.append("Pinky Finger")
            print("Pinky Finger is open")
        if len(fingers)==0:
            print("All fingers are closed")
            
        n = len(fingers)
        
    # if n = 2 -> selection mode else drawing mode (if not n = 0)
    if n==2:
        xp,yp = 0,0
        print("Selection Mode")
        if y1 < 125: # if in header region
            if 250 < x1 < 450:#if i m clicking at purple brush
                header = overlayList[3]
                drawcolor = (255,0,255)
            elif 550 < x1 < 750:#if i m clicking at blue brush
                header = overlayList[1]
                drawcolor = (255,0,0)
            elif 800 < x1 < 950:#if i m clicking at green brush
                header = overlayList[0]
                drawcolor = (0,255,0)
            elif 1050 < x1 < 1200:#if i m clicking at eraser
                header = overlayList[2]
                drawcolor = (0,0,0)
        cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), drawcolor, cv2.FILLED)#selection mode is represented as rectangle

    else:
        if n!=0:
            print("Drawing Mode")
            cv2.circle(img, (x1, y1), 15, drawcolor, cv2.FILLED)#drawing mode is represented as circle
            if xp==0 and yp==0: #first frame
                xp,yp = x1,y1
            if drawcolor==(0,0,0):
                cv2.line(img, (xp,yp), (x1,y1), drawcolor, eraserThickness)
                cv2.line(imgcanvas, (xp,yp), (x1,y1), drawcolor, eraserThickness)
            else:
                cv2.line(img, (xp,yp), (x1,y1), drawcolor, brushThickness)
                cv2.line(imgcanvas, (xp,yp), (x1,y1), drawcolor, brushThickness)
            xp,yp = x1,y1
            
    
    # Convert the image canvas to grayscale
    imgGray = cv2.cvtColor(imgcanvas, cv2.COLOR_BGR2GRAY)

    # Apply a binary threshold to the grayscale image to create a mask
    # Pixels with a value greater than 50 are set to 255 (white), while
    # pixels with a value less than or equal to 50 are set to 0 (black)
    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)

    # Convert the mask to a 3-channel image (BGR) so that it can be
    # combined with the original image
    imgInv = cv2.cvtColor(imgInv,cv2.COLOR_GRAY2BGR)

    # Use a bitwise AND operation to "erase" the parts of the original
    # image that correspond to white pixels in the mask
    img = cv2.bitwise_and(img,imgInv) 

    # Use a bitwise OR operation to combine the masked image with the
    # original image, effectively "pasting" the masked image onto the
    # canvas
    img = cv2.bitwise_or(img,imgcanvas)
            
    # setting the header image
    img[0:125, 0:1280] = header
    
    cv2.imshow("Image", img)
    cv2.waitKey(1)