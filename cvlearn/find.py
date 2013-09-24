import cv

class Figure():
    def __init__(self, *args, **kwargs):
        self.id = kwargs['id']
        self.border = {}
        self.inner = {}
        self.description = {}

    def plot(self, image, color):
        mask = cv.fromarray(self.description['mask'])
        background = cv.fromarray(image.copy())
        #print cv.GetSize(background)
        (width, height) = cv.GetSize(mask)
        #cv.Set(background, color)
        x = self.description['offset_x']
        y = self.description['offset_y']
        cv_image = cv.GetImage(cv.fromarray(image))
        cv.SetImageROI(cv_image, (x, y, width, height))
        cv.Set(cv_image, color, mask)
        cv.ResetImageROI(cv_image)

class Card():
    def __init__(self, *args, **kwargs):
        self.description = {}
        self.id = kwargs['id']
        self.figures = kwargs['figures']

    def plot(self, image, colors, feature_type):
        # plotting card specific
        # plotting figure specific
        color = colors[self.description[feature_type]]
        for figure in self.figures:
            figure.plot(image, color)

class Figures():
    def find(self, graph):
        root = 'root'
        queue = [root]
        nodes_on_level = []
        while queue:
            sequence = []
            for node in queue:
                sequence.extend(graph.successors(node))
            nodes_on_level.append(sequence)
            queue = sequence
        #print nodes_on_level
        difference = []
        for i in range(len(nodes_on_level) - 2):
            (left, right) = (len(nodes_on_level[i]), len(nodes_on_level[i+1]))
            difference.append(abs(left - right))
        figures = []
        return nodes_on_level, difference, figures
