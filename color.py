import cv2
import number
from plot import *

def distance(a, b, L):
    d = abs(a - b)
    result = min(d, L - d)    
    return result

def cluster_center(cluster, values):
    accumulator = 0
    for member in cluster:
        accumulator += values[member]
    center = accumulator / len(cluster)
    return center

def forel(elements, values):
    #print elements
    #print values
    sequence = set(elements)
    r = 0.10
    clusters = []
    while sequence:
        final = None
        #print sequence
        i = list(sequence)[0]
        cluster = set([i])
        initial = values[i]
        while initial != final:
            initial = cluster_center(cluster, values)
            #print 'initial:', initial
            cluster = set(filter(lambda x: distance(initial, values[x]) < r, sequence))
            final = cluster_center(cluster, values)
            #print 'final:', final
        #print cluster
        sequence -= cluster
        clusters.append(cluster)
    #print clusters
    return clusters

def mocm(element, clusters, values):
    measures = []
    for cluster in clusters:
        measure = distance(element, cluster_center(cluster, values), L)    
        measures.append(measure)
    summ = sum(measures)
    if summ != 0:
        measures = map(lambda x: 1 - (x / summ), measures)
        summ = sum(measures)
        measures = map(lambda x: x / summ, measures)
    return measures

def separator(figures, contours):
    pass

def normalize_colors(colors):
    # normalize
    summ = sum(colors.values())
    #print colors
    #print summ
    if summ != 0:
        for color in colors: colors[color] /= summ
    #print colors
    return colors

def calculate_colors(metrics, figures, color_list):
    colors = {}
    # cummulative sum
    for color in color_list:
        summ = 0
        counter = 0
        for i, figure in enumerate(figures):
            if figure['colors'].has_key(color):
                summ += metrics[i] * figure['colors'][color]
                counter += 1
        colors[color] = summ / counter 
    return colors

def classifier(cards, figure_hues):
    shading_list = ('solid', 'striped', 'open')
    figures = []
    figures_list = []
    for shading in shading_list:
        for card in filter(lambda x: x['description']['shading'] == shading, cards):
            figures_list.extend(card['figures'])
    #print figures_list
    # init colors
    color_list = [0]
    if figures_list:
        figure_id = figures_list[0]
        figure = {'id': figure_id, 'colors': {0: 1.0}}
        figures.append(figure)
    # comparing colors
    for i, figure_i in enumerate(figures_list[1:]):
        #print 'i: ', figure_i
        figure = {'id': figure_i}
        metrics = [] 
        for figure_j in figures_list[:i + 1]:
            #print 'j: ', figure_j      
            metric = 1 - cv2.compareHist(figure_hues[figure_i], figure_hues[figure_j], 3)
            #print metric
            metrics.append(metric)
        colors = calculate_colors(metrics, figures[:i + 1], color_list)
        if max(metrics) < 0.20:
            color = len(color_list)
            color_list.append(color)
            colors[color] = 1.0
        colors = normalize_colors(colors)
        figure['colors'] = colors      
        figures.append(figure)
    #print figures
    # card color detector
    for card in cards:
        figure_list = card['figures']
        card_colors = dict([(i, 0) for i in color_list])
        #print card_colors
        for figure_id in figure_list:
            figure = filter(lambda x: x['id'] == figure_id, figures)[0]
            #print figure
            for color in color_list:
                if figure['colors'].has_key(color):
                   card_colors[color] += figure['colors'][color]     
        card_colors = normalize_colors(card_colors)
        #print card_colors
        ccv = card_colors.values()
        card_color = card_colors.keys()[ccv.index(max(ccv))]
        #print card_color
        card['description']['color'] = card_color    
    return cards

def feature_detector(image, cards, graph, contours):
    hues = []
    figure_hues = {}
    # collecting figures
    for card in cards:
        #print 'card: ', card
        for figure_id in card['figures']:
            #print 'figure: ', figure
            figure_outer_contour_id = int(figure_id)
            ((hue, l, s), subimage, mask) = plot_intercontour_hist(image, figure_outer_contour_id, contours, graph)
            hues.append(hue)
            figure_hues[figure_id] = hue
    n = len(hues)
    similarity_matrix = {}
    for i in range(len(hues)):
        for j in range(len(hues[:i + 1])):
            metric = 1 - cv2.compareHist(hues[i], hues[j], 2)
            #print metric
            similarity_matrix[(i, j)] = metric
            similarity_matrix[(j, i)] = metric
    #print similarity_matrix
    #plot_heatmap(similarity_matrix, n)
    return figure_hues
