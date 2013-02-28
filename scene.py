import cv
import cv2
import time
import math
import number
import shading
import color
import symbol
from plot import *
from pygraphviz import *

def canny(image):
    result = cv2.Canny(image, 0, 255)  
    cv2.imshow('canny', result)
    return result
    
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

def feature_detector(image, graph, contours):
    cards = find_cards(graph)
    #figure_classifier(cards, graph, contours)
    figure_hues = color.classifier(image, cards, graph, contours)
    recognized_cards = []
    for card in cards:
        (sequence, NUMBER) = number.feature_detector(graph, card['id'])
        SHADING = shading.feature_detector(graph, card['id'], image, contours)
        card['description'] = {}
        card['description']['number'] = NUMBER
        card['description']['shading'] = SHADING
    # second pass for color color detection
    color.feature_detector(cards, figure_hues)
    print cards

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

def analysis(image):
    cards = []
    figures = []
    (contours, hierarchy) = find_all_contours(image)
    graph = get_hierarchy_tree(hierarchy)
    plot_hierarchy_tree(graph)
    draw_all_contours(image, contours)
    feature_detector(image, graph, contours)
    #print cards
    #print figures
