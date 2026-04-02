from Analize.mocks.nfa import *
from Analize.mocks.words import *
from Analize.tools.word_check import run_words
from Analize.tools.table_visualizer import visualize_nfa_dfa
from Analize.tools.graph_visualizer import visualize_automaton_graph

from Algoritms.sub_set import determinize_nfa
from Algoritms.brzozowski import determinize_brz
from Algoritms.transset import determinize_transset
from Algoritms.lazy_subset import determinize_lazy

from Algoritms_with_epsilon.sub_set_epsilon import determinize_nfa_epsilon
from Algoritms_with_epsilon.brzozowski_epsilon import determinize_brz_epsilon
from Algoritms_with_epsilon.transset_epsilon import determinize_transset_epsilon
from Algoritms_with_epsilon.lazy_subset_epsilon import determinize_lazy_epsilon

if __name__ == '__main__':

    nfa = nfa_test1
    dfa, _ops1 = determinize_nfa(nfa)
    dfa2, _ops2 = determinize_brz(nfa)
    dfa3, _ops3 = determinize_transset(nfa)
    dfa5, _ops5 = determinize_lazy(nfa)

    run_words(nfa, dfa2, words_1)
    run_words(nfa, dfa5, words_1)

    # --- Таблиці переходів ---
    print('Tables')
    visualize_nfa_dfa(nfa, base_filename='Outputs/tables/NFA')
    visualize_nfa_dfa(dfa, base_filename='Outputs/tables/sub_set')
    visualize_nfa_dfa(dfa2, base_filename='Outputs/tables/brzozowski')
    visualize_nfa_dfa(dfa3, base_filename='Outputs/tables/transset')
    visualize_nfa_dfa(dfa5, base_filename='Outputs/tables/lazy_subset')
    print('Graphs')
    # --- Графи автоматів ---
    visualize_automaton_graph(nfa, filename='Outputs/graphs/NFA_graph')
    visualize_automaton_graph(dfa, filename='Outputs/graphs/sub_set_graph')
    visualize_automaton_graph(dfa2, filename='Outputs/graphs/brzozowski_graph')
    visualize_automaton_graph(dfa3, filename='Outputs/graphs/transset_graph')
    visualize_automaton_graph(dfa5, filename='Outputs/graphs/lazy_subset_graph')

    # --- Epsilon NFA ---
    eps_dfa1, _eops1 = determinize_nfa_epsilon(nfa_epsilon)
    eps_dfa2, _eops2 = determinize_brz_epsilon(nfa_epsilon)
    eps_dfa3, _eops3 = determinize_transset_epsilon(nfa_epsilon)
    eps_dfa5, _eops5 = determinize_lazy_epsilon(nfa_epsilon)

    print('Epsilon Tables')
    # --- Epsilon таблиці ---
    visualize_nfa_dfa(nfa_epsilon, base_filename='Outputs/epsilon_tables/NFA')
    visualize_nfa_dfa(eps_dfa1, base_filename='Outputs/epsilon_tables/sub_set')
    visualize_nfa_dfa(eps_dfa2, base_filename='Outputs/epsilon_tables/brzozowski')
    visualize_nfa_dfa(eps_dfa3, base_filename='Outputs/epsilon_tables/transset')
    visualize_nfa_dfa(eps_dfa5, base_filename='Outputs/epsilon_tables/lazy_subset')

    print('Epsilon Graphs')
    # --- Epsilon графи ---
    visualize_automaton_graph(nfa_epsilon, filename='Outputs/epsilon_graphs/NFA_graph')
    visualize_automaton_graph(eps_dfa1, filename='Outputs/epsilon_graphs/sub_set_graph')
    visualize_automaton_graph(eps_dfa2, filename='Outputs/epsilon_graphs/brzozowski_graph')
    visualize_automaton_graph(eps_dfa3, filename='Outputs/epsilon_graphs/transset_graph')
    visualize_automaton_graph(eps_dfa5, filename='Outputs/epsilon_graphs/lazy_subset_graph')
