#!/usr/bin/env python3
"""Data Structures and Algorithms for CL III, Project 1
See <https://dsacl3-2022.github.io/p1/> for detailed instructions.

Course:      Data Structures and Algorithms for Computational Linguistics 3 WS22/23
Author:      Yin-Yin Cheng (2-person course team; shared implementation)
Honor Code:  I pledge that this program represents my own work.
I received help from: no one in designing and debugging my program.
"""

import numpy as np


def cost(ch1, ch2, counts=None):
    """Given two aligned characters, return cost for ch1 -> ch2.

    This function should be called from the find_edits() function
    below when calculating costs for the edit operations.  If the
    first character is the empty string, it indicates an insert.
    Similarly an empty string as the second character indicates a
    deletion.

    If `counts` is not given, the function should return 1 for all
    operations. if `counts` is given, you are strongly recommended to
    use estimated probability p of the edit operation from the given
    counts, and return `1 - p` as the cost (you should also consider
    using a smoothing technique). You are also welcome to
    experiment with other scoring functions.

    """
    if ch1 == "" or ch2 == "":
        return 1
    if ch1 == ch2:
        return 0
    if counts is None or len(counts) == 0:
        return 1
    else:
        if ch1 in counts and ch2 in counts[ch1]:
            return 1 - (counts[ch1][ch2] + 1) / (
                sum(counts[ch1].values()) + len(counts[ch1])
            )
        else:
            return 1


def find_edits(s1, s2, counts=None):
    """Find edits with minimum cost for given sequences.

    This function should implement the edit distance algorithm, using
    the scoring function above. If `counts` is given, the scoring
    should be based on the counts edits passed.

    The return value from this function should be a list of tuples.
    For example if the best alignment between correct word `work` and
    the misspelling `wrok` is as follows

                        wor-k
                        w-rok

    the return value should be
    [('w', 'w'), ('o', ''), ('r', 'r'), ('', o), ('k', 'k')].

    Parameters
    ---
    s1      The source sequences.
    s2      The target sequences.
    counts  A dictionary of dictionaries with counts of edit
            operations (see assignment description for more
            information and an example)
    """
    # levenstein distance for strings s1 and s2

    dp = np.zeros((len(s1) + 1, len(s2) + 1))
    dp[0, :] = np.arange(len(s2) + 1)
    dp[:, 0] = np.arange(len(s1) + 1)

    for i in range(1, len(s1) + 1):
        for j in range(1, len(s2) + 1):
            dp[i, j] = min(
                dp[i - 1, j] + cost(s1[i - 1], "", counts),
                dp[i, j - 1] + cost("", s2[j - 1], counts),
                dp[i - 1, j - 1] + cost(s1[i - 1], s2[j - 1], counts),
            )

    # print(dp)

    i = len(s1)
    j = len(s2)
    edits = []
    while i > 0 and j > 0:
        if dp[i, j] == dp[i - 1, j] + cost(s1[i - 1], "", counts):
            edits.append((s1[i - 1], ""))
            i -= 1
        elif dp[i, j] == dp[i, j - 1] + cost("", s2[j - 1], counts):
            edits.append(("", s2[j - 1]))
            j -= 1
        else:
            edits.append((s1[i - 1], s2[j - 1]))
            i -= 1
            j -= 1

    while i > 0:
        edits.append((s1[i - 1], ""))
        i -= 1

    while j > 0:
        edits.append(("", s2[j - 1]))
        j -= 1

    return edits[::-1]


def count_edits(filename, counts=None):
    """Calculate and return pairs of letters aligned by find_edits().

    Parameters
    ---
    filename    A file containing word - misspelling pairs.
                One pair per line, pairs separated by tab.
    counts      If given use as initial counts.
    """
    if counts is None:
        counts = {}

    with open(filename, "rt") as f:
        for line in f:
            line = line.strip()
            if line:
                word, misspelling = line.split("\t")
                edits = find_edits(word, misspelling, counts)
                for ch1, ch2 in edits:
                    if ch1 not in counts:
                        counts[ch1] = {}
                    if ch2 not in counts[ch1]:
                        counts[ch1][ch2] = 0
                    counts[ch1][ch2] += 1

    return counts


if __name__ == "__main__":
    # The code below shows the intended use of your implementation above.
    import json

    counts = None
    counts_new = count_edits("spelling-data.txt")
    while counts != counts_new:
        counts = counts_new
        counts_new = count_edits("spelling-data.txt", counts)
    with open("spell-errors.json", "wt") as f:
        json.dump(counts, f, ensure_ascii=False, indent=2)
