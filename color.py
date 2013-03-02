import cv2
import number
from plot import *

def normalize_colors(colors):
    # normalize
    summ = sum(colors.values())
    print colors
    print summ
    if summ != 0:
        for color in colors: colors[color] /= summ
    print colors
    return colors

def calculate_colors(metrics, figures, color_list):
    colors = {}
    # cummulative sum
    for color in color_list:
        summ = 0
        for i, figure in enumerate(figures):
            if figure['colors'].has_key(color):
                summ += metrics[i] * figure['colors'][color]
        colors[color] = summ
    return colors

def feature_detector(cards, figure_hues):
    shading_list = ('solid', 'striped', 'open')
    figures = []
    figures_list = []
    for shading in shading_list:
        for card in filter(lambda x: x['description']['shading'] == shading, cards):
            figures_list.extend(card['figures'])
    print figures_list
    # init colors
    color_list = [0]
    if figures_list:
        figure_id = figures_list[0]
        figure = {'id': figure_id, 'colors': {0: 1.0}}
        figures.append(figure)
    # comparing colors
    for i, figure_i in enumerate(figures_list[1:]):
        print 'i: ', figure_i
        figure = {'id': figure_i}
        metrics = [] 
        for figure_j in figures_list[:i + 1]:
            print 'j: ', figure_j      
            metric = 1 - cv2.compareHist(figure_hues[figure_i], figure_hues[figure_j], 3)
            print metric
            metrics.append(metric)
        colors = calculate_colors(metrics, figures[:i + 1], color_list)
        if max(metrics) < 0.30:
            color = len(color_list)
            color_list.append(color)
            colors[color] = 1.0
        colors = normalize_colors(colors)
        figure['colors'] = colors      
        figures.append(figure)
    print figures

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
