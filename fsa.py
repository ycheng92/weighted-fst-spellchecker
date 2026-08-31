#!/usr/bin/env python3
"""Data Structures and Algorithms for CL III, Project 1
See <https://dsacl3-2022.github.io/p1/> for detailed instructions.

Course:      Data Structures and Algorithms for Computational Linguistics 3 WS22/23
Author:      Yin-Yin Cheng (2-person course team; shared implementation)
Honor Code:  I pledge that this program represents my own work.
I received help from: no one in designing and debugging my program.
"""
from __future__ import annotations


class FSA:
    """A class representing finite state automata.
    Args:
        deterministic: The automaton is deterministic
    Attributtes:
        transitions: transitions kept as a dictionary
            where keys are the tuple (source_state, symbol),
            values are the target state for DFA
            and a set of target states for NFA.
            Note that we do not require a dedicated 'sink' state.
            Any undefined transition should cause the FSA to reject the
            string immediately.
        start_state: number/name of the start state
        accepting: the set of accepting states
        is_deterministic (boolean): whether the FSA is deterministic or not
    """

    def __init__(self, deterministic=True):
        self.transitions = dict()
        self.start_state = None
        self.accepting = set()
        self.is_deterministic = deterministic
        self._alphabet = set()  # just for convenience, we can
        self._states = set()  # always read it off from transitions

    def add_transition(self, s1, sym, s2=None, accepting=False):
        """Add a transition from state s1 to s2 with symbol"""
        if self.start_state is None:
            self.start_state = s1
            self._states.add(s1)
        if s2 is None:
            s2 = len(self._states)
            while s2 in self._states:
                s2 += 1
        self._states.add(s2)
        self._alphabet.add(sym)
        if (s1, sym) not in self.transitions:
            self.transitions[(s1, sym)] = set()
        self.transitions[(s1, sym)].add(s2)
        if accepting:
            self.accepting.add(s2)
        if len(self.transitions[(s1, sym)]) > 1:
            self.is_deterministic = False
        return s2

    def mark_accept(self, state):
        self.accepting.add(state)

    def is_accepting(self, state):
        return state in self.accepting

    def move(self, sym, s1=None):
        """Return the state(s) reachable from 's1' on 'symbol'"""
        if s1 is None:
            s1 = self.start_state
        if (s1, sym) not in self.transitions:
            return None
        else:
            return self.transitions[(s1, sym)]

    def _recognize_dfa(self, s):
        state = self.start_state
        for sym in s:
            states = self.transitions.get((state, sym), None)
            if states is None:
                return False
            else:
                state = next(iter(states))
        if state in self.accepting:
            return True
        else:
            return False

    def _recognize_nfa(self, s):
        """NFA recognition of 's' using a stack-based agenda."""
        agenda = []
        state = self.start_state
        inp_pos = 0
        for node in self.transitions.get((self.start_state, s[inp_pos]), []):
            agenda.append((node, inp_pos + 1))
        while agenda:
            node, inp_pos = agenda.pop()
            if inp_pos == len(s):
                if node in self.accepting:
                    return True
            else:
                for node in self.transitions.get((node, s[inp_pos]), []):
                    agenda.append((node, inp_pos + 1))
        return False

    def recognize(self, s):
        """Recognize the given string 's', return a boolean value"""
        if self.is_deterministic:
            return self._recognize_dfa(s)
        else:
            return self._recognize_nfa(s)

    def minimize(self):
        # initialize P and W
        F = self.accepting
        Q = self._states
        P = [F, Q - F]
        W = [F, Q - F]

        # iterate until W is empty
        while W:
            # choose and remove a set A from W
            A = W.pop(0)

            # iterate over all input symbols
            for c in self._alphabet:

                # get the set of states for which a transition on c leads to a state in A
                X = set()
                for transition in self.transitions:
                    if transition[1] == c:
                        for x in self.transitions[transition]:
                            if x in A:
                                X.add(transition[0])

                # iterate over all sets Y in P for which X ∩ Y is nonempty and Y \ X is nonempty
                for Y in P:
                    if X.intersection(Y) and Y.difference(X):
                        # replace Y in P by the two sets X ∩ Y and Y \ X
                        P.remove(Y)
                        P.append(X.intersection(Y))
                        P.append(Y.difference(X))

                        if Y in W:
                            # replace Y in W by the same two sets
                            W.remove(Y)
                            W.append(X.intersection(Y))
                            W.append(Y.difference(X))
                        else:
                            # add the smaller of the two sets to W
                            if len(X.intersection(Y)) <= len(Y.difference(X)):
                                W.append(X.intersection(Y))
                            else:
                                W.append(Y.difference(X))

        # construct the minimized DFA
        new_states = {frozenset(s) for s in P}
        new_tran = dict()
        i = 0
        for s in P:
            new_tran[i] = s
            i += 1
        new_final_states = set([s for s in new_states if s.intersection(F)])
        new_start_state = next(s for s in new_states if self.start_state in s)
        new_transitions = {}

        for state in new_states:
            for c in self._alphabet:
                if (next(iter(state)), c) in self.transitions:

                    next_state = next(iter(self.transitions[(next(iter(state)), c)]))
                    for i in new_states:
                        if next_state in i:
                            new_transitions[(state, c)] = i
                            break
        new_states1 = set()
        for i in range(len(new_states)):
            new_states1.add(i)

        new_final_states1 = set()
        for s in new_final_states:
            for i in new_tran:
                if new_tran[i] == s:
                    new_final_states1.add(i)

        new_start_state1 = 0
        for i in new_tran:
            if new_tran[i] == new_start_state:
                new_start_state1 = i

        new_transitions1 = dict()
        for s in new_transitions:
            for i in new_tran:
                if new_tran[i] == new_transitions[s]:
                    for j in new_tran:
                        if new_tran[j] == s[0]:
                            if (j, s[1]) not in new_transitions1:
                                new_transitions1[(j, s[1])] = set()
                            new_transitions1[(j, s[1])].add(i)

        self._states = new_states1
        self.start_state = new_start_state1
        self.accepting = new_final_states1
        self.transitions = new_transitions1


def get_i(word: str, i: int, default=None):
    return word[i] if -len(word) <= i < len(word) else default


def build_trie(words: list[str]) -> FSA:
    """Given a list of words, create and return a trie FSA.

    For the given sequence of words, you should build a trie,
    an FSA where letters are the edge labels. Since the structure is a
    trie, common prefix paths should be shared but suffixes will
    necessarily use many redundant paths.

    You should initialize an instance of the FSA class defined above,
    and add only the required arcs successively.
    """
    fsa = FSA()
    start_state = 0

    for word in words:
        next_state: int | None = start_state
        for i in range(len(word)):
            cur_letter = get_i(word, i, None)
            next_letter = get_i(word, i + 1, None)
            next_state_found = False
            next_states = fsa.move(cur_letter, next_state) or set()

            if len(next_states) != 0:
                for pos_next_state in iter(next_states):
                    if len(fsa.move(next_letter, pos_next_state) or set()) != 0:
                        next_state = pos_next_state
                        next_state_found = True
                        break
                if not next_state_found and len(next_states) != 0:
                    next_state = next(iter(next_states))
            else:
                next_state = fsa.add_transition(
                    next_state, cur_letter, accepting=next_letter is None
                )
    return fsa


if __name__ == "__main__":
    # Example usage:
    m = build_trie(
        ["walk", "walks", "wall", "walls", "want", "wants", "work", "works", "forks"]
    )
    m.minimize()
    assert m.recognize("walk") == True
    assert m.recognize("wark") == False
