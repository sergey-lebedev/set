import cv
import cv2
import number
from plot import *

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
        for i, figure in enumerate(figures):
            if figure['symbols'].has_key(symbol):
                summ += metrics[i] * figure['symbols'][symbol]
        symbols[symbol] = summ
    return symbols

def classifier(cards, contours):
    figures = []
    figures_list = []
    metric_type = cv.CV_CONTOURS_MATCH_I2
    max_number = max(map(lambda x: x['description']['number'], cards))
    number_list = range(max_number + 1)
    number_list.reverse()
    for number in number_list: 
        for card in filter(lambda x: x['description']['number'] == number, cards):
            figures_list.extend(card['figures'])
    print figures_list
    #print figures_list
    # init symbols
    symbol_list = [0]
    if figures_list:
        figure_id = figures_list[0]
        figure = {'id': figure_id, 'symbols': {0: 1.0}}
        figures.append(figure)
    # comparing symbols
    for i, figure_i in enumerate(figures_list[1:]):
        print 'i: ', figure_i
        figure = {'id': figure_i}
        metrics = [] 
        for figure_j in figures_list[:i + 1]:
            print 'j: ', figure_j      
            metric = 1 - cv2.matchShapes(contours[int(figure_i)], contours[int(figure_j)], metric_type, 0)
            print metric
            metrics.append(metric)
        symbols = calculate_symbols(metrics, figures[:i + 1], symbol_list)
        if max(metrics) < 0.66:
            symbol = len(symbol_list)
            symbol_list.append(symbol)
            symbols[symbol] = 1.0
        print symbols
        symbols = normalize_symbols(symbols)
        figure['symbols'] = symbols   
        figures.append(figure)
    print figures
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
    return cards

def feature_detector(cards, graph, contours):
    figure_contours = []
    figure_moments = {}
    # collecting figures
    for card in cards:
        #print 'card: ', card
        for figure_id in card['figures']:
            #print 'figure: ', figure
            figure_outer_contour_id = int(figure_id)
            figure_contours.append(figure_outer_contour_id)
            moments = cv2.moments(contours[figure_outer_contour_id])
            moments = cv2.HuMoments(moments)
            figure_moments[figure_id] = moments
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
    print figure_moments
    return figure_moments
