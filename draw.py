import pygame
from patterns import *

def draw_card(card, screen, position, is_selected):
    images_dir = 'images'
    filename = '_'.join((card['symbol'], card['shading'], card['color'],))
    fullname = '%s/%s.png' % (images_dir, filename)
    simple_image = pygame.image.load(fullname).convert_alpha()
    size = simple_image.get_size()

    width = 90
    height = 117
    card_size = (width, height)
    card_center = map(lambda (x): x/2 , card_size)

    # selection
    backlight_surface = pygame.surface.Surface(card_size)
    if is_selected:
        color = (255, 255, 0)
    else:
        color = (255, 255, 255)

    (x, y) = position
    rectangle = pygame.Rect(0, 0, width, height)
    pygame.draw.rect(backlight_surface, color, rectangle)
    screen.blit(backlight_surface, position)

    delta = 33
    vocabulary = {'one': 1, 'two': 2, 'three': 3}
    n = vocabulary[card['number']]
    offset = -(delta * (n - 1))/2

    (x, y) = position
    center = (card_center[0] - size[0]/2 + x, card_center[1] - size[1]/2 + y)
    for i in range(n):
        position = (center[0], center[1] + offset, center[0] + size[0], center[1] + size[1] + offset)
        screen.blit(simple_image, position)
        offset += delta

def visualize(cards, field_state):
    # pygame screen
    width = 90
    height = 117
    rows = set_number
    cols = len(cards) / rows
    screen = pygame.display.set_mode((width * cols, height * rows))
    pygame.display.set_caption('set')
    screen.fill((255, 255, 255))

    counter = 0
    for card in cards:
        position = ((counter % cols) * width, (counter / cols) * height)
        if not field_state['slots'].has_key(counter):
            field_state['slots'][counter] = {'card': card, 'position': position}
        if counter in field_state['selected']:
            is_selected = True
        else:
            is_selected = False
        draw_card(card, screen, position, is_selected)
        counter += 1

    pygame.display.update()
    return field_state

def draw_card_text(card):
    card_width = 5
    card_height = 1
    delta = 2
    vocabulary = {'one': 1, 'two': 2, 'three': 3}
    n = vocabulary[card['number']]
    offset = -(delta * (n - 1))/2
    right_offset = left_offset = (card_width - n - (delta - 1)*(n - 1))/2
    center = card_width/2
    card_text = drawings['blank']*left_offset
    for i in range(n):
        position = center + offset
        figure = '_'.join((card['shading'], card['symbol'],))
        figure = figure.replace('oval', 'square')
        figure = figure.replace('squiggle', 'circle')
        figure_text = colors[card['color']] + figures[figure] + u'\033[00m'
        card_text += figure_text
        if i != n - 1:
            card_text += drawings['blank']*(delta - 1)
        else:
            card_text += drawings['blank']*right_offset
        offset += delta
    #print card_text
    return card_text

def draw_set_text(node):
    card_width = 5
    header = drawings['light_arc_down_and_right'] + drawings['light_horizontal']*card_width + drawings['light_arc_down_and_left']
    footer = drawings['light_arc_up_and_right'] + drawings['light_horizontal']*card_width + drawings['light_arc_up_and_left']
    separator = drawings['light_vertical_and_right'] + drawings['light_horizontal']*card_width + drawings['light_vertical_and_left']
    set_text = header + '\n'
    for card in node[:-1]:
        card_text = draw_card_text(card)
        set_text += drawings['light_vertical'] + card_text + drawings['light_vertical'] + '\n'
        set_text += '%s\n' % separator
    set_text += drawings['light_vertical'] + draw_card_text(node[-1]) + drawings['light_vertical'] + '\n'
    set_text += '%s' % footer
    #print set_text
    return set_text

def ordered_sets(sets):
    texts = [draw_set_text(node).split('\n') for node in sets]
    horisontal_space = ' '
    string_list = [horisontal_space.join(string) for string in zip(*texts)]
    strings = '\n'.join(string_list)
    print strings
    return strings

def draw_card_slot(card):
    card_width = 5
    header = drawings['light_arc_down_and_right'] + drawings['light_horizontal']*card_width + drawings['light_arc_down_and_left']
    footer = drawings['light_arc_up_and_right'] + drawings['light_horizontal']*card_width + drawings['light_arc_up_and_left']
    separator = drawings['light_vertical']
    body = '%s%s%s' % (separator, draw_card_text(card), separator)
    card_slot_text = '\n'.join((header, body, footer))
    #print card_slot_text
    return card_slot_text

def draw_ordered_slots(cards):
    rows = 3
    cols = len(cards) / rows
    slots_text = ''
    for i in range(rows):
        slots_texts = [draw_card_slot(card).split('\n') for card in cards[i*cols: (i + 1) * cols]]
        horisontal_space = ' '
        slots_list = [horisontal_space.join(string) for string in zip(*slots_texts)]
        slots_text += '\n'.join(slots_list) + '\n'
    print slots_text
    return slots_text
