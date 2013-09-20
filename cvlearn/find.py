class Figure():
    def __init__(self):
        self.description = {}

class Card():
    def __init__(self):
        self.figures = []
        self.description = {}

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

class Cards():
    def __init__(self):
        self.cards = []

    def two_equal_peaks_finder(self, difference):
        # two equal peaks
        level = None
        position = 2
        sliced = difference[position:]
        if sliced:
            min_value = min(sliced)
            index = sliced.index(min_value)
            level = position + index + 1
        return level

    def find(self, graph):
        cards = []
        (nodes_on_level, difference, figures) = Figures().find(graph)
        # two equal peaks
        level = self.two_equal_peaks_finder(difference)
        steps = 2
        sequence = []
        if level: sequence = nodes_on_level[level]
        while steps != 0 and sequence:
            steps -= 1
            parents = []
            for node in sequence:
                parent = graph.predecessors(node)[0]
                if parent not in parents:
                    parents.append(parent)
                #print parents
            sequence = parents
        print '%d card(s) detected'%len(sequence)
        #print cards
        #print sequence
        cards = []
        for node in sequence:
            card = {'id': node, 'figures': graph.successors(node)}
            cards.append(card)
        #print cards
        return cards

    def veracity(self, cards, ids):
        veracity = 1
        for card_id in ids:
            veracity *= cards[card_id]['description']['veracity']
        return veracity
