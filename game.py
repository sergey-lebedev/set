import pygame
import random
import itertools
from draw import *
from pygame.locals import *
import pygraphviz as pgv

set_number = 3
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

print 'deck init'
# deck init
deck = deck_generator()
#print deck
#print len(deck)

# max number of sets is 27
#graph = graph_generator(deck)
#print topology_sort(graph)

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
    #print 'deck: %d' % len(deck)
    number_of_cards = set_number

    # pygame screen
    width = 90
    height = 117
    rows = set_number
    cols = len(cards) / rows
    screen = pygame.display.set_mode((width * cols, height * rows))
    screen.fill((255, 255, 255))

    col_counter = 0
    for card in cards:
        position = ((col_counter % cols) * width, (col_counter / cols) * height)
        draw_card(card, screen, position)
        #draw_card_slot(card)
        col_counter += 1
    pygame.display.update()
    draw_ordered_slots(cards)       

    # search set
    print 'sets:'
    sets = search_set(cards)
    #print sets
    #print 'number of sets: %d' % len(sets)
    for node in sets:
        draw_set_text(node)
    ordered_sets(sets)

    if sets: chosen_set = random.choice(sets)

    graph = graph_generator(cards)

    topology = []
    for node in graph.iternodes():
        topology.append(len(graph.neighbors(node)))
    print topology

    # searching disjoint sets
    print 'disjointed sets:'
    disjointed = topology_sort(graph)
    print disjointed

    replacement = take_cards(deck, number_of_cards)
    if sets and replacement and len(cards) <= initial_number_of_cards:
        replacements_list = zip(chosen_set, replacement)
        for (replaceable, replacing) in replacements_list:
            cards[cards.index(replaceable)] = replacing
    if sets and (not replacement or len(cards) > initial_number_of_cards):
        for card in chosen_set:
            cards.remove(card)
    if not sets and replacement:
        cards.extend(replacement)
    while raw_input():
        pass

''' 
is_break = False
while not is_break:
    for event in pygame.event.get():
        if event.type == QUIT:
            exit()
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 3:
                exit()
                #screen1 = pygame.display.set_mode((10, 10))
'''
