import cv
import cv2
import time
import math
from plot import *
from pygraphviz import *

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
    
def find_cards(graph):
    (nodes_on_level, difference, figures) = find_figures(graph)
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
    #print cards
    #print sequence
    cards = []
    for node in sequence:
        card = {'id': node, 'figures': graph.successors(node)}
        cards.append(card)
    #print cards
    return cards

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

def color_classifier(image, cards, graph, contours):
    hues = []
    figure_hues = {}
    # collecting figures
    for card in cards:
        #print 'card: ', card
        (sequence, number) = number_feature_detector(graph, card['id'])
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

def feature_detector(image, graph, contours):
    cards = find_cards(graph)
    #figure_classifier(cards, graph, contours)
    figure_hues = color_classifier(image, cards, graph, contours)
    recognized_cards = []
    for card in cards:
        (sequence, number) = number_feature_detector(graph, card['id'])
        shading = shading_feature_detector(graph, card['id'], image, contours)
        card['description'] = {}
        card['description']['number'] = number
        card['description']['shading'] = shading
    # second pass for color color detection
    color_feature_detector(cards, figure_hues)
    print cards

def number_feature_detector(graph, card):
    steps = 2
    #print card
    sequence = [card]
    #print sequence
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
    #print '%d figure(s) on card'%len(sequence)
    return sequence, len(sequence)
    
def symbol_feature_detector():
    pass

def color_feature_detector(cards, figure_hues):
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

def shading_feature_detector(graph, card, image, contours):
    card_id = int(card)
    ((h, background_lightness, s), subimage, mask) = plot_intercontour_hist(image, card_id, contours, graph)
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
        ((h, contour_lightness, s), subimage, mask) = plot_intercontour_hist(image, figure_outer_contour_id, contours, graph)
        cv2.imshow('%d-%d: '%(int(card), figure_outer_contour_id), subimage)
        ((h, lightness, s), subimage, mask) = plot_intercontour_hist(image, figure_inner_contour_id, contours, graph)
        cv2.imshow('%d-%d: '%(int(card), figure_inner_contour_id), subimage)
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

def find_figures(graph):
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
    figures = []
    return nodes_on_level, difference, figures

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

def find_all_contours(image):
    result = adaptive_threshold(image)
    contours, hierarchy = cv2.findContours(result, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return contours, hierarchy

def scene_analysis(image):
    cards = []
    figures = []
    (contours, hierarchy) = find_all_contours(image)
    graph = get_hierarchy_tree(hierarchy)
    plot_hierarchy_tree(graph)
    draw_all_contours(image, contours)
    feature_detector(image, graph, contours)
    #print cards
    #print figures
