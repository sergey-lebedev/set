import cv
import cv2
import set
import time
import math
import color
import number
import symbol
import shading
from plot import *
from find import *
from pygraphviz import *

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
    figure_hues = color.feature_detector(image, cards, graph, contours)
    recognized_cards = []
    for card in cards:
        (sequence, NUMBER) = number.feature_detector(graph, card['id'])
        SHADING = shading.feature_detector(graph, card['id'], image, contours)
        COLOR = None
        card['description'] = {}
        card['description']['number'] = NUMBER
        card['description']['shading'] = SHADING
        card['description']['symbol'] = None
    # second pass for color color detection
    cards = color.classifier(cards, figure_hues)
    print cards
    return cards

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
    cards = feature_detector(image, graph, contours)
    playing_cards = [card['description'] for card in cards]
    sets, card_ids = set.search_set(playing_cards)
    print sets
    if card_ids:
        contour_ids = map(lambda x: int(cards[x]['id']), card_ids[0])
        highlight_contours(image, contours, contour_ids)
    else:
        print 'None'
    #print cards
    #print figures