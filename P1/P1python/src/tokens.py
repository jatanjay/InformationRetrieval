"""
Jatan Pandya
446
James Allen
7/4/2023

"""

import sys
import gzip
import string
import re
from collections import Counter

PUNCT = string.punctuation
VOWELS = ["a", "e", "i", "o", "u", "y"]

stopword_lst = [
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "he",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "that",
    "the",
    "to",
    "was",
    "were",
    "with",
]


def gzHandler(gzfile):
    corpus = []
    spaced_corpus = []
    with gzip.open(gzfile, "rt") as f:
        for line in f:
            corpus.append(line)
    for line in corpus:  # [line, line]
        split_line = line.split(sep=" ")  # split_line = ['','']
        for tok in split_line:
            tok = tok.strip()
            if tok:
                spaced_corpus.append(tok.strip())  # master corpus containing all words
    return spaced_corpus


def tokenizer(token, tokenize):
    if tokenize == "spaces":
        return token

    if tokenize == "fancy":
        res = []
        is_number = False
        is_url = False

        # URL
        if re.search(r"https?://", token):
            is_url = True
            if token[-1] in PUNCT:
                token = token.strip(PUNCT)
                res.append(token)
                return res  # do no other procesing
            token = token.strip(PUNCT)
            res.append(token.strip())
            return res

        else:
            res_tok = token.lower()
            res_tok = res_tok.strip()
            # Is number (can contain + - , . but at least one digit)
            if re.search(r"^(?=.*\d)[\d,+\-.]*$", res_tok):
                is_number = True
                res.append(res_tok)
                return res

            if not is_number:
                # Apostrophes
                if re.search(r"(’|'|`)", res_tok):
                    res_tok = re.sub(r"(’|'|`)", "", res_tok)
                    res.append(res_tok)

                # Abbreviations
                if not is_number and not is_url:
                    all_punc = set(re.findall(r"[^\w\s]", res_tok))
                    if len(all_punc) == 1 and "." in all_punc:
                        res_tok = re.sub(r"\.", "", res_tok)
                        if res_tok:
                            res.append(res_tok)

                # Hyphens
                hyphen_temp = re.split(r"\-", res_tok)
                if len(hyphen_temp) > 1:
                    hyphen_temp.append(res_tok.replace("-", ""))
                    for ht in hyphen_temp:
                        recursive_res = tokenizer(ht, "fancy")
                        for rr in recursive_res:
                            res.append(rr)
                    return res

                # Other punctuation
                res_punct = re.split("[^a-zA-Z0-9\.\-]", res_tok)
                if res_punct:
                    if "" in res_punct:
                        res_punct.remove("")
                        for r_p in res_punct:
                            recursive_res = tokenizer(r_p, "fancy")
                            for rr in recursive_res:
                                res.append(rr)
                        return res
                return res_punct


def PorterStemmer(token, stemType):
    if stemType == "noStem":
        return token

    if stemType == "porterStem":
        one_c_flag = False

        # step 1a

        ## pt. 1
        if token.endswith("sses"):
            token = re.sub(r"sses$", "ss", token)

        ##  pt. 2
        elif token.endswith("ied") or token.endswith("ies"):
            if re.search(r"(?<!\b\w)\w{2,}(ied|ies)$", token):
                token = re.sub(r"(ied|ies)$", "i", token)
            else:
                token = re.sub(r"(ied|ies)$", "ie", token)

        ## pt. 3
        elif token.endswith("us") or token.endswith("ss"):
            token = token

        ## pt. 4
        elif token.endswith("s"):
            if token.endswith("s") and any(char in VOWELS for char in token[:-2]):
                token = token[:-1]
            else:
                token = token

        # step 1b
        if token.endswith("eed") or token.endswith("eedly"):
            stem = re.sub(r"(eed|eedly)$", "", token)
            VC_flag = False
            for i in range(1, len(stem)):
                if stem[i] not in VOWELS and stem[i - 1] in VOWELS:
                    VC_flag = True

            if VC_flag:
                token = re.sub(r"(eed|eedly)$", "ee", token)
                one_c_flag = True

        elif re.search(r"(ed|edly|ing|ingly)$", token):
            pattern = r"^(.*?[aeiouy].*?)(ed|edly|ing|ingly)$"
            obj = re.match(pattern, token)
            if obj:
                token = obj.group(1)

                ###############################################################

                # check if stem is short
                is_short = False

                vc_pattern = r"[aeiouy][^aeiouy]$"
                cc_v_c_pattern = r"[^aeiouy]+[aeiouy][^aeiouywx]$"

                if len(token) == 2:
                    if re.match(vc_pattern, token):
                        is_short = True
                else:
                    ## could be CC*VC (where last c cant be w,x)
                    if bool(re.match(cc_v_c_pattern, token)):
                        is_short = True
                ###############################################################

                # if stem ends in at,bl,iz -- add e
                if re.search(r"(at|bl|iz)$", token):
                    token += "e"
                    one_c_flag = True

                # dobule letter ending
                elif re.search(r"(bb|dd|ff|gg|mm|nn|pp|rr|tt)$", token):
                    token = token[:-1]
                    one_c_flag = True

                # if short
                elif is_short == True:
                    token += "e"
                    one_c_flag = True
                else:
                    one_c_flag = True
            else:
                one_c_flag = True
        else:
            one_c_flag = True

        # Step 1c
        if one_c_flag == True:
            if len(token) > 2:
                if token[-1] == "y":
                    if token[-2] not in VOWELS:
                        token = token[:-1] + "i"

    return token.strip()


def main(input_corpus, tokenize_type, stoplist_type, stemming_type):
    all_tokens = []

    for token in input_corpus:
        token = token.strip()
        all_tokens.append([token])

        if tokenize_type == "spaces" and stoplist_type == "yesStop":
            if token not in stopword_lst:
                if stemming_type == "porterStem":
                    all_tokens[-1].append(PorterStemmer(token, stemType=stemming_type))
                elif stemming_type == "noStem":
                    all_tokens[-1].append(token)  # simple spaced token

        elif tokenize_type == "spaces" and stoplist_type == "noStop":
            # no stopping
            if stemming_type == "porterStem":
                all_tokens[-1].append(PorterStemmer(token, stemType=stemming_type))
            elif stemming_type == "noStem":
                all_tokens[-1].append(token)  # simple spaced token

        elif tokenize_type == "fancy":
            fancy_tokenized = tokenizer(token=token, tokenize=tokenize_type)

            if stoplist_type == "yesStop":
                fancy_tokenized = [x for x in fancy_tokenized if x not in stopword_lst]

            if stemming_type == "porterStem":
                fancy_tokenized = [
                    PorterStemmer(x, stemType="porterStem") for x in fancy_tokenized
                ]

            for s in fancy_tokenized:
                all_tokens[-1].append(s.strip())
    return all_tokens


def fileGen(all_tokens, outputFilePrefix):
    # Generate outputPrefix-tokens.txt
    with open(f"{outputFilePrefix}-tokens.txt", "w") as tokens_file:
        for token_list in all_tokens:
            tokens_file.write(" ".join(token_list) + "\n")

    # Generate outputPrefix-heaps.txt
    with open(f"{outputFilePrefix}-heaps.txt", "w") as heaps_file:
        token_count = 0
        unique_tokens = set()
        for i, token_list in enumerate(all_tokens, 1):
            token_count += len(token_list) - 1
            unique_tokens.update(token_list[1:])
            if i % 10 == 0:
                heaps_file.write(f"{token_count} {len(unique_tokens)}\n")
        if i % 10 != 0:
            heaps_file.write(f"{token_count - 1} {len(unique_tokens)-1}\n")

    counter = Counter()
    for tok in all_tokens:
        if len(tok) >= 1:  # doesn't have any '' resultant toks:
            for i in range(1, len(tok)):
                if tok[i] in counter:
                    counter[tok[i]] += 1
                else:
                    counter[tok[i]] = 1

    total_tokens = sum(counter.values()) - 1
    total_unique_tokens = len(counter) - 1
    res = sorted([[counter[rx], rx] for rx in counter], key=lambda x: (-x[0], x[1]))

    with open(f"{outputFilePrefix}-stats.txt", "w") as file:
        file.write(f"{total_tokens}\n")
        file.write(f"{total_unique_tokens}\n")
        for item in sorted(res, key=lambda x: (-x[0], x[1]))[:100]:
            file.write(item[1] + " " + str(item[0]) + "\n")


if __name__ == "__main__":
    argv_len = len(sys.argv)
    inputFile = (
        sys.argv[1] if argv_len >= 2 else "P1python\src\sense-and-sensibility.gz"
    )
    outputFilePrefix = sys.argv[2] if argv_len >= 3 else "SAS"
    tokenize_type = sys.argv[3] if argv_len >= 4 else "fancy"
    stoplist_type = sys.argv[4] if argv_len >= 5 else "yesStop"
    stemming_type = sys.argv[5] if argv_len >= 6 else "porterStem"

    input_corpus = gzHandler(inputFile)
    required_tokens = main(
        input_corpus=input_corpus,
        tokenize_type=tokenize_type,
        stoplist_type=stoplist_type,
        stemming_type=stemming_type,
    )
    fileGen(all_tokens=required_tokens, outputFilePrefix=outputFilePrefix)
