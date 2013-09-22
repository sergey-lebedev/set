import cv
import cv2
import time
import math
import random
import color
import symbol
import filters
import shading
from find import *
from plot import *
from game import set
from pygraphviz import *

DEBUG = False

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

def feature_detector(image, graph, cards, contours):
    recognized_cards = []
    for card in cards:
        NUMBER = min(len(card.figures), set_number)
        card.description['veracity'] = 1
        card.description['number'] = NUMBER
    # second pass for color detection
    #figures = shading.feature_detector(graph, cards, image, contours)
    #shading.classifier(cards, figures)
    figures = symbol.feature_detector(cards, contours)
    symbol.classifier(cards, contours, figures)
    figures = color.feature_detector(cards, image, contours, graph)
    color.classifier(cards)
    #print cards
    return cards

def refining(graph, cards, contours):
    #print cards
    cleaning_figures_list = []
    refined_graph = AGraph(directed=True)
    root = 'root'
    refined_graph.add_node(root)
    for card in cards:
        card_inner_contour_id = card.id
        card_outer_contour_id = graph.predecessors(card_inner_contour_id)[0]
        #print card_outer_contour_id
        refined_graph.add_edge([root, card_outer_contour_id])
        #print card_inner_contour_id
        refined_graph.add_edge([card_outer_contour_id, card_inner_contour_id])
        for figure_outer_contour in card.figures:
            #print figure_outer_contour_id
            pretenders = graph.successors(figure_outer_contour.id)
            #print figure_inner_contour_id
            if pretenders:
                link = map(lambda x: (cv2.contourArea(contours[int(x)]), x), pretenders)
                link.sort(reverse = True)
                figure_inner_contour_id = link[0][1]
                refined_graph.add_edge([card_inner_contour_id, figure_outer_contour.id])
                refined_graph.add_edge([figure_outer_contour.id, figure_inner_contour_id])
            else:
                cleaning_figures_list.append(figure_outer_contour.id)
        while cleaning_figures_list:
            figure_outer_contour_id = cleaning_figures_list.pop(0)
            card_id = cards.index(card)
            #print cards[card_id]['figures']
            card.figures.remove([figure for figure in card.figures if figure.id == figure_outer_contour_id][0])
            #print cards[card_id]['figures']
            #print 'figure cleaned'
    return refined_graph

class Scene():
    def __init__(self, image):
        self.info = None
        self.cards = []
        self.image = image
        self.find_all_contours()
        self.get_hierarchy_tree()

    def find_all_contours(self):
        result = adaptive_threshold(self.image)
        self.contours, self.hierarchy = cv2.findContours(result, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    def get_hierarchy_tree(self):
        self.graph = AGraph(directed=True)
        root = 'root'
        self.graph.add_node(root)
        sequence = self.hierarchy[0]
        for i, node in enumerate(sequence):
            index = str(i)
            (h_next, h_prev, v_next, v_prev) = node
            self.graph.add_node(index)
            if v_prev == -1:
                self.graph.add_edge([root, index])
            else:
                self.graph.add_edge([str(v_prev), index])
        #plot_hierarchy_tree(self.graph, 'raw')

    def two_equal_peaks_finder(self, difference):
        # two equal peaks
        level = None
        position = 2
        sliced = difference[position:]
        if sliced:
            min_value = min(sliced)
            index = sliced.index(min_value)
            level = position + index + 1
        return level

    def find_cards(self, graph):
        (nodes_on_level, difference, figures) = Figures().find(graph)
        # two equal peaks
        level = self.two_equal_peaks_finder(difference)
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
        self.cards = []
        for node in sequence:
            figures_list = []
            for successor in graph.successors(node):
                figures_list.append(Figure(**{'id': successor}))
            card = Card(**{'id': node, 'figures': figures_list})
            self.cards.append(card)
        #print cards

    def veracity(self, cards, ids):
        veracity = 1
        for card_id in ids:
            selected_cards = [card for card in cards if card.id == card_id]
        for card in selected_cards:
            veracity *= card.description['veracity']
        return veracity

    def analysis(self):
        figures = []
        self.find_cards(self.graph)
        if self.cards:
            self.graph = refining(self.graph, self.cards, self.contours)
            if DEBUG: plot_hierarchy_tree(self.graph, 'refined')
            # chromatic adaptation
            #plot_hist_xyz(self.image, image_name='before')
            self.image = filters.chromatic_adaptation(self.image)
            #plot_hist_xyz(self.image, image_name='after')
            # drawing contours
            self.draw_all_contours()
            cards = feature_detector(self.image, self.graph, self.cards, self.contours)
            playing_cards = [card.description for card in cards]
            sets, card_ids = set.search_set(playing_cards)
            #print sets
            #print card_ids
            pairs = zip(sets, card_ids)
            self.info = []
            for s, ids in pairs:
                veracity = veracity(self.cards, ids)
                info.append([veracity, ids, s])
            contour_ids = []
            if card_ids:
                self.info = sorted(self.info, reverse=True)
                for i, elem in enumerate(info):
                    self.info[i][1] = map(lambda x: int(self.cards[x]['id']), elem[1])
            else:
                print 'None'
            for card in self.cards: print card.description

    def draw_all_contours(self):
        copy = self.image.copy()
        color = (255, 255, 255)
        for i, contour in enumerate(self.contours):
            cv2.drawContours(copy, self.contours, i, color, 1)
            rect = cv2.boundingRect(contour)
            (a, b, c, d) = rect
            rectangle = ((a, b), (a + c, b + d), WHITE)
            cv2.putText(copy, str(i), ((a + c), (b + d)), 1, 1, WHITE)
            cv2.rectangle(copy, *rectangle)
        cv2.imshow('result', copy)

    def highlight_contours(self):
        color = (0, 0, 255)
        copy = self.image.copy()
        for index in self.indexes:
            cv2.drawContours(copy, self.contours, index, color, 2)
        cv2.imshow('highlighted', copy)

    def plot(self):
        copy = self.image.copy()
        for card in self.cards:
            card.plot()
        cv2.imshow('scene', copy)

    def colorize(self, number_of_features):
        # HSL colorspace
        colors = []
        L_MAX = 180
        step = L_MAX / number_of_features
        shift = random.randint(0, L_MAX - 1)
        for i in range(number_of_features):
            color = (0, 0, (i*step + shift) % L_MAX)
            colors.append(color)
        return colors
