# Weighted FST Spell Checker

A finite-state spell checker built for *Data Structures and Algorithms for
Computational Linguistics 3* (WS22/23). It learns character-edit weights from
real misspelling data, builds a minimized trie lexicon, implements a weighted
finite-state transducer (FST), and composes the two into a checker that
suggests likely corrections for a misspelled word, ranked by plausibility.

## How it works

1. **Learn edit weights from data** ([compute-weights.py](compute-weights.py))
   Aligns each `(word, misspelling)` pair from
   [spelling-data.txt](spelling-data.txt) with a Levenshtein-style dynamic
   program, using a substitution/insertion/deletion cost function instead of
   uniform edit costs. The alignment is repeated iteratively: it starts with
   uniform costs, counts how often each letter pair is aligned, re-scores
   edits using those counts, and re-aligns — repeating until the counts stop
   changing. The result is a nested count table (letter → letter → count,
   with `""` marking insertions/deletions) written to
   [spell-errors.json](spell-errors.json).

2. **Build and minimize a lexicon FSA** ([fsa.py](fsa.py))
   `build_trie()` turns a word list ([lexicon.txt](lexicon.txt)) into a trie
   FSA, sharing common prefixes across words. `FSA.minimize()` then merges
   equivalent states using Hopcroft-style partition refinement, collapsing
   the trie into a minimal DFA that still recognizes exactly the same word
   set.

3. **Weighted finite-state transducer** ([fst.py](fst.py))
   The `FST` class supports:
   - `transduce(s)` — yields every possible output string (and its weight)
     for an input string, exploring all matching paths through the machine.
   - `invert()` — swaps input/output labels, turning a "correct → misspelling"
     transducer into a "misspelling → correct" one.
   - `compose_fst(m1, m2)` — composes two FSTs into one that maps `m1`'s
     input directly to `m2`'s output. Composed states are keyed by the
     `(q, p)` state pair from each machine, so the composition is correct
     regardless of how many states either machine has.

4. **Putting it together** ([spellcheck.py](spellcheck.py))
   - `build_editfst()` builds a small weighted FST that maps any word to all
     strings one edit away from it, weighted using the counts learned in
     step 1 (rarer edits cost more).
   - The lexicon FSA is converted to an identity FST and composed with the
     edit FST, producing a transducer from lexicon words to their weighted
     one-edit-away misspellings.
   - Inverting that composed FST gives the spell checker itself: feed it a
     misspelled word, and `transduce()` returns the lexicon words it could
     have come from, each with a weight so the more probable corrections can
     be ranked first.

## Usage

```bash
# 1. Learn edit weights (writes spell-errors.json)
python3 compute-weights.py

# 2. Build the lexicon, edit FST, compose, and try a correction
python3 spellcheck.py
```

## Files

| File | Purpose |
|---|---|
| [compute-weights.py](compute-weights.py) | Iterative alignment to learn edit-operation weights |
| [fsa.py](fsa.py) | FSA class, trie construction, DFA minimization |
| [fst.py](fst.py) | Weighted FST class: `transduce`, `invert`, `compose_fst` |
| [spellcheck.py](spellcheck.py) | Builds the edit FST and assembles the full spell checker |
| [spelling-data.txt](spelling-data.txt) | Training pairs of (correct word, misspelling) |
| [lexicon.txt](lexicon.txt) | Word list used as the spell checker's dictionary |
| [spell-errors.json](spell-errors.json) | Learned edit-operation counts (output of step 1) |

## Course context

This project was completed as a graded assignment for *Data Structures and
Algorithms for Computational Linguistics 3* (WS22/23). See each file's
header for authorship and the course honor code. Originally completed as a 2-person team assignment; shared publicly with contributions described at a high level to respect the other team member's privacy.
