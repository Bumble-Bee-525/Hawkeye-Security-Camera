from cv2 import VideoCapture, CAP_DSHOW, FONT_HERSHEY_SIMPLEX, CAP_PROP_FRAME_HEIGHT, CAP_PROP_FRAME_WIDTH, imshow, waitKey, destroyAllWindows, cvtColor, COLOR_BGR2GRAY, absdiff, threshold, THRESH_BINARY, countNonZero, putText, LINE_AA, line, rectangle
from winsound import PlaySound

print("LAUNCHING. . .")

def percent_change(im1, im2, sensitivity):
    # Convert the images to grayscale
    gray1 = cvtColor(im1, COLOR_BGR2GRAY)
    gray2 = cvtColor(im2, COLOR_BGR2GRAY)

    # Calculate the absolute difference between the grayscale images
    diff = absdiff(gray1, gray2)

    # Threshold the difference image to find regions with significant changes
    limit =  sensitivity # Adjust this value based on your specific needs
    limit, thresholded_diff = threshold(diff, limit, 255, THRESH_BINARY)

    # Count the number of white pixels (changed regions) in the thresholded image
    changed_pixels = countNonZero(thresholded_diff)

    # Calculate the percentage of changed pixels relative to the total image size
    total_pixels = gray1.shape[0] * gray1.shape[1]
    changed_percentage = (changed_pixels / total_pixels) * 100

    return changed_percentage


# configure settings
settings = open("settings.txt", "r")
camWidth = int(settings.readline())
camHeight = int(settings.readline())
tMax = float(settings.readline())

font = int(settings.readline())

temp = settings.readline()
lineColor = tuple(map(int, temp.split(",")))

temp = settings.readline()
textColor = tuple(map(int, temp.split(",")))

xMargin = int(settings.readline())
yMargin = int(settings.readline())

sensitivity = int(settings.readline())
settings.close()

# initialize video capture
camNumber = int(input("camera index: "))
cap = VideoCapture(camNumber, CAP_DSHOW)

# wait for capture to start
while not cap.isOpened():
    pass

# set video capture resolution
cap.set(CAP_PROP_FRAME_WIDTH, camWidth)
cap.set(CAP_PROP_FRAME_HEIGHT, camHeight)

# initialize default crop settings
status, oldImage = cap.read()
targetX = int(camWidth / 2)
targetY = int(camHeight / 2)
oldRef = oldImage.copy()
oldRef = oldImage[targetY - yMargin:targetY + yMargin, targetX - xMargin:targetX + xMargin]

# run continously
while True:
    # get an image from webcam
    status, newImage = cap.read()
    displayImage = newImage.copy()
    newRef = newImage.copy()
    newRef = newRef[targetY - yMargin:targetY + yMargin, targetX - xMargin:targetX + xMargin]

    # get change between old and new reference images
    change = percent_change(oldRef, newRef, sensitivity)

    # display stats
    putText(displayImage, "Camera " + str(camNumber) + ":", (20, 50), font, 2, textColor, 4, LINE_AA)
    putText(displayImage, f"change: {change:.2f}%", (20, 90), font, 0.75, textColor, 2, LINE_AA)
    putText(displayImage, f"tMAX: {tMax:.2f}%", (20, 120), font, 0.75, textColor, 2, LINE_AA)
    putText(displayImage, f"tCEN: {targetX}, {targetY}", (20, 150), font, 0.75, textColor, 2, LINE_AA)
    putText(displayImage, f"tWID: {xMargin * 2}", (20, 180), font, 0.75, textColor, 2, LINE_AA)
    putText(displayImage, f"tHEI: {yMargin * 2}", (20, 210), font, 0.75, textColor, 2, LINE_AA)
    putText(displayImage, f"RES: {camWidth}, {camHeight}", (20, 240), font, 0.75, textColor, 2, LINE_AA)

    # draw crosshairs
    line(displayImage, (targetX - 20, targetY), (targetX + 20, targetY), lineColor, 2)
    line(displayImage, (targetX, targetY - 20), (targetX, targetY + 20), lineColor, 2)

    # draw box showing target area  
    rectangle(displayImage, (targetX - xMargin, targetY - yMargin), (targetX + xMargin, targetY + yMargin), lineColor, 2)

    # if a disturbance is detected
    if change > tMax:
        # add to gui
        putText(displayImage, "CONTACT", (20, 500), font, 2, textColor, 4, LINE_AA)

        # display image
        imshow("Security Camera", displayImage)

        # play sound
        PlaySound("warning.wav", 0)

        # get user input
        key = waitKey(0)

        # if false flag
        if (key == ord('f')):
            # retake the reference image
            status, oldImage = cap.read()
            oldRef = oldImage.copy()
            oldRef = oldImage[targetY - yMargin:targetY + yMargin, targetX - xMargin:targetX + xMargin]
        # if real threat detected
        else:
            destroyAllWindows()
            break
    else:
        # display image
        imshow("Security Camera", displayImage)
        # debuggin stuf
        #imshow("oldRef", oldRef)
        #imshow("newRef", newRef)


    



    
    key = waitKey(1)
    
    #if a key was pressed
    if key != -1:
        validKey = True
        # press r to recalibrate (reset reference picture)
        if key == ord('r'):
            oldImage = newImage.copy()
        # press x to exit
        elif key == ord('x'):
            destroyAllWindows()
            break
        # press w to increase vertical scope
        elif key == ord('w') and targetY - (yMargin + 5) >= 0 and targetY + yMargin + 5 <= camHeight:
            yMargin += 5
        # press s to decrease vertical scope
        elif key == ord('s') and yMargin > 8:
            yMargin -= 5
        # press d to increase horizontal scope
        elif key == ord('d') and targetX - (xMargin + 5) >= 0 and targetX + xMargin + 5 <= camWidth:
            xMargin += 5
        # press a to decrease horizontal scope
        elif key == ord('a') and xMargin > 8:
            xMargin -= 5
        # press i to move target up
        elif key == ord('i') and (targetY - 5) - yMargin >= 0:
            targetY -= 5
        # press k to move target down
        elif key == ord('k') and targetY + 5 + yMargin <= camHeight:
            targetY += 5
        # press l to move target right
        elif key == ord('l') and targetX + 5 + xMargin <= camWidth:
            targetX += 5
        # press j to move target left
        elif key == ord('j') and (targetX - 5) - xMargin >= 0:
            targetX -= 5
        # press t to increase tMax
        elif key == ord('t') and tMax + 0.05 <= 100:
            tMax += 0.05
        # press g to decrease tMax
        elif key == ord('g') and tMax - 0.05 > 0:
            tMax -= 0.05
        #some random key was hit
        else:
             validKey = False
            
        # recrop the old image to fit new target area if a valid key was hit
        if validKey:
            oldRef = oldImage.copy()
            oldRef = oldRef[targetY - yMargin:targetY + yMargin, targetX - xMargin:targetX + xMargin]