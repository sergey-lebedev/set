def feature_detector(graph, card):
    steps = 2
    #print card
    sequence = [card]
    #print sequence
    while steps != 0 and sequence:
        steps -= 1
        childrens = []
        for node in sequence:
            #print node
            child = graph.successors(node)
            if child not in childrens:
                childrens.extend(child)
        sequence = childrens
        #print childrens
    #print '%d figure(s) on card'%len(sequence)
    return sequence, len(sequence)
