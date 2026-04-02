import graphviz
import re
from collections import defaultdict


def state_index(state: str) -> int:
    m = re.search(r'\d+', state)
    return int(m.group()) if m else 0


def visualize_automaton_graph(automaton, filename='automaton_graph'):
    """
    Будує графоїд автомата (NFA або DFA) і зберігає у PNG.

    - Стартовий стан: невидимий вузол зі стрілкою
    - Приймальні стани: подвійне коло
    - Переходи: стрілки з підписами символів
    - Об'єднує ребра між однаковими парами станів
    """
    dot = graphviz.Digraph(format='png')
    dot.attr(rankdir='LR', dpi='150')
    dot.attr('node', fontname='Arial', fontsize='12')
    dot.attr('edge', fontname='Arial', fontsize='11')

    # Невидимий вузол для стрілки до стартового стану
    dot.node('__start__', shape='point', width='0')
    dot.edge('__start__', automaton.start_state)

    # Вузли
    states = sorted(automaton.states, key=state_index)
    for state in states:
        if state in automaton.accept_states:
            dot.node(state, shape='doublecircle', style='filled',
                     fillcolor='#d4edda', color='#28a745', penwidth='2')
        else:
            dot.node(state, shape='circle', style='filled',
                     fillcolor='#e8f0fe', color='#4a86c8', penwidth='1.5')

    # Збір та об'єднання переходів
    edge_labels = defaultdict(list)
    for (src, symbol), targets in automaton.transitions.items():
        if isinstance(targets, str):
            # DFA: targets — рядок (один стан)
            edge_labels[(src, targets)].append(symbol)
        else:
            # NFA: targets — множина станів
            for dst in targets:
                edge_labels[(src, dst)].append(symbol)

    # Ребра
    for (src, dst), symbols in edge_labels.items():
        label = ', '.join("\u03b5" if s == "" else s for s in sorted(symbols))
        dot.edge(src, dst, label=label)

    # Збереження
    dot.render(filename, cleanup=True)
    print(f"Automaton graph saved to {filename}.png")
