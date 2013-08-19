import cv2
import filters
from plot import *

DEBUG = False

def normalize_colors(colors):
    # normalize
    summ = sum(colors.values())
    #print colors
    #print summ
    if summ != 0:
        for color in colors: colors[color] /= summ
    else:
        for color in colors: colors[color] = 1.0 / len(colors)
    #print colors
    return colors

def distance_old(a, b):
    result = abs(a - b)
    return result

def distance(hist_a, hist_b):
    params = (1, 0, cv2.NORM_L1)
    cv2.normalize(hist_a, hist_a, *params)
    cv2.normalize(hist_b, hist_b, *params)
    result = 1 - cv2.compareHist(hist_a, hist_b, 2)
    #print result
    return result

def cluster_center_old(cluster, hist):
    accumulator = 0
    for member in cluster:
        #print member
        #print hist[member % L]
        accumulator += member*hist[member % L]
        #print accumulator
    #print accumulator
    subhist = map(lambda x: hist[x % L], cluster)
    #print subhist
    #print sum(subhist)
    center = accumulator / sum(subhist)
    center %= L
    return center

def cluster_center(cluster, hists):
    subhists = map(lambda x: hists[x], cluster)
    center = reduce(lambda x, y: x + y, subhists)
    return center

def roi_old(sequence, c):
    r = 15
    #print 'c: ', c
    band = set([])
    band |= sequence
    for right_cnt in range(1, (c + r) // L + 1):
        subsequence = set(map(lambda x: x + right_cnt * L, sequence))
        band |= subsequence
    for left_cnt in range(-1, (c - r) // L - 1, -1):
        subsequence = set(map(lambda x: x + left_cnt * L, sequence))
        band |= subsequence
    #print band
    raw_cluster = set(filter(lambda x: distance(x, c) < r, band))
    return raw_cluster

def forel_old(hist):
    elements = range(len(hist))
    #print elements
    sequence = set(filter(lambda x: int(hist[x]) != 0, elements))
    #print sequence
    clusters = []
    while sequence:
        final = float('infinity')
        #print sequence
        hist_list = map(lambda x: int(hist[x]), sequence)
        maxs = filter(lambda x: int(hist[x]) == max(hist_list), sequence)
        i = maxs[0]
        initial = i
        raw_cluster = set([i])
        while initial != final:
            #print 'raw: ', raw_cluster
            initial = cluster_center(raw_cluster, hist)
            #print 'initial:', initial
            raw_cluster = roi(sequence, initial)
            #print 'raw: ', raw_cluster
            final = cluster_center(raw_cluster, hist)
            cluster = set(map(lambda x: x % L, raw_cluster))
            #print cluster
            #print 'final:', final
        #print cluster
        sequence -= cluster
        clusters.append((cluster, hist))
    #print clusters
    return clusters

def forel(figures):
    r = 0.65
    sequence = set(range(len(figures)))
    #print sequence
    #print figures
    hists = map(lambda x: x['inner']['hue'], figures)
    clusters = []
    while sequence:
        #print 'seq: ', sequence
        sequence_list = list(sequence)
        initial = hists[sequence_list[0]]
        final = hists[sequence_list[-1]]
        cluster = set([sequence_list[0]])
        while distance(initial, final) > 1e-7:
            #print 'cluster: ', cluster
            initial = cluster_center(cluster, hists)
            #print 'initial:', initial
            cluster = set(filter(lambda x: distance(hists[x], initial) < r, sequence))
            final = cluster_center(cluster, hists)
            #print cluster
            #print 'final:', final
        #print cluster
        sequence -= cluster
        clusters.append((cluster, final))
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

def feature_detector(cards, image, contours, graph):
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
        #plot_hist_hls(subimage, None, str(outer_contour_id) + '-' + 'o')
        figures_list = card['figures']
        for figure_id in figures_list:
            figure = {'id': figure_id, 'border': {}, 'inner': {}}
            #step no.2
            outer_contour_id = int(figure_id)
            ((h, l, s), subimage, mask) = plot_intercontour_hist(image, outer_contour_id, contours, graph)
            if DEBUG: cv2.imshow(str(outer_contour_id), subimage)
            figure['border']['hue'] = h
            figure['border']['lightness'] = l
            figure['border']['saturation'] = s
            ((h, l, s), subimage, mask, inverted_mask) = plot_inner_hist(image, outer_contour_id, contours)
            image_name = str(outer_contour_id)
            #cv2.imshow(image_name, subimage)
            #plot_hist_hls(subimage, None, str(outer_contour_id) + '-' + 'b')
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
            inverted_mask = cv2.bitwise_not(figure_mask)
            #cv2.imshow(image_name + '(u)', subimage)
            #plot_hist_hls(subimage, None, str(outer_contour_id) + '-' + 'u')
            #cv.Set(cv.fromarray(subimage), (0, 0, 0), cv.fromarray(inverted_mask))
            #cv2.imshow(image_name + '(full)', subimage)
            #plot_hist_hls(subimage, None, str(outer_contour_id) + '-' + 'p')
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
    #hists = map(lambda x: x['inner']['hue'], figures)
    #common_hist = reduce(lambda x, y: x + y, hists)
    #print 'common_hist: ', common_hist
    #for i, value in enumerate(common_hist): print i, value
    #clusters = forel(common_hist)
    clusters = forel(figures)
    #elements = range(len(common_hist))
    #step no.6
    color_list = range(len(clusters))
    color_hists = []
    #c = 0
    #plot_selected_hist(common_hist, str(c))
    for cluster, hist in clusters:
        #hist = map(lambda x: common_hist[x] if x in cluster else 0, elements)
        print cluster
        #hist = np.array(map(lambda x: np.array(x, dtype = np.float32, ndmin = 1), hist))
        #print hist
        params = (1, 0, cv2.NORM_INF)
        cv2.normalize(hist, hist, *params)
        #print hist
        color_hists.append(hist)
        #c += 1        
        #plot_selected_hist(hist, str(c))
    for figure in figures:
        hist = figure['inner']['hue']
        params = (1, 0, cv2.NORM_INF)
        cv2.normalize(hist, hist, *params)
        #plot_selected_hist(hist, 'fig: ' + figure['id'])
        colors = {}
        for color in color_list:
            #print hist
            metric = 1 - distance(color_hists[color], hist)
            #print 'color: ', color
            #print 'metric: ', metric
            #metrics.append(metric)
            colors[color] = metric
        #print colors
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
        card['description']['veracity'] *= max(ccv)
        #print card['description']['veracity']
    return cards
