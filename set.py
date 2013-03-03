import random
import itertools
import __builtin__
import pygraphviz as pgv
from draw import *
from pygame.locals import *

__builtin__.set_number = 3
color_list = ('red', 'green', 'blue')
symbol_list = ('diamond', 'squiggle', 'oval')
shading_list = ('solid', 'striped', 'open')
number_list = ('one', 'two', 'three')
feature_list = (color_list, symbol_list, shading_list, number_list)
features = ('color', 'symbol', 'shading', 'number')

def deck_generator():
    deck = []
    base = [range(len(feature)) for feature in feature_list]
    tally_counter = itertools.product(*base)
    for value in tally_counter:
        card_features = itertools.imap(lambda f, g: f[g], feature_list, value)
        card = dict([pair for pair in zip(features, card_features)])
        deck.append(card)
    return deck

def take_cards(deck, counter):
    cards = []
    while deck and counter != 0:
        cards.append(deck.pop(-1))
        counter -= 1
    return cards

def is_set(cards):
    if len(cards) != set_number: return False
    confirm = True
    for feature in features:
        feature_set = set([])
        for card in cards:
            feature_set |= set([card[feature]])
        if 1 < len(feature_set) < set_number:
            confirm = False
            break
    return confirm

def search_set(cards):
    ids = []
    sets = []
    n = len(cards)
    if n < set_number: return sets, ids
    for indexes in itertools.combinations(range(n), set_number):
        multiplet = [cards[i] for i in indexes]
        if is_set(multiplet):
            ids.append(indexes)
            sets.append(multiplet)
    return sets, ids

def copy_cards(cards):
    copied_cards = []
    for card in cards:
        copied_cards.append(card.copy())
    return copied_cards

def graph_generator(cards):
    sets = search_set(cards)
    graph = pgv.AGraph()
    graph.add_nodes_from(sets)
    for a in sets:
        for b in sets:
            is_break = False
            for card_a in a:
                for card_b in b:
                    if set(card_a.items()) - set(card_b.items()) == set([]):
                        is_break = True
                        graph.add_edge(a, b)
                        graph.add_edge(b, a)
                        break
                if is_break: break
    # removing self-loops
    for node in graph.iternodes():
        graph.delete_edge(node, node)
    return graph

def topology_sort(graph):
    disjointed = 0
    while graph:
        topology = []
        for node in graph.iternodes():
            topology.append((node, len(graph.neighbors(node))))
        topology.sort(key = lambda x: x[1])
        extracted_node = topology[0][0]
        for neighbor in graph.neighbors(extracted_node):
            graph.delete_node(neighbor)
        graph.delete_node(extracted_node)
        disjointed += 1
    return disjointed
