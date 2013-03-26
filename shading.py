import cv2
from plot import *

def feature_detector(graph, card, image, contours):
    card_id = int(card['id'])
    ((h, background_lightness, s), subimage, mask) = plot_intercontour_hist(image, card_id, contours, graph)
    #cv2.imshow('%d-%d: '%(card_id, card_id), subimage)
    #print subimage
    result = []
    for node in card['figures']:
        #print 'node: ', node
        figure_outer_contour_id = int(node)
        figure_inner_contour_id = int(graph.successors(node)[0])
        ((h, contour_lightness, s), subimage, mask) = plot_intercontour_hist(image, figure_outer_contour_id, contours, graph)
        #cv2.imshow('%d-%d: '%(card_id, figure_outer_contour_id), subimage)
        ((h, lightness, s), subimage, mask) = plot_intercontour_hist(image, figure_inner_contour_id, contours, graph)
        #cv2.imshow('%d-%d: '%(card_id, figure_inner_contour_id), subimage)
        h1 = cv2.compareHist(lightness, contour_lightness, 2)
        h2 = cv2.compareHist(lightness, background_lightness, 2)
        p = h1 / (h1 + h2)
        result.append(p)
    #print result
    result = sum(result)/len(result)
    #print result
    lb = 0.30
    ub = 0.93
    if result <= lb:
        shading = 'open'
    elif lb < result <= ub:
        shading = 'striped'
    elif result > ub:
        shading = 'solid'
    return shading
