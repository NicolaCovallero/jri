from PIL import Image
import numpy
import cv, cv2

pi = Image.open('img/jri_logo.png')
print pi.size

frame = cv.fromarray(numpy.array(pi))
resize_frame = cv.CreateMat(480, 640, frame.type)  # cv.CV_8UC3
cv.Resize(frame, resize_frame)

cv2.namedWindow('image', cv2.WINDOW_NORMAL)
#cv2.imshow('image', mpimg.imread('img/tux3.jpg'))
cim = cv.fromarray(numpy.asarray(pi))

resize_frame = cv.CreateMat(480, 640, cim.type)  #
cv.Resize(cim, resize_frame)
cv2.imshow('image', numpy.array(resize_frame))
cv2.waitKey(0)
cv2.destroyAllWindows()

