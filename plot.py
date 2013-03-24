import cv
import cv2
import math
import numpy as np

L = 181
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
screen_width = 1280
screen_height = 700

def get_subimage(image, first_anchor, second_anchor):
    (fax, fay) = first_anchor
    (sax, say) = second_anchor
    width = abs(fax - sax) + 1
    height = abs(fay - say) + 1
    center = ((fax + sax) / 2.0, (fay + say) / 2.0)
    subimage = cv2.getRectSubPix(image, (width, height), center)
    return subimage

def plot_selected_hist(hist, image_name=''):
    height = 300
    l1_norm_min = cv.Norm(cv.fromarray(hist), None, cv2.NORM_L1)
    params = (300, 0, cv2.NORM_INF)
    cv2.normalize(hist, hist, *params)
    hist = np.int32(np.around(hist))
    # density of probability calculation
    bins = np.arange(L) #.reshape(256,1)
    pts = np.column_stack((bins, height - hist))
    hist_image = np.zeros((height, L, 1))
    cv2.polylines(hist_image, [pts], False, (255, 255, 255))
    cv2.imshow('%s'%image_name, hist_image)       

def plot_hist_hls(image, mask=None, image_name='', normalized=True):
    converted_image = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
    (hue, lightness, saturation) = cv2.split(converted_image)
    counts = (L, 256, 256)
    #components = {'h': hue, 's': saturation, 'l': lightness}
    components = {}
    for name in components:
        cv2.imshow(image_name + ' ' + name, components[name])
    subhists = []
    for i, slice in enumerate((hue, lightness, saturation)):
        subhist = cv2.calcHist([slice], [0], mask, [counts[i]], [0, counts[i] - 1])
        if normalized:
            params = (1, 0, cv2.NORM_L1)
            cv2.normalize(subhist, subhist, *params)
        subhists.append(subhist)
    #plot_selected_hist(subhists[0], image_name)    
    return subhists

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
    color_rectangle = plot_color_rectangle(image, mask)
    #cv.ShowImage('%s color triangle: '%image_name, color_rectangle)
    return subhists

def plot_hierarchy_tree(graph, image_name='graph'):
    format = 'png'
    filename = '.'.join([image_name, format])
    graph.draw(path=filename, format=format, prog='dot')
    graph_image = cv2.imread(filename)
    (width, height) = cv.GetSize(cv.fromarray(graph_image))
    scale_factor = min(screen_width/float(width), screen_height/float(height))
    scale_factor = min(1, scale_factor)
    resized_graph = cv2.resize(graph_image, (0, 0), fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LANCZOS4)
    cv2.imshow(image_name, resized_graph)

def plot_heatmap(similarity_matrix, n):
    if n != 0: 
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

def plot_color_rectangle(image, mask):
    a = screen_height
    width = 180
    height = 256
    #print (width, height)
    color_rectangle = cv.CreateImage((width, height), cv.IPL_DEPTH_8U, 3)    
    (image_width, image_height) = cv.GetSize(cv.fromarray(image))
    #print (image_width, image_height)
    rectangle = (((0, 0), (width, 0), (width, height), (0, height)), BLACK)
    cv.FillConvexPoly(color_rectangle, *rectangle)
    converted_image = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
    for i in range(image_height):
        for j in range(image_width):
            if mask == None or mask[i][j]:
                color = image[i][j]
                hls = converted_image[i][j]
                #print color
                (h, l, s) = hls
                hls = (h, l, s)
                #print hls
                x = int(h)
                y = int(l)
                color = cv.Scalar(*color)
                rectangle = (((x, y), (x, y), (x, y), (x, y)), color)
                cv.FillConvexPoly(color_rectangle, *rectangle)
    #x = (a - 1) / 2
    #y = (a - 1) / 2
    #white_dot = (x, y) 
    #rectangle = ((white_dot, white_dot, white_dot, white_dot), WHITE)
    cv.FillConvexPoly(color_rectangle, *rectangle)
    return color_rectangle

def plot_inner_hist(image, outer_contour_id, contours):
    outer_contour = contours[outer_contour_id]
    (x, y, width, height) = cv2.boundingRect(outer_contour)
    subimage = get_subimage(image, (x, y), (x + width, y + height))
    monochrome = cv2.cvtColor(subimage, cv2.COLOR_BGR2GRAY)
    mask = cv2.compare(monochrome, monochrome, cv2.CMP_EQ)
    inverted_mask = mask.copy()
    for i in range(width):
        for j in range(height):
            point = (x + i, y + j)
            outer_contour_test = cv2.pointPolygonTest(outer_contour, point, 0)
            if outer_contour_test > 0:
                inverted_mask[j][i] = 0
            else:
                mask[j][i] = 0
    cv.Set(cv.fromarray(subimage), (0, 0, 0), cv.fromarray(inverted_mask))
    image_name = '%d'%(outer_contour_id)
    #cv2.imshow(image_name, subimage) 
    #subhists = plot_hist(subimage, mask, image_name)
    subhists = plot_hist_hls(subimage, mask, image_name)
    return subhists, subimage, mask, inverted_mask

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
    subhists = plot_hist_hls(subimage, mask, image_name)
    return subhists, subimage, mask

def draw_box(image, first, second):
    cv2.rectangle(image, first, second, (0, 255, 0))

def draw_all_contours(image, contours):
    copy = image.copy()
    color = (255, 255, 255)
    for i, contour in enumerate(contours):
        cv2.drawContours(copy, contours, i, color, 1)
        rect = cv2.boundingRect(contour)
        (a, b, c, d) = rect
        rectangle = ((a, b), (a + c, b + d), WHITE)
        cv2.putText(copy, str(i), ((a + c), (b + d)), 1, 1, WHITE)
        cv2.rectangle(copy, *rectangle)
    cv2.imshow('result', copy)
    return copy

def plot_figures_hist(contours, hierarchy, image):
    (graph, nodes_on_level, difference) = find_figures(hierarchy)
    # two equal peaks
    level = two_equal_peaks_finder(difference)
    if level:
        # intercontour gap
        subimage, mask = intercontour_gap_processing(image, contours, graph, nodes_on_level, level)
    return subimage, mask

def highlight_contours(image, contours, indexes):
    copy = image.copy()
    color = (0, 0, 255)
    for index in indexes: cv2.drawContours(copy, contours, index, color, 2)
    cv2.imshow('highlighted', copy)
