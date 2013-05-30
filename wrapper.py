import cv2
import scene
import filters
from plot import *

debug = not False

images_dir = './samples'
##filename = 'Webcam-1355581255.png'
#filename = 'Webcam-1355052953.png'
#filename = 'Webcam-1356160723.png'
#filename = 'Webcam-1355053113.png'
##filename = 'Webcam-1356180412.png'
##filename = 'Webcam-1355052975.png'
##filename = 'Webcam-1356180892.png'
#filename = 'Webcam-1356203219.png'
#filename = 'DSC03466_mini.JPG'
filename = 'DSC03467_mini.JPG'
#filename = 'DSC03537_mini.JPG'
#filename = 'DSC03539_mini.JPG'
#filename = 'sharp.bmp'
image = cv2.imread('/'.join((images_dir, filename)))
cv2.moveWindow('experiment', 100, 100)

first_anchor = None
second_anchor = None
box_drawing = False
box = ((-1, -1), (0, 0))   

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
            #cv2.imshow('subimage', subimage)
            #plot_hist_hls(subimage)
            (contours, info_list) = scene.analysis(subimage)
            if info_list:
                print info_list[0][0], info_list[0][2]
                contour_ids = info_list[0][1]
                scene.highlight_contours(subimage, contours, contour_ids)
            first_anchor = None
            second_anchor = None

main_window = 'main'
temp = image.copy()

if debug:
    while True:
        cv2.setMouseCallback(main_window, mouse_callback, image)
        cv2.imshow(main_window, temp)
        if cv2.waitKey(10) == 27:
            cv2.destroyAllWindows()
            break
else:
    info_list = []
    while True:
        cv2.imshow(main_window, image)
        key = cv2.waitKey(10)
        if key == 32:
            if not info_list:
                (contours, info_list) = scene.analysis(image)
            if info_list:
                info = info_list.pop(0)
                contour_ids = info[1]
                print info[0], info[2]
                scene.highlight_contours(image, contours, contour_ids)
        elif key == 27:
            cv2.destroyAllWindows()
            break
