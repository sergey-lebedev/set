import cv
import cv2
from plot import *
import classificator
Classify = classificator.SymbolClassificator()

DEBUG = False

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
            initial = Classify.cluster_center(cluster, values)
            #print 'initial:', initial
            cluster = set(filter(lambda x: Classify.distance(initial, values[x]) < r, sequence))
            final = Classify.cluster_center(cluster, values)
            #print 'final:', final
        #print cluster
        sequence -= cluster
        clusters.append(cluster)
    #print clusters
    return clusters

def feature_detector(cards, contours):
    figure_contours = []
    figure_moments = {}
    # collecting figures
    for card in cards:
        #print 'card: ', card
        for figure in card.figures:
            #print 'figure: ', figure
            figure_outer_contour_id = int(figure.id)
            figure_contours.append(figure_outer_contour_id)
            contour = contours[figure_outer_contour_id]
            #moments = cv2.moments(contours[figure_outer_contour_id])
            #moments = cv2.HuMoments(moments)
            #figure_moments[figure.id] = moments
            square = cv2.contourArea(contour)
            if square != 0:
                rect = cv2.minAreaRect(contour)
                box = cv.BoxPoints(rect)
                box = np.array([[np.int0(point)] for point in box])
                min_rect_square = cv2.contourArea(box)
                figure_moments[figure.id] = (min_rect_square - square) / square
            else:
                figure_moments[figure.id] = 0
    '''
    # adjacency matrix
    n = len(figure_contours)
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
    '''
    #print figure_moments
    return figure_moments

def classifier(cards, contours, figure_moments):
    figures_list = []
    metric_type = cv.CV_CONTOURS_MATCH_I2
    max_number = max(map(lambda x: x.description['number'], cards))
    number_list = range(max_number + 1)
    number_list.reverse()
    for number in number_list:
        for card in filter(lambda x: x.description['number'] == number, cards):
            figures_list.extend(card.figures)
    # clustering
    clusters = forel([figure.id for figure in figures_list], figure_moments)
    #print clusters
    values = figure_moments.values()
    #print values
    centers = map(lambda x: Classify.cluster_center(x, figure_moments), clusters)
    #print centers
    # EM clustering
    n = len(clusters)
    if n > set_number:
        n = set_number
        centers = range(0, set_number)
        centers = map(lambda x: x * (1.0 / (set_number - 1)), centers)
    #print centers
    em = cv2.EM(n)
    em.trainE(np.array(values), np.array(centers))
    # init symbols
    symbol_list = range(n)
    figures = []
    for figure in figures_list:
        if em.isTrained:
            (dummy, emmocm) = em.predict(np.array(figure_moments[figure.id]))
            measures = list(emmocm[0])
        else:
            measures = mocm(figure_moments[figure.id], clusters, figure_moments)
        symbols = {}
        for symbol in symbol_list:
            symbols[symbol] = measures[symbol]
        figure.description['symbols'] = symbols
        figures.append(figure)
    #print figures
    Classify.set_feature(cards, symbol_list)
    return len(symbol_list)
