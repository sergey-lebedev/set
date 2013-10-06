"""Operations with colors"""
import cv2
import filters
from plot import *
import classificator
Classify = classificator.ColorClassificator()

DEBUG = False

"""
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
    raw_cluster = set(filter(lambda x: Classify.distance(x, c) < r, band))
    return raw_cluster
"""
"""
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
            initial = Classify.cluster_center(raw_cluster, hist)
            #print 'initial:', initial
            raw_cluster = roi(sequence, initial)
            #print 'raw: ', raw_cluster
            final = Classify.cluster_center(raw_cluster, hist)
            cluster = set(map(lambda x: x % L, raw_cluster))
            #print cluster
            #print 'final:', final
        #print cluster
        sequence -= cluster
        clusters.append((cluster, hist))
    #print clusters
    return clusters
"""
def forel(figures):
    r = 0.65
    sequence = set(range(len(figures)))
    #print sequence
    #print figures
    hists = map(lambda x: x.inner['hue'], figures)
    clusters = []
    while sequence:
        #print 'seq: ', sequence
        sequence_list = list(sequence)
        initial = hists[sequence_list[0]]
        final = hists[sequence_list[-1]]
        cluster = set([sequence_list[0]])
        while Classify.distance(initial, final) > 1e-7:
            #print 'cluster: ', cluster
            initial = Classify.cluster_center(cluster, hists)
            #print 'initial:', initial
            cluster = set(filter(lambda x: Classify.distance(hists[x], initial) < r, sequence))
            final = Classify.cluster_center(cluster, hists)
            #print cluster
            #print 'final:', final
        #print cluster
        sequence -= cluster
        clusters.append((cluster, final))
    #print clusters
    return clusters

def feature_detector(cards, image, contours, graph):
    figures = []
    for card in cards:
        #print card
        # create hist dictionary
        card.hist = {}
        # step no.1
        outer_contour_id = int(card.id)
        ((h, l, s), subimage, mask, x, y, winnames) = plot_intercontour_hist(image, outer_contour_id, contours, graph)
        card.hist['hue'] = h
        card.hist['lightness'] = l
        card.hist['saturation'] = s
        card.winnames.extend(winnames)
        #cv2.imshow(str(outer_contour_id), subimage)
        #plot_hist_hls(subimage, None, str(outer_contour_id) + '-' + 'o')
        for figure in card.figures:
            #step no.2
            outer_contour_id = int(figure.id)
            ((h, l, s), subimage, mask, x, y, winnames) = plot_intercontour_hist(image, outer_contour_id, contours, graph)
            if DEBUG: cv2.imshow(str(outer_contour_id), subimage)
            figure.border['hue'] = h
            figure.border['lightness'] = l
            figure.border['saturation'] = s
            figure.description['offset_x'] = x
            figure.description['offset_y'] = y
            figure.winnames.extend(winnames)
            ((h, l, s), subimage, mask, inverted_mask, winnames) = \
                        plot_inner_hist(image, outer_contour_id, contours)
            figure.winnames.extend(winnames)
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
                        #print 'card_lightness: ', card.hist['lightness'][value]
                        #print 'figure_lightness: ',figure['border']['lightness'][value]
                        if card.hist['lightness'][value] > figure.border['lightness'][value]:
                            figure_mask[j][i] = 0
            inverted_mask = cv2.bitwise_not(figure_mask)
            #cv2.imshow(image_name + '(u)', subimage)
            #plot_hist_hls(subimage, None, str(outer_contour_id) + '-' + 'u')
            #cv.Set(cv.fromarray(subimage), (0, 0, 0), cv.fromarray(inverted_mask))
            #cv2.imshow(image_name + '(full)', subimage)
            #plot_hist_hls(subimage, None, str(outer_contour_id) + '-' + 'p')
            #step no.4
            ((h, l, s), winnames) = \
                        plot_hist_hls(subimage, figure_mask, \
                                      image_name, normalized=False)
            figure.inner['hue'] = h
            figure.inner['lightness'] = l
            figure.inner['saturation'] = s
            figure.description['mask'] = figure_mask
            figure.winnames.extend(winnames)
            #print 'allwinnames: ', allwinnames
            #figures.append(figure)
        # clear hist dictionary
        card.hist = {}
    return figures

def classifier(cards):
    #step no.5
    #cluster hist
    #hists = map(lambda x: x['inner']['hue'], figures)
    #common_hist = reduce(lambda x, y: x + y, hists)
    #print 'common_hist: ', common_hist
    #for i, value in enumerate(common_hist): print i, value
    #clusters = forel(common_hist)
    figures = []
    for card in cards:
        figures.extend(card.figures)
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
        hist = figure.inner['hue']
        params = (1, 0, cv2.NORM_INF)
        cv2.normalize(hist, hist, *params)
        #plot_selected_hist(hist, 'fig: ' + figure['id'])
        colors = {}
        for color in color_list:
            #print hist
            metric = 1 - Classify.distance(color_hists[color], hist)
            #print 'color: ', color
            #print 'metric: ', metric
            #metrics.append(metric)
            colors[color] = metric
        #print colors
        #colors = normalize_colors(colors)
        #print colors
        figure.description['colors'] = colors
    #print figures
    # card color detector
    Classify.set_feature(cards, color_list)
    return len(color_list)
