import cv2 as cv
#import djitellopy 
import numpy as np

cap = cv.VideoCapture(0)
hsvVals = [0, 0, 117, 179, 22, 219]
sensors = 3

threshold = 0.2
width, height = 480, 360

sensitivity = 3 # if number is high less sensitive 
weights = [-25, -15, 0, 15, 25]
curve = 0 # Global Curve
fspeed = 15

def thresholding(img):
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    lower = np.array([hsvVals[0],hsvVals[1],hsvVals[2]])
    upper = np.array([hsvVals[3],hsvVals[4],hsvVals[5]])
    mask = cv.inRange(hsv, lower, upper)

    return mask
    
def getContours(imgThres, img):
    contours, heirarchy = cv.findContours(imgThres, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    biggest = max(contours, key=cv.contourArea)
    x,y,w,h = cv.boundingRect(biggest)
    cx = x + w//2
    cy = y + h//2
    cv.drawContours(img, contours, -1, (255, 0, 255), 7)
    cv.circle(img, (cx, cy), 10, (0,255,0), cv.FILLED)

    return cx

def getSensorOutput(imgThres, sensors):
    imgs = np.hsplit(imgThres, sensors)
    totalPixels = (img.shape[1]//sensors) * img.shape[0]
    senOut = []
    for x, im in enumerate(imgs):
        pixelCount = cv.countNonZero(im)
        if pixelCount > threshold*totalPixels:
            senOut.append(1)
        else:
            senOut.append(0)
        cv.imshow(str(x), im)   
  
        printDirection(senOut)

    return senOut   

def printDirection(senOut):
    if senOut == [0,1,0]: 
        print(senOut, " Go Straight")
    elif senOut == [1,0,0]: 
        print(senOut, " Go Left")
    elif senOut == [0,0,1]: 
        print(senOut, " Go Right")
    elif senOut == [1,1,0]: 
        print(senOut, " Slight Left")
    elif senOut == [0,1,1]: 
        print(senOut, " Slight Right")
    elif senOut == [1,1,1]: 
        print(senOut, " Stop")
    elif senOut == [0,0,0]: 
        print(senOut, " Stop")

def weightAdjust(senOut):

    # Switch Case

    match senOut:
        case [1,0,0]: curve = weights[0]
        case [1,1,0]: curve = weights[1]
        case [0,1,0]: curve = weights[2]
        case [0,1,1]: curve = weights[3]
        case [0,0,1]: curve = weights[4]

        case [1,1,1]: curve = weights[2]
        case [0,0,0]: curve = weights[2]
        case [1,0,1]: curve = weights[2]

    return curve


def sendCommand(senOut, cx):

    # Translation
    lr = (cx - width // 2)//sensitivity
    lr = int(np.clip(lr, -10, 10))
    if lr < 2 and lr > -2: lr = 0

    #me.send_rc_control(lr, 0, 0, 0)

    # Rotation
    curve = weightAdjust(senOut)
    #me.send_rc_control(lr, fspeed, 0, curve)


while True:
    success, img = cap.read()
    img = cv.resize(img, (width, height))
    #img = cv.flip(img, 0)
                                                         
    imgThres = thresholding(img)
    cx = getContours(imgThres, img) # For Translation
    senOut = getSensorOutput(imgThres, sensors) # For Rotation
    #sendCommand(senOut, cx)

    cv.imshow("Test", img)
    cv.imshow("Path", imgThres)

    if cv.waitKey(1) & 0xFF == ord('f'):
        img = cv.flip(img, 0)

    if cv.waitKey(1) & 0xFF == ord(' '):
        break