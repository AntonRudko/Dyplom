import matplotlib.pyplot as plt
import re

def state_index(state: str) -> int:
    m = re.search(r'\d+', state)
    return int(m.group()) if m else 0

def _label(state, automaton):
    label = state
    if state == automaton.start_state:
        label = f"→{label}"
    if state in automaton.accept_states:
        label = f"{label}*"
    return label

def _cell(target):
    if target is None:
        return "–"
    if isinstance(target, str):
        return target
    return ", ".join(sorted(target)) if target else "∅"

def visualize_transition_table(automaton, filename='transition_table.png'):
    states = sorted(
        automaton.states,
        key=lambda s: (s != automaton.start_state, state_index(s))
    )
    has_epsilon = any(sym == "" for (_, sym) in automaton.transitions)
    alphabet = sorted(automaton.alphabet)
    if has_epsilon:
        display_symbols = [""] + [s for s in alphabet if s != ""]
    else:
        display_symbols = alphabet

    table_data = [
        [_label(state, automaton)]
        + [_cell(automaton.transitions.get((state, symbol))) for symbol in display_symbols]
        for state in states
    ]

    col_labels = ["State"] + [("\u03b5" if s == "" else s) for s in display_symbols]

    fig, ax = plt.subplots(figsize=(len(col_labels) * 1.2, len(states) * 0.6 + 1))
    ax.axis("off")

    table = ax.table(
        cellText=table_data,
        colLabels=col_labels,
        cellLoc="center",
        loc="center"
    )

    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 1.4)

    for col in range(len(col_labels)):
        cell = table[0, col]
        cell.set_text_props(weight="bold")
        cell.set_facecolor("#DDDDDD")

    plt.savefig(filename, bbox_inches="tight")
    plt.close(fig)
    print(f"Transition table saved to {filename}")

def visualize_nfa_dfa(automaton, base_filename='automaton'):
    visualize_transition_table(automaton, f'{base_filename}.png')
