#!/usr/bin/env python3
"""Data Structures and Algorithms for CL III, Project 1
See <https://dsacl3-2022.github.io/p1/> for detailed instructions.

Course:      Data Structures and Algorithms for Computational Linguistics 3 WS22/23
Author:      Yin-Yin Cheng (2-person course team; shared implementation)
Honor Code:  I pledge that this program represents my own work.
I received help from: no one in designing and debugging my program.
"""
from __future__ import annotations

from fsa import FSA
from typing import Iterator

from collections import OrderedDict
from sortedcollections import OrderedSet


class FST:
    """A weighted FST class."""

    def __init__(self):
        self.transitions: OrderedDict[tuple[int, str], set[tuple[str, int, int]]] = (
            OrderedDict()
        )
        self.start_state, self.accepting = None, OrderedSet()
        self._sigma_in, self._sigma_out = OrderedSet(), OrderedSet()
        self._states = OrderedSet([0])

    @classmethod
    def fromfsa(cls, fsa: FSA) -> "FST":
        """Return an FST instance using an FSA.

        This method should take an instance of the FSA class defined
        in fsa.py, and returns an FST with identity transitions.
        """
        fst = cls()
        for (s1, sym), s2s in fsa.transitions.items():
            for s2 in s2s:
                fst.add_transition(s1, sym, s2, sym)
        fst.accepting = fsa.accepting
        fst.start_state = fsa.start_state
        return fst

    def mark_accepting(self, state):
        self.accepting.add(state)

    def get_transitions(
        self, s1: int, insym: str | None = None
    ) -> Iterator[tuple[int, str, int]]:
        """ """
        if insym is None:
            syms = self._sigma_in
        else:
            syms = (insym,)
        for sym in syms:
            if (s1, sym) in self.transitions:
                for outsym, s2, w in self.transitions[(s1, sym)]:
                    yield s2, outsym, w

    def add_transition(
        self,
        s1: int,
        insym: str,
        s2: int | None = None,
        outsym: str = None,
        w: int = 0,
        accepting=False,
    ) -> int:
        """Add a transition from s1 to s2 with label insym:outsym.

        If s2 is None, create a new state. If outsym is None, assume
        identity transition.

        We assume transition labels are characters, and the states are
        integers, and we use integer labels when we create states.
        However, the code should (mostly) work fine with arbitrary labels.
        """
        if self.start_state is None:
            self.start_state = s1
            self._states.add(s1)
        if s2 is None:
            s2 = len(self._states)
            while s2 in self._states:
                s2 += 1
        if s2 not in self._states:
            self._states.add(s2)
        if outsym is None:
            outsym = insym
        self._sigma_in.add(insym)
        self._sigma_out.add(outsym)
        if (s1, insym) not in self.transitions:
            self.transitions[(s1, insym)] = OrderedSet()
        self.transitions[s1, insym].add((outsym, s2, w))
        if accepting:
            self.accepting.add(s2)
        return s2

    def move(self, s1: int, insym: str) -> set[int]:
        """Return the state(s) reachable from 's1' on 'symbol'"""
        if (s1, insym) in self.transitions:
            return self.transitions[(s1, insym)]
        else:
            return OrderedSet()

    def transduce_util(
        self,
        path: list[tuple[int, str, int]],
        state: int,
        visited: set[tuple[int, str]],
        word: str,
    ) -> Iterator[list[tuple[str, int, int]]]:
        # print(path)
        if not word:
            if state in self.accepting:
                yield path
            return

        first_sym = word[0]
        for state, sym, w in self.get_transitions(state, first_sym):
            if (state, sym) not in visited:
                visited.add((state, sym))
                np = [*path, (sym, w)]
                yield from self.transduce_util(np, state, visited, word[1:])

    def transduce(self, s: str) -> Iterator[list[tuple[str, float]]]:
        """Transduce the string s, returning the result of the transduction.

        You do not need to handle epsilon loops (our FSTs do not have
        epsilon loops).

        Each result should be accompanied by the weight of the
        particular transduction of the input string. We calculate
        the weight of a path as the sum of the weights of the transitions
        in the path (this works well with log probabilities).

        Your method should preferably yield pairs of (output, weight)
        or return a sequence of such pairs.

        Tips:
            - You may find the _recognize_nfa method of the FSA class
              a useful starting point for implementing this method.
            - You will need to keep the output string built so far
              and its weight in your agenda so that you can use it
              when backtracking.
            - Unlike NFA recognition, we cannot stop as soon as we find
              an acceptable string. We want to generate all possible
              paths.
        """
        if not s:
            yield []

            return

        first_sym = s[0]

        for state, sym, weight in self.get_transitions(self.start_state, first_sym):
            yield from self.transduce_util(
                [(sym, weight)], state, {(state, sym)}, s[1:]
            )

        return

    def invert(self):
        """Invert the FST."""

        outs = self._sigma_in
        ins = self._sigma_out
        transitions: OrderedDict[tuple[int, str], set[tuple[str, int, int]]] = (
            OrderedDict()
        )
        for t in self.transitions:
            for i in self.transitions[t]:
                if (t[0], i[0]) not in transitions:
                    transitions[(t[0], i[0])] = OrderedSet()
                transitions[(t[0], i[0])].add((t[1], i[1], i[2]))
        self.transitions = transitions
        self._sigma_in = ins
        self._sigma_out = outs

    @classmethod
    def compose_fst(cls, m1: FST, m2: FST) -> "FST":
        """Compose two FST instances (m1 and m2) and return the composed FST.

        While implementing this method, you should pay attention to
        epsilons, since our use case requires epsilon transitions.
        However, you can make use of the fact that `m1` does not
        include any epsilon transitions in our application. Also,
        since `m1` in our application is not weighted, the arc weight
        can trivially be taken from `m2`.
        """
        fst = cls()

        # compose states
        Q = m1._states
        P = m2._states
        R = set()
        for q in Q:
            for p in P:
                R.add((q, p))
        fst._states = R

        # compose start states
        Q0 = m1.start_state
        P0 = m2.start_state
        R0 = (Q0, P0)
        fst.start_state = R0

        # compose final states
        QF = m1.accepting
        PF = m2.accepting
        RF = set()
        for q in QF:
            for p in PF:
                RF.add((q, p))
        fst.accepting = RF

        # compose transitions
        A = m1.transitions
        B = m2.transitions
        ins = set()
        outs = set()
        for a in A:
            for b in B:
                for i in A[a]:
                    if i[0] == b[1]:
                        for j in B[b]:
                            fst.add_transition(
                                (a[0], b[0]), a[1], (i[1], j[1]), j[0], j[2]
                            )
                            ins.add(a[1])
                            outs.add(j[0])
        fst._sigma_in = ins
        fst._sigma_out = outs

        return fst


if __name__ == "__main__":
    f = FST()
    f.add_transition(0, "a", 1, "x")
    f.add_transition(0, "a", 1, "b")
    f.add_transition(0, "b", 2, "y")
    f.add_transition(1, "c", 3, "z")
    f.add_transition(2, "d", 3, "w")
    f.add_transition(2, "e", 4, "t")

    f.mark_accepting(3)
    f.mark_accepting(4)

    # res = list(f.transduce("ac"))

    # print(res)

    f.invert()

    res = list(f.transduce("bz"))

    print(res)
