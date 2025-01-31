import cv2 as cv
import numpy as np
import os

from utils import ResizeWithAspectRatio

# Change the working directory to the folder this script is in.
# Doing this because I'll be putting the files from each video in their own folder on GitHub
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Can use IMREAD flags to do different pre-processing of image files,
# like making them grayscale or reducing the size.
# https://docs.opencv.org/4.2.0/d4/da8/group__imgcodecs.html
sample_img = cv.imread('assets/sample.png', cv.IMREAD_UNCHANGED)

# skill_casting_img = cv.imread('assets/skill-casting.png', cv.IMREAD_UNCHANGED)
skill_off_cooldown_img = cv.imread('assets/skill-off-cooldown.png', cv.IMREAD_UNCHANGED)
# skill_on_cooldown_img = cv.imread('assets/skill-on-cooldown.png', cv.IMREAD_UNCHANGED)

# There are 6 comparison methods to choose from:
# TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
# You can see the differences at a glance here:
# https://docs.opencv.org/master/d4/dc6/tutorial_py_template_matching.html
# Note that the values are inverted for TM_SQDIFF and TM_SQDIFF_NORMED
result = cv.matchTemplate(sample_img, skill_off_cooldown_img, cv.TM_SQDIFF_NORMED)

# I've inverted the threshold and where comparison to work with TM_SQDIFF_NORMED
threshold = 0.17
# The np.where() return value will look like this:
# (array([482, 483, 483, 483, 484], dtype=int32), array([514, 513, 514, 515, 514], dtype=int32))
locations = np.where(result <= threshold)
# We can zip those up into a list of (x, y) position tuples
locations = list(zip(*locations[::-1]))
print(locations)

if locations:
    print('Found object.')

    object_w = skill_off_cooldown_img.shape[1]
    object_h = skill_off_cooldown_img.shape[0]
    line_color = (0, 255, 0)
    line_type = cv.LINE_4

    # Loop over all the locations and draw their rectangle
    for loc in locations:
        # Determine the box positions
        top_left = loc
        bottom_right = (top_left[0] + object_w, top_left[1] + object_h)
        # Draw the box
        cv.rectangle(sample_img, top_left, bottom_right, line_color, line_type)

    resized = ResizeWithAspectRatio(sample_img, width=1280)

    cv.imshow('Matches', resized)
    cv.waitKey()
    #cv.imwrite('result.jpg', resized)


else:
    print('object not found.')
