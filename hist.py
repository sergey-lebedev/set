import cv
import cv2
import time
import numpy as np

WHITE = (255, 255, 255)

images_dir = './samples'
#filename = 'Webcam-1355581255.png'
filename = 'Webcam-1355052953.png'
#filename = 'Webcam-1356160723.png'
#filename = 'Webcam-1355053113.png'
#filename = 'Webcam-1356180412.png'
#filename = 'Webcam-1355052975.png'
image = cv2.imread('/'.join((images_dir, filename)))
cv2.moveWindow('experiment', 100, 100)

first_anchor = None
second_anchor = None
box_drawing = False
box = ((-1, -1), (0, 0))

def plot_hist(image):
    bins = np.arange(256) #.reshape(256,1)
    slices = cv2.split(image)
    colors = zip(('b', 'g', 'r'), slices)
    color_dict = {
        'b': (255, 0, 0),
        'g': (0, 255, 0),
        'r': (0, 0, 255)
    }
    l1_norm = []
    subhists = []
    height = 300
    for i, (color, slice) in enumerate(colors):
        cv2.imshow(color, slice)
        subhist = cv2.calcHist([slice], [0], None, [256], [0, 255])
        subhists.append(subhist)
        params = (0, height - 1, cv2.NORM_MINMAX)
        cv2.normalize(subhist, subhist, *params)
        l1_norm.append(cv.Norm(cv.fromarray(subhist), None, cv2.NORM_L1))
    l1_norm_min = min(l1_norm)
    hist_image = np.zeros((height, 256, 3))
    for i, (color, slice) in enumerate(colors):
        subhist = subhists[i]
        params = (l1_norm_min, 0, cv2.NORM_L1)
        cv2.normalize(subhist, subhist, *params)
        subhist = np.int32(np.around(subhist))
        pts = np.column_stack((bins, height - subhist))
        cv2.polylines(hist_image, [pts], False, color_dict[color])
    cv2.imshow('hist: ', hist_image)

def adaptive_threshold(image):
    result = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    result = cv2.medianBlur(result, 5)
    cv2.imshow('blured', result)
    #result = cv2.inpaint(result)
    adaptive_method = cv2.ADAPTIVE_THRESH_MEAN_C
    threshold_type = cv2.THRESH_BINARY_INV
    block_size = 7
    c = 4
    result = cv2.adaptiveThreshold(result, 255, adaptive_method, threshold_type, block_size, c)
    cv2.imshow('threshold', result)
    return result

def canny(image):
    result = cv2.Canny(image, 0, 255)  
    cv2.imshow('canny', result)
    return result

def draw_all_contours(image):
    copy = image.copy()
    result = adaptive_threshold(copy)
    contours, hierarchy = cv2.findContours(result, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    print hierarchy
    color = (255, 255, 255)
    for i in range(len(contours)):
        cv2.drawContours(copy, contours, i, color)
        moments = cv2.moments(contours[i])
        rect = cv2.boundingRect(contours[i])
        (a, b, c, d) = rect
        rectangle = ((a, b), (a + c, b + d), WHITE)
        cv2.putText(copy, str(i), ((a + c), (b + d)), 1, 1, WHITE)
        cv2.rectangle(copy, *rectangle)
        #print i
        #print cv2.HuMoments(moments)
        #print cv.MinAreaRect2(cv.fromarray(contours[i]))
    for i in range(len(contours)):
        print i, cv2.matchShapes(contours[0], contours[i], cv.CV_CONTOURS_MATCH_I3 , 0)
    return copy

def draw_box(image, first, second):
    cv2.rectangle(image, first, second, (0, 255, 0))

def get_subimage(image, first_anchor, second_anchor):
    (fax, fay) = first_anchor
    (sax, say) = second_anchor
    width = abs(fax - sax)
    height = abs(fay - say)
    center = ((fax + sax) / 2, (fay + say) / 2)
    subimage = cv2.getRectSubPix(image, (width, height), center)
    return subimage

def mouse_callback(event, x, y, flags, image):
    global first_anchor
    global second_anchor
    global box_drawing
    global temp
    global box
    if event == cv2.EVENT_MOUSEMOVE:
        if box_drawing and first_anchor:
            box = (first_anchor, (x, y))
            temp = image.copy()
            draw_box(temp, *box)
    if event == cv2.EVENT_LBUTTONDOWN:
        temp = image.copy()
        box_drawing = not box_drawing
        if not first_anchor:
            first_anchor = (x, y)
        else:
            second_anchor = (x, y)
        if first_anchor and second_anchor:
            subimage = get_subimage(image, *box)
            plot_hist(subimage)
            subimage = draw_all_contours(subimage)
            cv2.imshow('result', subimage)
            first_anchor = None
            second_anchor = None

main_window = 'example4'
temp = image.copy()
while True:
    cv2.setMouseCallback(main_window, mouse_callback, image)
    cv2.imshow(main_window, temp)
    if cv2.waitKey(10) == 27:
        cv2.destroyAllWindows()
        break
