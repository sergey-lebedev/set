import time
import pygame
from set import *

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
while cards or deck:
    print u'\033[2J'
    #print '%d cards in a deck' % len(deck)

    # search set
    sets, card_ids = search_set(cards)
    #print sets
    #print 'number of sets: %d' % len(sets)
    draw_ordered_slots(cards)
    print 'sets:'
    ordered_sets(sets)
    '''
    graph = graph_generator(cards)

    topology = []
    for node in graph.iternodes():
        topology.append(len(graph.neighbors(node)))
    print topology

    # searching disjoint sets
    disjointed = topology_sort(graph)
    print 'disjointed sets: %d' % disjointed
    '''
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
