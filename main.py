from Analize.nfa import *
from Analize.words import *
from Analize.word_check import run_words
from Analize.table_visualizer import visualize_nfa_dfa
from Analize.simple_benchmark import benchmark_random_determinization

from Algoritms.sub_set import determinize_nfa
from Algoritms.brzozowski import determinize_brz
from Algoritms.transset import determinize_transset

if __name__ == '__main__':

    nfa = nfa_test2
    dfa = determinize_nfa(nfa)
    dfa2 = determinize_brz(nfa)
    dfa3 = determinize_transset(nfa)

    run_words(nfa,dfa2,words_1)

    visualize_nfa_dfa(nfa, base_filename='Table/NFA')
    visualize_nfa_dfa(dfa, base_filename='Table/sub_set')
    visualize_nfa_dfa(dfa2, base_filename='Table/brzozowski')
    visualize_nfa_dfa(dfa3, base_filename='Table/transset')

    benchmark_random_determinization()
