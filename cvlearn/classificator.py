import cv2

class Classificator():
    def normalize(self, sequence):
        # normalize
        summ = sum(sequence.values())
        #print sequence
        #print summ
        if summ != 0:
            for item in sequence: sequence[item] /= summ
        else:
            for item in sequence: sequence[item] = 1.0 / len(sequence)
        #print sequence
        return sequence

    def mocm(self, element, clusters, values):
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

class ColorClassificator(Classificator):
    def distance(self, hist_a, hist_b):
        params = (1, 0, cv2.NORM_L1)
        cv2.normalize(hist_a, hist_a, *params)
        cv2.normalize(hist_b, hist_b, *params)
        result = 1 - cv2.compareHist(hist_a, hist_b, 2)
        #print result
        return result

    def cluster_center_old(self, cluster, hist):
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

    def cluster_center(self, cluster, hists):
        subhists = map(lambda x: hists[x], cluster)
        center = reduce(lambda x, y: x + y, subhists)
        return center

class ShadingClassificator(Classificator):
    def cluster_center(self, hist):
        mass = 0.0
        accum = 0.0
        for index, value in enumerate(hist):
            mass += value[0] * index
            accum += value[0]
        center = mass / accum
        #print center
        return center

class SymbolClassificator(Classificator):
    def distance(self, a, b):
        result = abs(a - b)    
        return result

    def cluster_center(self, cluster, values):
        accumulator = 0
        for member in cluster:
            accumulator += values[member]
        center = accumulator / len(cluster)
        return center
