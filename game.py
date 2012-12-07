import time
import pygame
import random
import itertools
import __builtin__
import pygraphviz as pgv
from draw import *
from user_input import *
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
    sets = []
    if len(cards) < set_number: return sets
    for multiplet in itertools.combinations(cards, set_number):
        if is_set(multiplet): sets.append(multiplet)
    return sets

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

def interaction(cards):
    width = 90
    height = 117
    is_break = False
    field_state = {'slots': {}, 'selected': []}
    chosen_set = None
    pygame.event.set_blocked(None)
    pygame.event.set_allowed([MOUSEBUTTONDOWN, QUIT])
    slots = visualize(cards, field_state)
    while not is_break:
        event = pygame.event.wait()
        if event.type == QUIT:
            exit()
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                (x_pos, y_pos) = pygame.mouse.get_pos()
                slots = field_state['slots']
                for key in slots:
                    slot = slots[key]
                    (v, h) = slot['position']
                    if v <= x_pos < v + width and h <= y_pos < h + height:
                        if key in field_state['selected']:
                            field_state['selected'].remove(key)
                            visualize(cards, field_state)
                        else:
                            if len(field_state['selected']) < set_number:
                                field_state['selected'].append(key)
                                visualize(cards, field_state)
                            if len(field_state['selected']) == set_number:
                                selected_cards = []
                                for number in field_state['selected']:
                                    selected_cards.append(slots[number]['card'])
                                if is_set(selected_cards):
                                    chosen_set = selected_cards
                                    is_break = True
                                    break
            if event.button == 2:
                exit()
            if event.button == 3:
                is_break = True
                break
    return chosen_set

print 'deck init'
# deck init
deck = deck_generator()
#print deck
#print len(deck)

# max number of sets is 27

# deck shuffle
print 'shuffling deck'
random.shuffle(deck)
#print deck

# pygame init
pygame.init()

# game loop
sets = []
# pick up cards
initial_number_of_cards = 4 * set_number
cards = take_cards(deck, initial_number_of_cards)
while sets or deck:
    print u'\033[2J'
    #print '%d cards in a deck' % len(deck)

    # search set
    sets = search_set(cards)
    #print sets
    #print 'number of sets: %d' % len(sets)
    draw_ordered_slots(cards)
    print 'sets:'
    ordered_sets(sets)

    graph = graph_generator(cards)

    topology = []
    for node in graph.iternodes():
        topology.append(len(graph.neighbors(node)))
    print topology

    # searching disjoint sets
    disjointed = topology_sort(graph)
    print 'disjointed sets: %d' % disjointed

    chosen_set = interaction(cards)
    replacement = take_cards(deck, set_number)

    if sets and chosen_set:
        if replacement and len(cards) <= initial_number_of_cards:
            replacements_list = zip(chosen_set, replacement)
            for (replaceable, replacing) in replacements_list:
                cards[cards.index(replaceable)] = replacing
        else:
            for card in chosen_set:
                cards.remove(card)
    else:
        if replacement:
            cols = len(cards) / set_number
            index = 1
            for inserted in replacement:
                cards.insert(index * (cols + 1) - 1, inserted)
                index += 1
    if not sets and not replacement:
        print 'game over'
        break
