import cv
import cv2
import time
import math
import numpy as np
from pygraphviz import *

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
screen_width = 1280
screen_height = 700

images_dir = './samples'
##filename = 'Webcam-1355581255.png'
filename = 'Webcam-1355052953.png'
##filename = 'Webcam-1356160723.png'
#filename = 'Webcam-1355053113.png'
##filename = 'Webcam-1356180412.png'
##filename = 'Webcam-1355052975.png'
##filename = 'Webcam-1356180892.png'
image = cv2.imread('/'.join((images_dir, filename)))
cv2.moveWindow('experiment', 100, 100)

first_anchor = None
second_anchor = None
box_drawing = False
box = ((-1, -1), (0, 0))

def plot_lightness_hist(image, mask=None, image_name=''):
    bins = np.arange(256)
    height = 300
    hist_image = np.zeros((height, 256, 1))
    converted_image = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
    (hue, lightness, saturation) = cv2.split(converted_image)
    cv2.imshow(image_name, lightness)
    subhist = cv2.calcHist([lightness], [0], mask, [256], [0, 255])
    #print subhist
    params = (1, 0, cv2.NORM_L1)
    cv2.normalize(subhist, subhist, *params)
    #subhist = np.int32(np.around(subhist))
    # density of probability calculation
    #pts = np.column_stack((bins, height - subhist))
    #cv2.polylines(hist_image, [pts], False, 255)
    #cv2.imshow('%s hist: '%image_name, hist_image)
    #print subhist
    return subhist

def plot_hist(image, mask=None, image_name=''):
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
        subhist = cv2.calcHist([slice], [0], mask, [256], [0, 255])
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
        # density of probability calculation
        subhists[i] = map(lambda x: float(x)/l1_norm_min, subhist)
        pts = np.column_stack((bins, height - subhist))
        cv2.polylines(hist_image, [pts], False, color_dict[color])
    #cv2.imshow('%s hist: '%image_name, hist_image)
    #color_triangle = plot_color_triangle(image, mask)
    #cv.ShowImage('%s color triangle: '%image_name, color_triangle)
    return subhists

def adaptive_threshold(image):
    result = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    result = cv2.medianBlur(result, 5)
    #result = cv2.equalizeHist(result)
    cv2.imshow('blured', result)
    #result = cv2.inpaint(result, [], 10, cv2.INPAINT_NS)
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

def get_hierarchy_tree(hierarchy):
    graph = AGraph(directed=True)
    root = 'root'
    graph.add_node(root)
    sequence = hierarchy[0]
    for i, node in enumerate(sequence):
        index = str(i)
        (h_next, h_prev, v_next, v_prev) = node
        graph.add_node(index)
        if v_prev == -1:
            graph.add_edge([root, index])
        else:
            graph.add_edge([str(v_prev), index])
    return graph

def plot_hierarchy_tree(graph):
    filename = 'graph.png'
    graph.draw(path=filename, format='png', prog='dot')
    graph_image = cv2.imread(filename)
    (width, height) = cv.GetSize(cv.fromarray(graph_image))
    scale_factor = min(screen_width/float(width), screen_height/float(height))
    scale_factor = min(1, scale_factor)
    resized_graph = cv2.resize(graph_image, (0, 0), fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LANCZOS4)
    cv2.imshow('graph', resized_graph)
    
def find_cards(hierarchy):
    (graph, nodes_on_level, difference) = find_figures(hierarchy)
    # two equal peaks
    level = two_equal_peaks_finder(difference)
    steps = 2
    sequence = []
    if level: sequence = nodes_on_level[level]
    while steps != 0 and sequence:
        steps -= 1
        parents = []
        for node in sequence:
            parent = graph.predecessors(node)[0]
            if parent not in parents:
                parents.append(parent)
        #print parents
        sequence = parents
    print '%d card(s) detected'%len(sequence)
    return graph, sequence

def plot_heatmap(similarity_matrix, n):
    pixels = max(1, min(screen_width / n, screen_height / n))
    side = n * pixels
    heatmap = cv.CreateImage((side, side), cv.IPL_DEPTH_8U, 1)
    for i in range(n):
        for j in range(n):
            (a, b) = (i * pixels, j * pixels)
            (c, d) = (a + pixels, b + pixels)
            intensity = int((1 - similarity_matrix[(i, j)]) * 255)
            rectangle = (((a, b), (c, b), (c, d), (a, d)), intensity)
            cv.FillConvexPoly(heatmap, *rectangle)
    cv.ShowImage('heatmap', heatmap)

def plot_color_triangle(image, mask):
    a = screen_height
    height = a
    width = int(math.ceil(2 * a / math.sqrt(3)))
    #print (width, height)
    color_triangle = cv.CreateImage((width, height), cv.IPL_DEPTH_8U, 3)    
    (image_width, image_height) = cv.GetSize(cv.fromarray(image))
    #print (image_width, image_height)
    rectangle = (((0, 0), (width, 0), (width, height), (0, height)), BLACK)
    cv.FillConvexPoly(color_triangle, *rectangle)
    for i in range(image_height):
        for j in range(image_width):
            if mask == None or mask[i][j]:
                color = image[i][j]
                #print color
                (B, G, R) = color
                color = (B, G, R)
                #print color
                intensity = float(sum(color))
                if intensity == 0:
                    b = 1.0 / 3.0
                    g = 1.0 / 3.0
                else:
                    b = (B / intensity)
                    g = (G / intensity)
                #print b, g
                x = math.sqrt(3) * (a - 1) * (1 - b) / 2 
                y = (a - 1) * (1 - g)
                x = int(x)
                y = int(y)
                #print x, y
                #print color_triangle[0][0]
                #color_triangle[x][y] = 255
                color = cv.Scalar(*color)
                rectangle = (((x, y), (x, y), (x, y), (x, y)), color)
                cv.FillConvexPoly(color_triangle, *rectangle)
    x = (a - 1) / math.sqrt(3)
    y = 2 * (a - 1) / 3.0
    white_dot = (x, y) 
    rectangle = ((white_dot, white_dot, white_dot, white_dot), WHITE)
    cv.FillConvexPoly(color_triangle, *rectangle)
    return color_triangle 

def figure_classifier(hierarchy, contours):
    (graph, cards) = find_cards(hierarchy)
    figure_contours = []
    # collecting figures
    for card in cards:
        (sequence, number) = number_feature_detector(graph, card)
        for node in sequence:
            figure_outer_contour_id = int(graph.predecessors(node)[0])
            figure_contours.append(figure_outer_contour_id)
    n = len(figure_contours)
    # adjacency matrix
    similarity_matrix = {}
    metric_type = cv.CV_CONTOURS_MATCH_I2
    for i, ci in enumerate(figure_contours):
        for j, cj in enumerate(figure_contours[:i + 1]):
            metric_ij = cv2.matchShapes(contours[ci], contours[cj], metric_type, 0)
            metric_ji = cv2.matchShapes(contours[ci], contours[cj], metric_type, 0)
            metric = 1 - (metric_ij + metric_ji) / 2
            similarity_matrix[(i, j)] = metric
            similarity_matrix[(j, i)] = metric
    #print similarity_matrix
    plot_heatmap(similarity_matrix, n)

def color_classifier(image, hierarchy, contours):
    (graph, cards) = find_cards(hierarchy)
    figure_contours = []
    # collecting figures
    for card in cards:
        #print 'card: ', card
        (sequence, number) = number_feature_detector(graph, card)
        for node in sequence:
            #print 'node: ', node
            figure_outer_contour_id = int(graph.predecessors(node)[0])
            figure_contours.append(figure_outer_contour_id)
            (subhists, subimage, mask) = plot_intercontour_hist(image, figure_outer_contour_id, contours, graph)
            #cv2.imshow('%d-%d: '%(int(card), int(node)), subimage) 
    n = len(figure_contours)

def feature_detector(image, hierarchy, contours):
    (graph, cards) = find_cards(hierarchy)
    figure_classifier(hierarchy, contours)
    #color_classifier(image, hierarchy, contours)
    recognized_cards = []
    for card in cards:
        recognized_card = {}
        (sequence, number) = number_feature_detector(graph, card)
        shading = shading_feature_detector(graph, card, image, contours)
        recognized_card['number'] = number
        recognized_card['shading'] = shading
        recognized_cards.append(recognized_card)
    print recognized_cards

def number_feature_detector(graph, card):
    steps = 2
    #print card
    sequence = [card]
    while steps != 0 and sequence:
        steps -= 1
        childrens = []
        for node in sequence:
            #print node
            child = graph.successors(node)
            if child not in childrens:
                childrens.extend(child)
        sequence = childrens
        #print childrens
    print '%d figure(s) on card'%len(sequence)
    return sequence, len(sequence)
    
def symbol_feature_detector():
    pass

def color_feature_detector():
    pass

def shading_feature_detector(graph, card, image, contours):
    card_id = int(card)
    (background_subhists, subimage, mask) = plot_intercontour_hist(image, card_id, contours, graph)
    cv2.imshow('%d-%d: '%(int(card), int(card)), subimage)
    #print subimage_hsv
    steps = 2
    #print card
    sequence = [card]
    while steps != 0 and sequence:
        steps -= 1
        childrens = []
        for node in sequence:
            #print node
            child = graph.successors(node)
            if child not in childrens:
                childrens.extend(child)
        sequence = childrens
        #print childrens
    result = []
    for node in sequence:
        #print 'node: ', node
        figure_outer_contour_id = int(graph.predecessors(node)[0])
        figure_inner_contour_id = int(node)
        (contour_subhists, subimage, mask) = plot_intercontour_hist(image, figure_outer_contour_id, contours, graph)
        cv2.imshow('%d-%d: '%(int(card), figure_outer_contour_id), subimage)
        (subhists, subimage, mask) = plot_intercontour_hist(image, figure_inner_contour_id, contours, graph)
        cv2.imshow('%d-%d: '%(int(card), figure_inner_contour_id), subimage)
        (width, height) = cv.GetSize(cv.fromarray(mask))
        # conversion to HSV
        subimage_hsv = cv2.cvtColor(subimage, cv2.COLOR_BGR2HLS)
        for i in range(height):
            for j in range(width):
                if mask == None or mask[i][j]:
                    (hue, lightness, saturation) = subimage_hsv[i][j]
                    #print 'lightness: ', lightness
                    #print 'contour_subhists[lightness]: ', contour_subhists[lightness]
                    #print 'background_subhists[lightness]: ', background_subhists[lightness]
                    '''
                    point_vector = subimage[i][j]
                    p = range(len(point_vector))
                    for k, component in enumerate(point_vector):
                        h1 = contour_subhists[k][component]
                        h2 = background_subhists[k][component]
                        if h1 == h2:
                            p[k] = 0.5
                        else:
                            p[k] = h1 / (h1 + h2)
                    #p = sum(p)/len(p)
                    prod = 1
                    for elem in p:
                        prod *= elem
                    p = prod
                    #p = pow(p, 1/3.0)
                    '''
                    h1 = contour_subhists[lightness]
                    h2 = background_subhists[lightness]
                    if h1 == h2:
                        p = 0.5
                    else:
                        p = h1 / (h1 + h2)
                    #print p
                    #result.extend(p)
                    result.append(p)
    #result.sort()
    #print result
    #print len(result)
    #print len(result)/2
    #result = result[len(result)/2]
    result = sum(result)/len(result)
    print cv2.compareHist(subhists, contour_subhists, 2)
    print cv2.compareHist(subhists, background_subhists, 2)
    print result
    lb = 0.08
    ub = 0.45
    if result <= lb:
        shading = 'open'
    elif lb < result <= ub:
        shading = 'striped'
    elif result > ub:
        shading = 'solid'
    return shading

def find_figures(hierarchy):
    graph = get_hierarchy_tree(hierarchy)
    root = 'root'
    queue = [root]
    nodes_on_level = []
    while queue:
        sequence = []
        for node in queue:
            sequence.extend(graph.successors(node))
        nodes_on_level.append(sequence)
        queue = sequence
    #print nodes_on_level
    difference = []
    for i in range(len(nodes_on_level) - 2):
        (left, right) = (len(nodes_on_level[i]), len(nodes_on_level[i+1]))
        difference.append(abs(left - right))
    return graph, nodes_on_level, difference

def plot_intercontour_hist(image, outer_contour_id, contours, graph):
    outer_contour = contours[outer_contour_id]
    (x, y, width, height) = cv2.boundingRect(outer_contour)
    subimage = get_subimage(image, (x, y), (x + width, y + height))
    monochrome = cv2.cvtColor(subimage, cv2.COLOR_BGR2GRAY)
    mask = cv2.compare(monochrome, monochrome, cv2.CMP_EQ)
    inverted_mask = mask.copy()
    inner_contours = [contours[int(contour_id)] for contour_id in graph.successors(outer_contour_id)]
    for i in range(width):
        for j in range(height):
            point = (x + i, y + j)
            outer_contour_test = cv2.pointPolygonTest(outer_contour, point, 0)
            inner_contours_test = -1
            for inner_contour in inner_contours:
                inner_contour_test = cv2.pointPolygonTest(inner_contour, point, 0)
                if inner_contour_test > 0: 
                    inner_contours_test = 1
                    break
            if outer_contour_test > 0 and inner_contours_test < 0:
                inverted_mask[j][i] = 0
            else:
                mask[j][i] = 0
    cv.Set(cv.fromarray(subimage), (0, 0, 0), cv.fromarray(inverted_mask))
    inner_contour_id = str(inner_contours)
    image_name = '%d-%s'%(outer_contour_id, inner_contours)
    #cv2.imshow(image_name, subimage) 
    #subhists = plot_hist(subimage, mask, image_name)
    subhists = plot_lightness_hist(subimage, mask, image_name)
    return subhists, subimage, mask

def two_equal_peaks_finder(difference):
    # two equal peaks
    level = None
    position = 2
    sliced = difference[position:]
    if sliced:
        min_value = min(sliced)
        index = sliced.index(min_value)
        level = position + index + 1
    return level 

def plot_figures_hist(contours, hierarchy, image):
    (graph, nodes_on_level, difference) = find_figures(hierarchy)
    # two equal peaks
    level = two_equal_peaks_finder(difference)
    if level:
        # intercontour gap
        subimage, mask = intercontour_gap_processing(image, contours, graph, nodes_on_level, level)
    return subimage, mask

def draw_all_contours(image):
    copy = image.copy()
    result = adaptive_threshold(copy)
    contours, hierarchy = cv2.findContours(result, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    graph = get_hierarchy_tree(hierarchy)
    plot_hierarchy_tree(graph)
    #plot_figures_hist(contours, hierarchy, image)
    feature_detector(image, hierarchy, contours)
    color = (255, 255, 255)
    for i, contour in enumerate(contours):
        cv2.drawContours(copy, contours, i, color, 1)
        #moments = cv2.moments(contour)
        rect = cv2.boundingRect(contour)
        (a, b, c, d) = rect
        rectangle = ((a, b), (a + c, b + d), WHITE)
        cv2.putText(copy, str(i), ((a + c), (b + d)), 1, 1, WHITE)
        cv2.rectangle(copy, *rectangle)
    return copy

def draw_box(image, first, second):
    cv2.rectangle(image, first, second, (0, 255, 0))

def intercontour_gap_processing(image, contours, graph, nodes_on_level, level):
    # intercontour gap
    for node in nodes_on_level[level]:
        figure_inner_contour_id = int(node)
        figure_outer_contour_id = int(graph.predecessors(node)[0])
        (subhists, subimage, mask) = plot_intercontour_hist(image, figure_outer_contour_id, contours, graph)
    return subimage, mask

def card_processing(image, figure_outer_contour_id, contours, graph):
    # card background
    card_inner_contour_id = int(graph.predecessors(figure_outer_contour_id)[0])
    plot_intercontour_hist(image, card_inner_contour_id, contours, graph)

def cards_recognition():
    return recognized_cards

def interior_processing():
    pass

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
