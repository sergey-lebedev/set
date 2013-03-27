import cv
import cv2
import set
import time
import math
import color
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
    result = cv2.medianBlur(result, 3)
    #result = cv2.equalizeHist(result)
    cv2.imshow('blured', result)
    #result = cv2.inpaint(result, [], 10, cv2.INPAINT_NS)
    adaptive_method = cv2.ADAPTIVE_THRESH_MEAN_C
    threshold_type = cv2.THRESH_BINARY_INV
    block_size = 9
    c = 2
    result = cv2.adaptiveThreshold(result, 255, adaptive_method, threshold_type, block_size, c)
    cv2.imshow('threshold', result)
    return result

def find_all_contours(image):
    result = adaptive_threshold(image)
    contours, hierarchy = cv2.findContours(result, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return contours, hierarchy

def feature_detector(image, graph, cards, contours):
    recognized_cards = []
    for card in cards:
        NUMBER = min(len(card['figures']), set_number)
        SHADING = shading.feature_detector(graph, card, image, contours)
        COLOR = None
        card['description'] = {}
        card['description']['veracity'] = 1
        card['description']['number'] = NUMBER
        card['description']['shading'] = SHADING
    # second pass for color detection
    figure_moments = symbol.feature_detector(cards, contours)
    cards = symbol.classifier(cards, contours, figure_moments)
    figures = color.feature_detector(cards, image, contours, graph)
    cards = color.classifier(cards, figures)
    #print cards
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

def refining(graph, cards, contours):
    #print cards
    cleaning_figures_list = []
    refined_graph = AGraph(directed=True)
    root = 'root'
    refined_graph.add_node(root)
    for card in cards:
        card_inner_contour_id = card['id']
        card_outer_contour_id = graph.predecessors(card_inner_contour_id)[0]
        #print card_outer_contour_id
        refined_graph.add_edge([root, card_outer_contour_id])
        #print card_inner_contour_id
        refined_graph.add_edge([card_outer_contour_id, card_inner_contour_id])
        for figure_outer_contour_id in card['figures']:
            #print figure_outer_contour_id
            pretenders = graph.successors(figure_outer_contour_id)
            #print figure_inner_contour_id
            if pretenders:
                link = map(lambda x: (cv2.contourArea(contours[int(x)]), x), pretenders)
                link.sort(reverse = True)
                figure_inner_contour_id = link[0][1]
                refined_graph.add_edge([card_inner_contour_id, figure_outer_contour_id])
                refined_graph.add_edge([figure_outer_contour_id, figure_inner_contour_id])
            else:
                cleaning_figures_list.append(figure_outer_contour_id)
        while cleaning_figures_list:
            figure_outer_contour_id = cleaning_figures_list.pop(0)
            card_id = cards.index(card)
            #print cards[card_id]['figures']
            cards[card_id]['figures'].remove(figure_outer_contour_id)
            #print cards[card_id]['figures']
            #print 'figure cleaned'
    return refined_graph

def cards_veracity(cards, ids):
    veracity = 1
    for card_id in ids:
        veracity *= cards[card_id]['description']['veracity']
    return veracity    

def analysis(image):
    cards = []
    figures = []
    (contours, hierarchy) = find_all_contours(image)
    graph = get_hierarchy_tree(hierarchy)
    #plot_hierarchy_tree(graph, 'raw')
    cards = find_cards(graph)
    graph = refining(graph, cards, contours)
    plot_hierarchy_tree(graph, 'refined')
    draw_all_contours(image, contours)
    cards = feature_detector(image, graph, cards, contours)
    playing_cards = [card['description'] for card in cards]
    sets, card_ids = set.search_set(playing_cards)
    #print sets
    #print card_ids
    pairs = zip(sets, card_ids)
    info = []
    for s, ids in pairs:
        veracity = cards_veracity(cards, ids)
        info.append([veracity, ids, s])
    contour_ids = [] 
    if card_ids:
        info = sorted(info, reverse=True)
        for i, elem in enumerate(info): 
            info[i][1] = map(lambda x: int(cards[x]['id']), elem[1])
    else:
        print 'None'
    print cards
    #print figures
    return contours, info
