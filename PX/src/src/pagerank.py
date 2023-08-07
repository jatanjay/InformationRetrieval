"""
jatan pandya
page-rank PX, 7/12/2023
"""

import sys
import gzip
from numpy import array
from numpy.linalg import norm


def do_pagerank_to_convergence(input_file, lamb, tau, inlinks_file, pagerank_file, k):
    with gzip.open(input_file, "rb") as file:
        fout = file.read().decode("utf-8")
    links = fout.strip().split("\n")

    # Build Index
    P = {}
    for line in links:
        line = line.split("\t")
        if len(line) == 2 and all(line):
            P.setdefault(line[0].strip("\r"), []).append(line[1].strip("\r"))
            P.setdefault(line[1].strip("\r"), [])

    G = {page: index for index, page in enumerate(P)}
    I = [1 / len(P)] * len(P)

    while True:
        res = 0
        R = [lamb / len(P)] * len(P)
        for page in P:
            Q = P[page]
            if len(Q) > 0:
                for curr_page in Q:
                    R[G[curr_page]] += (1 - lamb) * (I[G[page]] / len(Q))
            else:
                res += (1 - lamb) * (I[G[page]] / len(P))

        for curr_index in range(len(R)):  # out of loop
            R[curr_index] += res

        norm_res = norm(array(R) - array(I), ord=2)
        if norm_res < tau:
            break
        I = R

    pageRank = [[i, R[G[i]]] for i in G]

    pageRank = sorted(pageRank, key=lambda x: (-x[1], x[0]), reverse=False)
    with open(pagerank_file, "w+", encoding="utf-8") as pout:
        for i, (page, rank) in enumerate(pageRank[:k]):
            line = f"{page}\t{i+1}\t{rank:.12f}\n"
            pout.write(line)

    res = [0] * len(P)
    for _, outlinks in P.items():
        for outlink in outlinks:
            res[G[outlink]] += 1

    inLink = [[key, res[G[key]]] for key in P]
    inLink = sorted(inLink, key=lambda x: (-int(x[1]), x[0]))

    with open(inlinks_file, "w+", encoding="utf-8") as iout:
        for i, (page, inlinks) in enumerate(inLink[:k]):
            line = f"{page}\t{i+1}\t{inlinks}\n"
            iout.write(line)


def do_pagerank_n_times(input_file, lamb, N, inlinks_file, pagerank_file, k):
    with gzip.open(input_file, "rb") as file:
        fout = file.read().decode("utf-8")
    links = fout.strip().split("\n")

    # Build Index
    P = {}
    for line in links:
        line = line.split("\t")
        if len(line) == 2 and all(line):
            P.setdefault(line[0].strip("\r"), []).append(line[1].strip("\r"))
            P.setdefault(line[1].strip("\r"), [])

    G = {page: index for index, page in enumerate(P)}
    I = [1 / len(P)] * len(P)

    iters = 0
    while iters < N:
        res = 0
        R = [lamb / len(P)] * len(P)
        for page in P:
            Q = P[page]
            if len(Q) > 0:
                for curr_page in Q:
                    R[G[curr_page]] += (1 - lamb) * (I[G[page]] / len(Q))
            else:
                res += (1 - lamb) * (I[G[page]] / len(P))

        for curr_index in range(len(R)):
            R[curr_index] += res

        I = R
        iters += 1

    pageRank = [[i, R[G[i]]] for i in G]
    pageRank = sorted(pageRank, key=lambda x: (-x[1], x[0]), reverse=False)
    with open(pagerank_file, "w+", encoding="utf-8") as pout:
        for i, (page, rank) in enumerate(pageRank[:k]):
            line = f"{page}\t{i+1}\t{rank:.12f}\n"
            pout.write(line)

    res = [0] * len(P)
    for _, outlinks in P.items():
        for outlink in outlinks:
            res[G[outlink]] += 1

    inLink = [[key, res[G[key]]] for key in P]
    inLink = sorted(inLink, key=lambda x: (-int(x[1]), x[0]))

    with open(inlinks_file, "w+", encoding="utf-8") as iout:
        for i, (page, inlinks) in enumerate(inLink[:k]):
            line = f"{page}\t{i+1}\t{inlinks}\n"
            iout.write(line)


def main():
    argc = len(sys.argv)
    input_file = (
        sys.argv[1]
        if argc > 1
        else r"C:\Users\jayes\Desktop\Spring 23\446\PX\src\links.srt.gz"
    )
    lamb = float(sys.argv[2]) if argc > 2 else 0.2

    tau = 0.005
    N = -1  # signals to run until convergence
    if argc > 3:
        arg = sys.argv[3]
        if arg.lower().startswith("exactly"):
            N = int(arg.split(" ")[1])
        else:
            tau = float(arg)

    inlinks_file = sys.argv[4] if argc > 4 else "inlinks.txt"
    pagerank_file = sys.argv[5] if argc > 5 else "pagerank.txt"
    k = int(sys.argv[6]) if argc > 6 else 100

    if N == -1:
        do_pagerank_to_convergence(
            input_file, lamb, tau, inlinks_file, pagerank_file, k
        )
    else:
        do_pagerank_n_times(input_file, lamb, N, inlinks_file, pagerank_file, k)


if __name__ == "__main__":
    main()
