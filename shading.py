import cv2
from plot import *

def feature_detector(graph, card, image, contours):
    card_id = int(card)
    ((h, background_lightness, s), subimage, mask) = plot_intercontour_hist(image, card_id, contours, graph)
    #cv2.imshow('%d-%d: '%(int(card), int(card)), subimage)
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
        ((h, contour_lightness, s), subimage, mask) = plot_intercontour_hist(image, figure_outer_contour_id, contours, graph)
        #cv2.imshow('%d-%d: '%(int(card), figure_outer_contour_id), subimage)
        ((h, lightness, s), subimage, mask) = plot_intercontour_hist(image, figure_inner_contour_id, contours, graph)
        #cv2.imshow('%d-%d: '%(int(card), figure_inner_contour_id), subimage)
        h1 = cv2.compareHist(lightness, contour_lightness, 2)
        h2 = cv2.compareHist(lightness, background_lightness, 2)
        p = h1 / (h1 + h2)
        result.append(p)
    result = sum(result)/len(result)
    #print result
    lb = 0.30
    ub = 0.77
    if result <= lb:
        shading = 'open'
    elif lb < result <= ub:
        shading = 'striped'
    elif result > ub:
        shading = 'solid'
    return shading
