"""
jatan pandya
7/24


The need to handle phrases means your index must contain position information about 
the words as well as their presence. The need to handle QL and BM25 queries means you will also want to include term 
count information in your index. You will also generate a graph regarding how a particular set of words are used across the corpus.
"""

"""
corpus: 
{
    "corpus": [
        {
            "article": "8951",
            "storyID": "8951-id_1",
            "storynum": "id_1",
            "url": "https://www.gutenberg.org/cache/epub/8951/pg8951-images.html#id_1",
            "text": "improvement in hull and cleanse hominy many of our reader well remember when hull corn was a standing winter dish this was corn or maize the kernel of which were denude of their hull by the chemical action of alka which however impair the sweet of the food hominy is corn deprived of the hull by mechanical means leave the corn with all its original flavor unimpaired hominy is a favorite dish throughout the country but is not always entire free from particle of the outer skin of the kernel the mill shown in perspective in the engraving is intended to obviate this objection  picture of donaldson s patent hominy mill donaldson s patent hominy mill the corn is placed in the hopper a from which it is fed to the hull cylinder contained in the case b the hull machinery is driven by a belt on the pulley c the other end of the shaft of which carry a pinion which give motion to the gear wheel d this by means of a pinion on the shaft of the blower e drive the fan of the blower on the other or front end of the shaft which carry the gear d is a bevel gear by which another bevel gear and worm is turn the worm rotate the worm gear f in two opposite arms of which are slot that carry pin project inwards which may be move toward or away from the center this gear wheel turn free on the shaft that carry the pulley c and is intended for opening by means of the pin in the arms and lever a cover in the bottom of the hopper and a valve in the bottom of the hull cylinder coil or bent spring return these lever or valve to place when the pin which move them has pass a wrist pin on the gear d form a crank which is connected to a bar at the rear end of the sieve g pivot to an arm at h by which the sieve have a shake or reciprocate motion as the machine operate the blower drive out the hull and the motion of the sieve with their inclined position insure access of the air to every portion of the hominy it will be notice that the connection of all the parts is absolute the motion of the sieve the speed of the blower and the action of the inlet hopper valve and the delivery hull valve are always exactly proportion to the speed of the hull cylinder whether fast or slow the upper or feed valve open upward and has a downward project lip that shut into a recess in its seat which insure security against leakage from the hopper to the hull cylinder during the interval of its being raise a great advantage in hominy making as no grain ought to get into the batch until that in the cylinder is done patent oct 15 1867 by john donaldson who may be address for further information at rockford ill   "
        },
    ]
}

"""

import sys
import json
import gzip
import re
import math
from collections import defaultdict


def buildIndex(inputFile):
    invertedIndex = defaultdict(lambda: defaultdict(list))
    totalWords, totalDocs = 0, 0
    longestDocument, shortestDocument = None, None

    try:
        with gzip.open(inputFile, "r") as f:
            corpusData = json.load(f)
    except (IOError, json.JSONDecodeError):
        print("Error loading the input file.")
        return None

    print("building index")

    for document in corpusData["corpus"]:
        text = re.split(r"\s+", document["text"])
        text = [x.strip() for x in text if x.strip()]
        docWords = len(text)
        totalWords += docWords
        totalDocs += 1

        invertedIndex["api"][document["storyID"]] = docWords  # For bm25

        if longestDocument is None or docWords > longestDocument:
            longestDocument = docWords
        if shortestDocument is None or docWords < shortestDocument:
            shortestDocument = docWords

        for i, term in enumerate(text, start=1):
            if term:
                invertedIndex[term][document["storyID"]].append(i)

    avgWordsPerDoc = totalWords / totalDocs

    invertedIndex["api"].update(
        {
            "totalWords": totalWords,
            "totalDocs": totalDocs,
            "avgWordsPerDoc": avgWordsPerDoc,
            "longestDocument": longestDocument,
            "shortestDocument": shortestDocument,
        }
    )

    with open("inverted_index.json", "w", encoding="utf-8") as fout:
        json.dump(invertedIndex, fout)
    print("index built")

    return invertedIndex


def isPhrase(index, wordList, startIndex, docName):
    for i in range(len(wordList)):
        word = wordList[i]
        if docName not in index.get(word, {}):
            return False
        elif startIndex + i not in index[word][docName]:
            return False
    return True


def find_adjacent_positions(positions_a, positions_b):
    adjacent_positions = []
    for pos_a in positions_a:
        for pos_b in positions_b:
            if pos_b == pos_a + 1:
                adjacent_positions.append(pos_b)
    return adjacent_positions


def find_positions_for_phrase(phrase, invertedIndex):
    positions = set()
    words = phrase.split()
    if len(words) == 1:
        return set(invertedIndex.get(phrase, {}).keys())

    for doc_id, doc_positions in invertedIndex.get(words[0], {}).items():
        for i in range(1, len(words)):
            next_word_positions = set(invertedIndex.get(words[i], {}).get(doc_id, []))
            doc_positions = find_adjacent_positions(doc_positions, next_word_positions)

        if doc_positions:
            positions.add(doc_id)
    return positions


def qAnd(invertedIndex, search_terms):
    first_term = search_terms[0]
    result = set(invertedIndex.get(first_term, {}).keys())

    if result:
        for term in search_terms[1:]:
            term_docs = set(invertedIndex.get(term, {}).keys())
            result = result.intersection(term_docs)

    return sorted(result)


def qOr(invertedIndex, search_terms):
    first_term = search_terms[0]
    result = set()

    if first_term:
        for term in search_terms:
            term_positions = find_positions_for_phrase(term, invertedIndex)
            result = result.union(term_positions)

    return sorted(result)


def bm25(inverted_index, search_terms):
    # that is, any story that includes at least one of the query
    docs = qOr(inverted_index, search_terms)
    scored_docs = []

    # k1=1.8, k2=5, b=0.75
    k1 = 1.8
    k2 = 5
    b = 0.75

    R = 0  # given
    r = 0  # given
    N = inverted_index["api"]["totalDocs"]

    freq_dict = defaultdict(int)
    for term in search_terms:
        freq_dict[term] += 1

    for doc in docs:
        bmscore = 0
        # things needed to cal K:
        # k1, b, dl, avdl (have k1, b)
        dl = inverted_index["api"][doc]  # doc length
        avdl = inverted_index["api"]["avgWordsPerDoc"]
        K = k1 * ((1 - b) + b * (dl / avdl))

        # so now, i got stuff for each doc, now run for each query
        for term in search_terms:
            # fi is the frequency of term i in the document;
            # qfi is the frequency of term i in the query
            qfi = freq_dict[term]

            n = (
                len(inverted_index[term])
                if " " not in term
                else len(qOr(inverted_index, [term]))
            )

            if " " not in term:
                if doc not in inverted_index[term]:
                    f = 0
                else:
                    f = len(inverted_index[term][doc])

            # i got f, n, qfi for a single querry
            # same for phrase querrey

            else:
                f = 0
                res = term.split()
                first_term = res[0]
                if doc in inverted_index[first_term]:
                    for i in inverted_index[first_term][doc]:
                        if isPhrase(inverted_index, res, i, doc) == True:
                            f += 1

            t1_num = (r + 0.5) / (R - r + 0.5)
            t1_denom = (n - r + 0.5) / (N - n - R + r + 0.5)
            t1 = t1_num / t1_denom

            t2_num = (k1 + 1) * f
            t2_denom = K + f
            t2 = t2_num / t2_denom

            t3_num = (k2 + 1) * qfi
            t3_denom = k2 + qfi
            t3 = t3_num / t3_denom

            res = math.log(t1) * t2 * t3
            bmscore += res
        scored_docs.append([doc, bmscore])
    scored_docs = sorted(scored_docs, key=lambda x: (x[1], x[0]), reverse=True)
    return scored_docs


def qQL(inverted_index, search_term):
    mu = 300
    res = {}
    docs = qOr(inverted_index, search_term)
    scored_docs = []

    api_total_words = inverted_index["api"]["totalWords"]
    api_doc_lengths = {doc: inverted_index["api"][doc] for doc in docs}

    for doc in docs:
        score = 0
        doc_length = api_doc_lengths[doc]

        for term in search_term:
            f = 0
            c = 0

            if " " not in term:
                if doc in inverted_index[term]:
                    f = len(inverted_index[term][doc])
                c = res.get(term, 0)

            else:
                phrase = term.split()
                if doc in inverted_index[phrase[0]]:
                    for i in inverted_index[phrase[0]][doc]:
                        if isPhrase(inverted_index, phrase, i, doc):
                            f += 1
                    c = res.get(term, 0)

            if not c:
                if " " not in term:
                    c = sum(len(inverted_index[term][x]) for x in inverted_index[term])
                else:
                    phrase = term.split()
                    c = sum(
                        1
                        for x in inverted_index[phrase[0]]
                        if any(
                            isPhrase(inverted_index, phrase, i, x)
                            for i in inverted_index[phrase[0]][x]
                        )
                    )
                res[term] = c

            num = f + mu * c / api_total_words
            denom = doc_length + mu
            lhs = num / denom
            score += math.log(lhs)

        scored_docs.append([doc, score])

    scored_docs = sorted(scored_docs, key=lambda x: (x[1], x[0]), reverse=True)
    return scored_docs


def runQueries(index, queriesFile, outputFile):
    # rember to split the phrase and handle whatever
    with open(outputFile, "w") as fout:
        with open(queriesFile, "r") as queryFile:
            for line in queryFile:
                line = line.rstrip("\n")
                line = line.split("\t")

                queryType, queryName = line[0], line[1]
                search_terms = line[2:]

                if queryType.lower() == "and":
                    bool_and = qAnd(index, search_terms)
                    fout.writelines(
                        "{: <8} skip {: <20} {: <5} {:.3f} jpandya\n".format(
                            queryName, result, str(i + 1), 1.0
                        )
                        for i, result in enumerate(bool_and)
                    )
                elif queryType.lower() == "or":
                    bool_or = qOr(index, search_terms)
                    fout.writelines(
                        "{: <8} skip {: <20} {: <5} {:.3f} jpandya\n".format(
                            queryName, result, str(i + 1), 1.0
                        )
                        for i, result in enumerate(bool_or)
                    )

                elif queryType.lower() == "ql":
                    q_ql = qQL(index, search_terms)
                    fout.writelines(
                        "{: <8} skip {: <20} {: <5} {:.4f} jpandya\n".format(
                            queryName, result[0], str(i + 1), result[1]
                        )
                        for i, result in enumerate(q_ql)
                    )
                elif queryType.lower() == "bm25":
                    q_bm25 = bm25(index, search_terms)
                    fout.writelines(
                        "{: <9} skip {: <20} {: <5} {:.4f} jpandya\n".format(
                            queryName, result[0], str(i + 1), result[1]
                        )
                        for i, result in enumerate(q_bm25)
                    )


if __name__ == "__main__":
    # Read arguments from command line, or use sane defaults for IDE.
    argv_len = len(sys.argv)
    inputFile = (
        sys.argv[1]
        if argv_len >= 2
        else r"C:\Users\jayes\Desktop\Spring 23\446\P3\P3python\sciam.json.gz"
    )
    # queriesFile = sys.argv[2] if argv_len >= 3 else "trainQueries.tsv"
    queriesFile = (
        sys.argv[2]
        if argv_len >= 3
        else r"C:\Users\jayes\Desktop\Spring 23\446\P3\P3python\P3train.tsv"
    )

    outputFile = sys.argv[3] if argv_len >= 4 else "P3train.trecrun"

    index = buildIndex(inputFile)
    runQueries(index, queriesFile, outputFile)
