def qQL(inverted_index, search_term):
    mu = 300
    res = dict()
    docs = qOr(inverted_index, search_term)
    scored_docs = []
    for doc in docs:
        score = 0
        for term in search_term:
            f = 0
            if " " not in term:
                if doc in inverted_index[term]:
                    f = len(inverted_index[term][doc])
            else:
                phrase = term.split()
                if doc in inverted_index[phrase[0]]:
                    for i in inverted_index[phrase[0]][doc]:
                        if isPhrase(inverted_index, phrase, i, doc) == True:
                            f += 1

            if term not in res:
                if " " not in term:
                    c = 0
                    for x in inverted_index[term]:
                        c = c + len(inverted_index[term][x])
                    res[term] = c
                else:
                    phrase = term.split()
                    c = 0
                    for x in inverted_index[phrase[0]]:
                        for i in inverted_index[phrase[0]][x]:
                            if isPhrase(inverted_index, phrase, i, x) == True:
                                c += 1
            else:
                c = res[term]
            C = inverted_index["api"]["totalWords"]
            D = inverted_index["api"][doc]
            num = f + mu * c / C
            denom = D + mu
            lhs = num / denom
            lhs = math.log(lhs)
            score += lhs
        scored_docs.append([doc, score])
    scored_docs = sorted(scored_docs, key=lambda x: (x[1], x[0]), reverse=True)
    return scored_docs
