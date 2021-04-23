import cv2
import numpy as np
import math

# Function to show image
def viewImage(image):
    # Create window
    cv2.namedWindow('Display', cv2.WINDOW_NORMAL)
    # Show image in that window
    cv2.imshow('Display', image)
    # Wait key 0
    cv2.waitKey(0)
    # After that destroy all windows
    cv2.destroyAllWindows()

# Function to find contours
def findContours(image):

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(gray, cv2.COLOR_HSV2RGB)
    gray = cv2.cvtColor(gray, cv2.COLOR_RGB2GRAY)

    ret, threshold = cv2.threshold(gray, 90, 255, 0)
    # viewImage(threshold) ## 1

    contours, hierarchy = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(image, contours, -1, (0, 0, 255), 3)
    # viewImage(image) ## 2

    # Return all contours
    return contours, threshold

# Function to find required area
def findGreatesContour(contours):
    # Area of whole picture
    whole_area = 0
    # Required area
    largest_area = 0
    # Index of whole picture
    whole_area_index = -1
    # Index of required area
    largest_contour_index = -1

    # Loop to check all contours
    for i in range(len(contours)):
        # Each area
        area = cv2.contourArea(contours[i])
        # Make first area the whole area
        if whole_area == 0:
            whole_area = area
            whole_area_index = i
        # If current area bigger than whole area
        # so largest area becomes whole area
        # and whole area becomes current area
        elif area > whole_area:
            largest_area = whole_area
            whole_area = area
            largest_contour_index = whole_area_index
            whole_area_index = i
        # If current area less than whole area and bigger than largest area
        # largest area becomes current area
        elif area < whole_area and area > largest_area:
            largest_area = area
            largest_contour_index = i

    # Return largest area and its index
    return largest_area, largest_contour_index


# Function to check if mark is almost round
def checkRound(threshold, rad, cX, cY):
    '''
    This function checks ring inside the circle
    If black area inside it bigger than 30% of area of this ring function returns true
    '''

    # Black area inside the circle
    area = 0
    # Radius of inner circle
    R = rad - 50
    # Loop to check every pixel of ring
    for i in range(int(cX - rad), int(cX + rad)):
        a = int(i - cX) * int(i - cX)
        rad2 = rad * rad
        if rad2 < a:
            continue
        y1 = int(cY - math.sqrt(rad2 - a))
        y2 = int(cY + math.sqrt(rad2 - a))
        for j in range(y1, y2):
            # If current pixel is inside inner circle loop continues
            # otherwise we check colour of this pixel
            # If it is black area increases
            if (i - cX) * (i - cX) + (j - cY) * (j - cY) > R * R:
                if threshold[i, j] == 0:
                    area += 1

    # Find area of ring
    S = math.pi * rad * rad - math.pi * R * R
    S *= 0.3

    # If black area is bigger than 30% of ring return true
    return area > S

# Method to find mark on picture
def detect(pic, d):
    # Open main image
    image = cv2.imread(pic)
    # Copy image for output
    output = image.copy()

    # Contours on the main image
    contours, threshold = findContours(image)

    # Find required area and index of this area
    largest_area, largest_contour_index = findGreatesContour(contours)

    # Find center of required area
    # cnt is required area
    cnt = contours[largest_contour_index]
    M = cv2.moments(cnt)
    # x and y coordinates of center
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])


    # Find radius of area
    # Assume that required area is circle find radius using formula S=π*R^2
    # so R=sqrt(S/π)
    rad = math.sqrt(largest_area / math.pi)

    '''Some values in case of error
    Coefficient for radius
    delta X and Y for moving of center '''
    coef = 1
    dX = 0.0
    dY = 0.0

    # Change radius and center of circle usinf user's changes
    rad = rad * coef
    cX = cX + dX
    cY = cY + dY

    # Draw circle
    # Small circle to show center of big circle
    cv2.circle(output, (int(cX), int(cY)), 3, (0,255,255), 10)
    # Big circle
    cv2.circle(output, (int(cX), int(cY)), int(rad), (0,255,255), 3)

    # Diameter of circle
    diam = d * rad
    cv2.putText(output, ("diameter~" + str(diam) + "micron"), (int(cX - rad), int(cY - rad - 15)),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)

    # Save picture with result picture
    cv2.imwrite("Result.jpg", output)
    # Show this picture
    viewImage(output)

    # If mark is not round write corresponding message
    if not checkRound(threshold, rad, cX, cY):
        print("Maybe it is not a round mark, check please")

    # If diameter of circle greater or equal than size of picture method returns 'False'
    return (rad * 2 < image.shape[0] and rad * 2 < image.shape[1])