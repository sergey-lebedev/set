import cv
import cv2
import number
from plot import *

def distance(a, b):
    result = abs(a - b)    
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
        measure = distance(element, cluster_center(cluster, values))    
        measures.append(measure)
    #print measures
    summ = sum(measures)
    #print summ
    if summ != 0:
        measures = map(lambda x: 1 - (x / summ), measures)
        summ = sum(measures)
    if summ != 0:
        measures = map(lambda x: x / summ, measures)
    #print measures
    return measures

def normalize_symbols(symbols):
    # normalize
    summ = sum(symbols.values())
    #print symbols
    #print summ
    if summ != 0:
        for symbol in symbols: symbols[symbol] /= summ
    #print symbols
    return symbols

def calculate_symbols(metrics, figures, symbol_list):
    symbols = {}
    # cummulative sum
    for symbol in symbol_list:
        summ = 0
        counter = 0
        for i, figure in enumerate(figures):
            if figure['symbols'].has_key(symbol):
                summ += metrics[i] * figure['symbols'][symbol]
                counter += 1
        symbols[symbol] = summ / counter
    return symbols

def classifier(cards, contours, figure_moments):
    figures = []
    figures_list = []
    metric_type = cv.CV_CONTOURS_MATCH_I2
    max_number = max(map(lambda x: x['description']['number'], cards))
    number_list = range(max_number + 1)
    number_list.reverse()
    for number in number_list: 
        for card in filter(lambda x: x['description']['number'] == number, cards):
            figures_list.extend(card['figures'])
    #print figures_list
    # clustering
    clusters = forel(figures_list, figure_moments)
    # init symbols
    symbol_list = range(len(clusters))
    for figure_id in figures_list:
        figure = {'id': figure_id, 'symbols': {}}
        measures = mocm(figure_moments[figure_id], clusters, figure_moments)
        symbols = {}
        for symbol in symbol_list:
            symbols[symbol] = measures[symbol]
        figure['symbols'] = symbols   
        figures.append(figure)
    #print figures
    # card symbol detector
    for card in cards:
        figure_list = card['figures']
        card_symbols = dict([(i, 0) for i in symbol_list])
        #print card_symbols
        for figure_id in figure_list:
            figure = filter(lambda x: x['id'] == figure_id, figures)[0]
            #print figure
            for symbol in symbol_list:
                if figure['symbols'].has_key(symbol):
                    card_symbols[symbol] += figure['symbols'][symbol]
        card_symbols = normalize_symbols(card_symbols)
        #print card_symbols
        csv = card_symbols.values()
        card_symbol = card_symbols.keys()[csv.index(max(csv))]
        #print card_symbol
        card['description']['symbol'] = card_symbol
        card['description']['veracity'] *= max(csv)  
    return cards

def feature_detector(cards, contours):
    figure_contours = []
    figure_moments = {}
    # collecting figures
    for card in cards:
        #print 'card: ', card
        for figure_id in card['figures']:
            #print 'figure: ', figure
            figure_outer_contour_id = int(figure_id)
            figure_contours.append(figure_outer_contour_id)
            contour = contours[figure_outer_contour_id]
            #moments = cv2.moments(contours[figure_outer_contour_id])
            #moments = cv2.HuMoments(moments)
            #figure_moments[figure_id] = moments
            square = cv2.contourArea(contour)
            rect = cv2.minAreaRect(contour)
            box = cv.BoxPoints(rect)
            box = np.array([[np.int0(point)] for point in box])
            min_rect_square = cv2.contourArea(box)
            figure_moments[figure_id] = (min_rect_square - square) / square
    n = len(figure_contours)
    # adjacency matrix
    similarity_matrix = {}
    metric_type = cv.CV_CONTOURS_MATCH_I2
    for i, ci in enumerate(figure_contours):
        moments = cv2.moments(contours[ci])
        #print moments
        #print cv2.HuMoments(moments)
        for j, cj in enumerate(figure_contours[:i + 1]):
            metric_ij = cv2.matchShapes(contours[ci], contours[cj], metric_type, 0)
            metric_ji = cv2.matchShapes(contours[cj], contours[ci], metric_type, 0)
            metric = 1 - (metric_ij + metric_ji) / 2
            similarity_matrix[(i, j)] = metric
            similarity_matrix[(j, i)] = metric
    #print similarity_matrix
    #plot_heatmap(similarity_matrix, n)
    #print figure_moments
    return figure_moments
