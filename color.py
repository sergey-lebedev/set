import cv2
import number
from plot import *

def feature_detector(cards, figure_hues):
    shading_list = ('solid', 'striped', 'open')
    figures = []
    figures_list = []
    color_list = []
    for shading in shading_list:
        for card in filter(lambda x: x['description']['shading'] == shading, cards):
            figures_list.extend(card['figures'])
    print figures_list
    for i, figure_i in enumerate(figures_list[:-1]):
        print 'i: ', figure_i
        figure = {'id': figure_i, 'colors': []}
        for figure_j in figures_list[i + 1:]:
            print 'j: ', figure_j
            if not color_list:
                color_list.append(len(color_list))
                figure['colors'] = {0 : 1}           
            metric = 1 - cv2.compareHist(figure_hues[figure_i], figure_hues[figure_j], 2)
            print metric 
        figures.append(figure)

def classifier(image, cards, graph, contours):
    hues = []
    figure_hues = {}
    # collecting figures
    for card in cards:
        #print 'card: ', card
        (sequence, dummy) = number.feature_detector(graph, card['id'])
        for node in sequence:
            #print 'node: ', node
            figure_outer_contour_id = int(graph.predecessors(node)[0])
            ((hue, l, s), subimage, mask) = plot_intercontour_hist(image, figure_outer_contour_id, contours, graph)
            hues.append(hue)
            figure_hues[graph.predecessors(node)[0]] = hue
    n = len(hues)
    similarity_matrix = {}
    for i in range(len(hues)):
        for j in range(len(hues[:i + 1])):
            metric = 1 - cv2.compareHist(hues[i], hues[j], 2)
            #print metric
            similarity_matrix[(i, j)] = metric
            similarity_matrix[(j, i)] = metric
    #print similarity_matrix
    plot_heatmap(similarity_matrix, n)
    return figure_hues
