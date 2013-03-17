import cv2
import number
from plot import *

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

def distance(a, b, L):
    d = abs(a - b)
    if d < L - d:
        marker = False
        result = d
    else:
        marker = True
        result = L - d
    return result, marker

def cluster_center(cluster, hist):
    accumulator = 0
    for member in cluster:
        #print member
        #print hist[member % L]
        accumulator += member*hist[member % L]
        #print accumulator
    #print accumulator
    subhist = map(lambda x: hist[x % L], cluster)
    #print sum(subhist)
    center = accumulator / sum(subhist)
    center %= L
    return center

def roi(sequence, center):
    r = 30
    raw_cluster = set([])
    for element in sequence:
        d, flag = distance(center, element, L)
        if d < r:
            if flag: element += L
            raw_cluster |= set([element])      
    return raw_cluster

def forel(hist):
    elements = range(len(hist))
    #print elements
    sequence = set(filter(lambda x: hist[x] != 0, elements))
    #print sequence
    clusters = []
    while sequence:
        final = float('infinity')
        #print sequence
        i = list(sequence)[0]
        initial = i
        raw_cluster = set([i])
        while initial != final:
            initial = cluster_center(raw_cluster, hist)
            #print 'initial:', initial
            raw_cluster = roi(sequence, initial)
            #print raw_cluster
            final = cluster_center(raw_cluster, hist)
            cluster = set(map(lambda x: x % L, raw_cluster))
            #print cluster
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

def separator(cards, image, contours, graph):
    figures = []
    for card in cards:
        #print card
        # create hist dictionary
        card['hist'] = {}
        # step no.1
        outer_contour_id = int(card['id'])
        ((h, l, s), subimage, mask) = plot_intercontour_hist(image, outer_contour_id, contours, graph)
        card['hist']['hue'] = h
        card['hist']['lightness'] = l
        card['hist']['saturation'] = s
        #cv2.imshow(str(outer_contour_id), subimage)
        figures_list = card['figures']
        for figure_id in figures_list:
            figure = {'id': figure_id, 'border': {}, 'inner': {}}
            #step no.2
            outer_contour_id = int(figure_id)
            ((h, l, s), subimage, mask) = plot_intercontour_hist(image, outer_contour_id, contours, graph)
            #cv2.imshow(str(outer_contour_id), subimage)
            figure['border']['hue'] = h
            figure['border']['lightness'] = l
            figure['border']['saturation'] = s
            ((h, l, s), subimage, mask, inverted_mask) = plot_inner_hist(image, outer_contour_id, contours)
            image_name = str(outer_contour_id)
            #cv2.imshow(image_name, subimage)
            #step no.3
            converted_image = cv2.cvtColor(subimage, cv2.COLOR_BGR2HLS)
            (hue, lightness, saturation) = cv2.split(converted_image)
            (width, height) = cv.GetSize(cv.fromarray(subimage))
            figure_mask = mask.copy()
            #print (width, height)
            for i in range(width):
                for j in range(height):
                    #print 'mask: ', mask[j][i]
                    if mask[j][i] != 0:
                        value = lightness[j][i]
                        #print value
                        #print 'card_lightness: ', card['hist']['lightness'][value]
                        #print 'figure_lightness: ',figure['border']['lightness'][value]    
                        if card['hist']['lightness'][value] > figure['border']['lightness'][value]:
                            figure_mask[j][i] = 0
                            inverted_mask[j][i] = 255
            #cv.Set(cv.fromarray(subimage), (0, 0, 0), cv.fromarray(inverted_mask))
            #cv2.imshow(image_name + '(full)', subimage)
            #step no.4
            (h, l, s) = plot_hist_hls(subimage, figure_mask, image_name, normalized=False)
            figure['inner']['hue'] = h
            figure['inner']['lightness'] = l
            figure['inner']['saturation'] = s            
            figures.append(figure)
        # clear hist dictionary
        card['hist'] = {}
    return figures

def classifier(cards, figures):
    #step no.5
    #cluster hist
    hists = map(lambda x: x['inner']['hue'], figures)
    common_hist = reduce(lambda x, y: x + y, hists)
    #print 'common_hist: ', common_hist
    #for i, value in enumerate(common_hist): print i, value
    clusters = forel(common_hist)
    elements = range(len(common_hist))
    #step no.6
    color_list = range(len(clusters))
    color_hists = []
    for cluster in clusters:
        hist = map(lambda x: common_hist[x] if x in cluster else 0, elements)
        #print hist
        hist = np.array(map(lambda x: np.array(x, dtype = np.float32, ndmin = 1), hist))
        #print hist
        params = (1, 0, cv2.NORM_L1)
        cv2.normalize(hist, hist, *params)
        #print hist
        color_hists.append(hist)
    for figure in figures:
        hist =  figure['inner']['hue']
        params = (1, 0, cv2.NORM_L1)
        cv2.normalize(hist, hist, *params)
        figure['inner']['hue'] = hist
        colors = {}
        for color in color_list:
            #print hist
            metric = 1 - cv2.compareHist(color_hists[color], hist, 3)
            #print 'color: ', color
            #print 'metric: ', metric
            #metrics.append(metric)
            colors[color] = metric
        #print colors
        #colors = calculate_colors(metrics, figures, color_list)
        #colors = normalize_colors(colors)
        #print colors
        figure['colors'] = colors
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

def feature_detector(graph, image, cards, contours):
    figures = separator(cards, image, contours, graph)
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
    #return figure_hues
    return figures
