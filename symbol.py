import cv
import cv2
from plot import *

def symbol_feature_detector():
    pass

def figure_classifier(cards, graph, contours):
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
        moments = cv2.moments(contours[ci])
        print moments
        print cv2.HuMoments(moments)
        for j, cj in enumerate(figure_contours[:i + 1]):
            metric_ij = cv2.matchShapes(contours[ci], contours[cj], metric_type, 0)
            metric_ji = cv2.matchShapes(contours[cj], contours[ci], metric_type, 0)
            metric = 1 - (metric_ij + metric_ji) / 2
            similarity_matrix[(i, j)] = metric
            similarity_matrix[(j, i)] = metric
    #print similarity_matrix
    plot_heatmap(similarity_matrix, n)
