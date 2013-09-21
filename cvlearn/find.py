class Figure():
    def __init__(self, *args, **kwargs):
        self.description = {}

    def plot(self):
        pass

class Card():
    def __init__(self, *args, **kwargs):
        self.description = {}
        self.id = kwargs['id']
        self.figures = kwargs['figures']

    def plot(self):
        for figure in self.figures:
            figure.plot()

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
