"""Figure classification"""
import cv2

class Classificator():
    """"""
    def normalize(self, sequence):
        """Normalizing sequence normalize(self, sequence)"""
        # normalize
        summ = sum(sequence.values())
        #print sequence
        #print summ
        if summ != 0:
            for item in sequence: 
                sequence[item] /= summ
        else:
            for item in sequence: 
                sequence[item] = 1.0 / len(sequence)
        #print sequence
        return sequence

    def mocm(self, element, clusters, values):
        """Measuring mocm(self, element, clusters, values)"""
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

    def set_feature(self, cards, feature_list, feature_name):
        """
        Card feature detector 
        set_feature(self, cards, feature_list, feature_name)"""
        features_name = feature_name  + 's'
        for card in cards:
            card_features = dict([(i, 0) for i in feature_list])
            #print card_features
            for figure in card.figures:
                #figure_id  = filter(lambda x: x['id'] == figure_id, figures)[0]
                #print figure
                for feature in feature_list:
                    if figure.description[features_name].has_key(feature):
                       card_features[feature] += \
                                    figure.description[features_name][feature]
            card_features = self.normalize(card_features)
            #print card_features
            cfv = card_features.values()
            card_feature = card_features.keys()[cfv.index(max(cfv))]
            #print card_feature
            card.description[feature_name] = card_feature
            card.description['veracity'] *= max(cfv)
            #print card['description']['veracity']

class ColorClassificator(Classificator):
    """ColorClassificator"""
    def distance(self, hist_a, hist_b):
        """Measuring distance between two hists"""
        params = (1, 0, cv2.NORM_L1)
        cv2.normalize(hist_a, hist_a, *params)
        cv2.normalize(hist_b, hist_b, *params)
        result = 1 - cv2.compareHist(hist_a, hist_b, 2)
        #print result
        return result
    """
    def cluster_center_old(self, cluster, hist):
        """"""  
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
    """
    def cluster_center(self, cluster, hists):
        """Searching cluster center cluster_center(self, cluster, hists)"""
        subhists = map(lambda x: hists[x], cluster)
        center = reduce(lambda x, y: x + y, subhists)
        return center

    def set_feature(self, cards, feature_list):
        """Setting features"""
        Classificator.set_feature(self, cards, feature_list, 'color')

class ShadingClassificator(Classificator):
    """ShadingClassificator"""
    def cluster_center(self, hist):
        """Searching cluster center cluster_center(self, hist)"""
        mass = 0.0
        accum = 0.0
        for index, value in enumerate(hist):
            mass += value[0] * index
            accum += value[0]
        center = mass / accum
        #print center
        return center

    def set_feature(self, cards, feature_list):
        """Setting features"""
        Classificator.set_feature(self, cards, feature_list, 'shading')

class SymbolClassificator(Classificator):
    """SymbolClassificator"""
    def distance(self, a, b):
        """Measuring distance between two symbols"""
        result = abs(a - b)
        return result

    def cluster_center(self, cluster, values):
        """Searching cluster center cluster_center(sself, cluster, values)"""
        accumulator = 0
        for member in cluster:
            accumulator += values[member]
        center = accumulator / len(cluster)
        return center

    def set_feature(self, cards, feature_list):
        """Setting features"""
        Classificator.set_feature(self, cards, feature_list, 'symbol')
