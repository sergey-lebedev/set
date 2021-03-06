import cv2
from cvlearn.scene import Scene
from cvlearn import filters
from cvlearn.plot import *

debug = not False

images_dir = './cvlearn/samples'
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

scene = None
first_anchor = None
second_anchor = None
box_drawing = False
box = ((-1, -1), (0, 0))

def draw_box(image, first, second):
    cv2.rectangle(image, first, second, (0, 255, 0))

def mouse_callback(event, x, y, flags, image):
    global first_anchor
    global second_anchor
    global box_drawing
    global temp
    global box
    global scene
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
            if scene: scene.clear()
            scene = Scene(subimage)
            scene.analysis()
            if scene.info:
                scene.highlight_contours()
            first_anchor = None
            second_anchor = None

main_window = 'main'
temp = image.copy()

if debug:
    while True:
        cv2.setMouseCallback(main_window, mouse_callback, image)
        cv2.imshow(main_window, temp)
        if cv2.waitKey(10) & 0xff == 27:
            cv2.destroyAllWindows()
            break
else:
    while True:
        cv2.imshow(main_window, image)
        key = cv2.waitKey(10)
        #print key
        scene = Scene(image)
        if key & 0xff == 32:
            if not scene.info:
                scene.analysis()
            else:
                scene.highlight_contours()
        elif key & 0xff == 27:
            cv2.destroyAllWindows()
            break
