import cv2
from plot import *
import classificator
Classify = classificator.ShadingClassificator()

DEBUG = False

def mix(hists):
    mixture = []
    for hist in hists:
        for index, value in enumerate(hist):
            #print index, value
            if value[0] != 0:
                extension = map(lambda x: index, range(value[0]))
                #print extension
                mixture.extend(extension)
                #print mixture
    return mixture

def prob(hist, em, cluster_num):
    p = [0.0] * cluster_num
    accum = 0.0
    for index, value in enumerate(hist):
        accum += value[0]
        if value[0] != 0:
            (dummy, emmocm) = em.predict(np.array(index))
            #print emmocm[0]
            for i, mocm in enumerate(list(emmocm[0])):
                #print mocm
                p[i] += float(mocm) * value[0]
            #print p
    #print accum
    if accum != 0:
        p = map(lambda x: x / accum, p)
    else:
        p = range(cluster_num - 1) * (1.0 / cluster_num)
    return p

def feature_detector(graph, cards, image, contours):
    figures = {}
    for card in cards:
        card_id = int(card['id'])
        ((h, background_lightness, s), background_subimage, mask) = plot_intercontour_hist(image, card_id, contours, graph, False)
        image_name = '%d-%d: '%(card_id, card_id)
        #cv2.imshow(image_name, background_subimage)
        if DEBUG: plot_selected_hist(background_lightness, image_name)
        cb0 = Classify.cluster_center(background_lightness)
        #print background_lightness
        #print cb0
        #print background_subimage
        result = []
        for figure_id in card['figures']:
            if DEBUG: print 'figure_id: ', figure_id
            figure_outer_contour_id = int(figure_id)
            figure_inner_contour_id = int(graph.successors(figure_id)[0])
            ((h, contour_lightness, s), contour_subimage, mask) = plot_intercontour_hist(image, figure_outer_contour_id, contours, graph, False)
            image_name = '%d-%d: '%(card_id, figure_outer_contour_id)
            #cv2.imshow(image_name, contour_subimage)
            if DEBUG: plot_selected_hist(contour_lightness, image_name)
            #print contour_lightness
            cc0 = Classify.cluster_center(contour_lightness)
            #print cc0
            ((h, lightness, s), subimage, mask) = plot_intercontour_hist(image, figure_inner_contour_id, contours, graph, False)
            image_name = '%d-%d: '%(card_id, figure_inner_contour_id)
            #cv2.imshow(image_name, subimage)
            if DEBUG: plot_selected_hist(lightness, image_name)
            #print lightness
            centers = [cb0, cc0]
            if DEBUG: print centers
            mixture = mix([background_lightness, contour_lightness])
            #print 'mixture: ', mixture
            CLUSTER_NUM = 2
            em = cv2.EM(CLUSTER_NUM)
            em.trainE(np.array(mixture), np.array(centers))
            #print em.isTrained()
            #print dir(em)
            #print em.getParams()
            #print dir(em.getAlgorithm())
            #print em.getMat('means')
            means = map(lambda x: float(x), em.getMat('means'))

            [cb, cc] = means
            if DEBUG: print means
            #print em.paramHelp('means')
            h1 = cv2.compareHist(lightness, contour_lightness, 2)
            h2 = cv2.compareHist(lightness, background_lightness, 2)
            #print h1, h2
            p = h1 / (h1 + h2)
            if DEBUG: print p
            #p = prob(lightness, em, CLUSTER_NUM)
            ca = Classify.cluster_center(lightness)
            em = cv2.EM(CLUSTER_NUM)
            em.trainE(np.array(mix([lightness])), np.array(means))
            if DEBUG: print em.getMat('means')
            #print em.getMat('covs')
            if DEBUG: print em.getMat('weights')         
            p =  (ca - min(cb, cc)) / abs(cb - cc)
            #(dummy, check) = em.predict(np.array(cb))
            #check = list(check[0])
            #if not check.index(max(check)): p.reverse()
            if DEBUG: print p
            figures[figure_id] = {'shading': p}
    '''
    lb = 0.30
    ub = 0.93
    if result <= lb:
        shading = 'open'
    elif lb < result <= ub:
        shading = 'striped'
    elif result > ub:
        shading = 'solid'
    '''
    return figures

def classifier(cards, figures):
    #print figures
    values = []
    for figure in figures:
        values.append(figures[figure]['shading'])
    values.sort()
    if DEBUG: print values
    #clusters = hierarchy_group(figures)
    shading_list = range(len(clusters))
    for card in cards:
        figure_list = card['figures']
        card_shadings = dict([(i, 0) for i in shading_list])
        #print card_shadings
        for figure_id in figure_list:
            figure = filter(lambda x: x['id'] == figure_id, figures)[0]
            #print figure
            for shading in shading_list:
                if figure['shading'].has_key(shading):
                   card_shadings[shading] += figure['shading'][shading]
        card_shadings = Classify.normalize(card_shadings)
        #print card_shadings
        ccv = card_shading.values()
        card_shading = card_shading.keys()[ccv.index(max(ccv))]
        #print card_shading
        card['description']['shading'] = card_shading
        card['description']['veracity'] *= max(ccv)
        #print card['description']['veracity']
    return cards
