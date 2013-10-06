'''
Drawing cards
'''
import pygame
from patterns import FIGURES, DRAWINGS, COLORS
#from math import pi

def draw_card(card, screen, position, is_selected):
    '''
    Card drawing draw_card(card, screen, position, is_selected)
    '''
    images_dir = 'images'
    filename = '_'.join((card['symbol'], card['shading'], card['color'],))
    fullname = '%s/%s.png' % (images_dir, filename)
    simple_image = pygame.image.load(fullname).convert_alpha()
    size = simple_image.get_size()

    width = 90
    height = 117
    card_size = (width, height)
    card_center = map(lambda (x): x/2, card_size)

    # selection
    frame = pygame.surface.Surface(card_size)
    frame.fill((255, 255, 255))

    if is_selected:
        a = 6
        b = 5
        dx = 1
        dy = 1
        (x, y) = position
        # filling
        color = (255, 255, 0)
        left_up_ellipse = (dx, dy, 2*a, 2*b)
        right_up_ellipse = (width - (2*a + dx), dy, 2*a, 2*b)
        left_down_ellipse = (dx, height - (2*b + dy), 2*a, 2*b)
        right_down_ellipse = (width - (2*a + dx), height - (2*b + dy), 2*a, 2*b)
        vertical_rectangle = \
        pygame.Rect(dx + a, dy, width - 2*(dx + a), height - 2*dy)
        horizontal_rectangle = \
        pygame.Rect(dx, dy + b, width - 2*dx, height - 2*(dy + b))
        rects = [vertical_rectangle, horizontal_rectangle]
        for rect in rects: 
            pygame.draw.rect(frame, color, rect)
        ellipses = [left_up_ellipse, right_up_ellipse, 
                    left_down_ellipse, right_down_ellipse]
        for ellipse in ellipses: 
            pygame.draw.ellipse(frame, color, ellipse)
        # border not presented cause pygame draws awful arcs
        '''
        border_color = (0, 0, 0)
        top_line = ((dx + a, dy), (width - (a + dx), dy))
        bottom_line = ((dx + a, height - dy), (width - (a + dx), height - dy))
        left_line = ((dx, dy + b), (dx, height - (b + dy)))
        rigth_line = ((width - dx, dy + b), (width - dx, height - (b + dy)))
        lines = [top_line, bottom_line, left_line, rigth_line]
        right_top_arc = (right_up_ellipse, 0, 2*pi)
        left_top_arc = (left_up_ellipse, 0, 2*pi)
        left_bottom_arc = (left_down_ellipse, 0, 2*pi)
        right_bottom_arc = (right_down_ellipse, 0, 2*pi)
        arcs = [right_top_arc, left_top_arc, left_bottom_arc, right_bottom_arc]
        for line in lines: pygame.draw.line(frame, border_color, *line)
        for arc in arcs: pygame.draw.arc(frame, border_color, *arc)
        '''
    screen.blit(frame, position)

    delta = 33
    vocabulary = {'one': 1, 'two': 2, 'three': 3}
    n = vocabulary[card['number']]
    offset = -(delta * (n - 1))/2

    (x, y) = position
    center = (card_center[0] - size[0]/2 + x, card_center[1] - size[1]/2 + y)
    for i in range(n):
        position = (center[0], center[1] + offset, 
                    center[0] + size[0], center[1] + size[1] + offset)
        screen.blit(simple_image, position)
        offset += delta

def visualize(cards, field_state):
    '''
    Graphical visualisation visualize(cards, field_state)
    '''
    # pygame screen
    width = 90
    height = 117
    rows = SET_NUMBER
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
    '''
    Drawing cards in console draw_card_text(card)
    '''
    card_width = 5
    #card_height = 1
    delta = 2
    vocabulary = {'one': 1, 'two': 2, 'three': 3}
    n = vocabulary[card['number']]
    offset = -(delta * (n - 1))/2
    right_offset = left_offset = (card_width - n - (delta - 1)*(n - 1))/2
    #center = card_width/2
    card_text = DRAWINGS['blank']*left_offset
    for i in range(n):
        #position = center + offset
        figure = '_'.join((card['shading'], card['symbol'],))
        figure = figure.replace('oval', 'square')
        figure = figure.replace('squiggle', 'circle')
        figure_text = COLORS[card['color']] + FIGURES[figure] + u'\033[00m'
        card_text += figure_text
        if i != n - 1:
            card_text += DRAWINGS['blank']*(delta - 1)
        else:
            card_text += DRAWINGS['blank']*right_offset
        offset += delta
    #print card_text
    return card_text

def draw_set_text(node):
    '''
    Drawing sets in console draw_set_text(node)
    '''   
    card_width = 5
    header = DRAWINGS['light_arc_down_and_right'] + \
             DRAWINGS['light_horizontal']*card_width + \
             DRAWINGS['light_arc_down_and_left']
    footer = DRAWINGS['light_arc_up_and_right'] + \
             DRAWINGS['light_horizontal']*card_width + \
             DRAWINGS['light_arc_up_and_left']
    separator = DRAWINGS['light_vertical_and_right'] + \
                DRAWINGS['light_horizontal']*card_width + \
                DRAWINGS['light_vertical_and_left']
    set_text = header + '\n'
    for card in node[:-1]:
        card_text = draw_card_text(card)
        set_text += DRAWINGS['light_vertical'] + \
                    card_text + \
                    DRAWINGS['light_vertical'] + '\n'
        set_text += '%s\n' % separator
    set_text += DRAWINGS['light_vertical'] + \
                draw_card_text(node[-1]) + \
                DRAWINGS['light_vertical'] + '\n'
    set_text += '%s' % footer
    #print set_text
    return set_text

def ordered_sets(sets):
    '''
    Ordering sets ordered_sets(sets)
    '''
    texts = [draw_set_text(node).split('\n') for node in sets]
    horisontal_space = ' '
    limit = 10
    counter = 0
    strings = None
    if sets: 
        strings = ''
    while counter < len(sets):
        string_list = [horisontal_space.join(string) \
                      for string in zip(*texts[counter:counter + limit])]
        limited_strings = '\n'.join(string_list)
        strings = '\n'.join((strings, limited_strings))
        counter += limit
    print strings
    return strings

def draw_card_slot(card):
    '''
    Drawing slot that contains figures draw_card_slot(card)
    '''
    card_width = 5
    header = DRAWINGS['light_arc_down_and_right'] + \
             DRAWINGS['light_horizontal']*card_width + \
             DRAWINGS['light_arc_down_and_left']
    footer = DRAWINGS['light_arc_up_and_right'] + \
             DRAWINGS['light_horizontal']*card_width + \
             DRAWINGS['light_arc_up_and_left']
    separator = DRAWINGS['light_vertical']
    body = '%s%s%s' % (separator, draw_card_text(card), separator)
    card_slot_text = '\n'.join((header, body, footer))
    #print card_slot_text
    return card_slot_text

def draw_ordered_slots(cards):
    '''
    Drawing ordered slots draw_ordered_slots(cards)
    '''
    rows = 3
    cols = len(cards) / rows
    slots_text = ''
    limit = 10
    counter = 0
    while counter < cols:
        limited_slots_text = ''
        for i in range(rows):
            cards_slice = \
                cards[i*cols + counter: i*cols + min(counter + limit, cols)]
            slots_texts = \
                [draw_card_slot(card).split('\n') for card in cards_slice]
            horisontal_space = ' '
            slots_list = \
                [horisontal_space.join(string) for string in zip(*slots_texts)]
            limited_slots_text += '\n'.join(slots_list) + '\n'
        slots_text += limited_slots_text
        counter += limit
    print slots_text
    return slots_text
