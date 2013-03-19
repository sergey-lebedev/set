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
    else:
        for color in colors: colors[color] = 1.0 / len(colors)
    #print colors
    return colors

def distance(a, b):
    result = abs(a - b)
    return result

def cluster_center(cluster, hist):
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

def roi(sequence, c):
    r = 25
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

def forel(hist):
    elements = range(len(hist))
    #print elements
    sequence = set(filter(lambda x: hist[x] != 0, elements))
    #print sequence
    clusters = []
    while sequence:
        final = float('infinity')
        #print sequence
        hist_list = map(lambda x: int(hist[x]), sequence)
        maxs = filter(lambda x: hist[x] == max(hist_list), sequence)
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
    '''
    c = 0
    height = 300
    subhist = common_hist[:]
    l1_norm_min = cv.Norm(cv.fromarray(subhist), None, cv2.NORM_L1)
    params = (300, 0, cv2.NORM_L1)
    cv2.normalize(common_hist, subhist, *params)
    subhist = np.int32(np.around(subhist))
    # density of probability calculation
    bins = np.arange(L) #.reshape(256,1)
    pts = np.column_stack((bins, height - subhist))
    hist_image = np.zeros((height, L, 1))
    cv2.polylines(hist_image, [pts], False, (255, 255, 255))
    cv2.imshow('%d hist: '%c, hist_image)   
    ''' 
    for cluster in clusters:
        hist = map(lambda x: common_hist[x] if x in cluster else 0, elements)
        #print hist
        hist = np.array(map(lambda x: np.array(x, dtype = np.float32, ndmin = 1), hist))
        #print hist
        params = (1, 0, cv2.NORM_L1)
        cv2.normalize(hist, hist, *params)
        #print hist
        color_hists.append(hist)
        '''
        c += 1        
        height = 300
        subhist = hist[:]
        l1_norm_min = cv.Norm(cv.fromarray(subhist), None, cv2.NORM_L1)
        params = (300, 0, cv2.NORM_L1)
        cv2.normalize(hist, subhist, *params)
        subhist = np.int32(np.around(subhist))
        # density of probability calculation
        bins = np.arange(L) #.reshape(256,1)
        pts = np.column_stack((bins, height - subhist))
        hist_image = np.zeros((height, L, 1))
        cv2.polylines(hist_image, [pts], False, (255, 255, 255))
        cv2.imshow('%d hist: '%c, hist_image)
        '''   
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
