import math
import sys


def calculate_ndcg_at_k(queryname, trec_data, qrels_data, k=20):
    if queryname not in trec_data or queryname not in qrels_data:
        return 0.0

    trec_results = trec_data[queryname]
    qrels = qrels_data[queryname]
    num_rel = sum(1 for docid, relevance in qrels.items() if relevance > 0)

    if num_rel == 0:
        return 0.0

    dcg_at_k = qrels.get(trec_results[0]["docid"], 0)  # rel1
    dcg_at_k += sum(
        relevance / math.log2(i)
        for i, doc in enumerate(trec_results[1:k], start=2)
        for docid, relevance in qrels.items()
        if docid == doc["docid"]
    )

    sorted_qrels = sorted(qrels.items(), key=lambda x: x[1], reverse=True)[:k]

    if not sorted_qrels:
        return 0.0

    idcg_at_k = sorted_qrels[0][1]  # rel1
    idcg_at_k += sum(
        relevance / math.log2(i)
        for i, (_, relevance) in enumerate(sorted_qrels[1:], start=2)
    )

    ndcg_at_k = dcg_at_k / idcg_at_k
    return ndcg_at_k


def calculate_rr(queryname, trec_data, qrels_data):
    if queryname not in trec_data or queryname not in qrels_data:
        return 0.0

    trec_results = trec_data[queryname]
    qrels = qrels_data[queryname]

    num_rel = sum(1 for relevance in qrels.values() if relevance > 0)
    rel_found = sum(1 for doc in trec_results if qrels.get(doc["docid"], 0) > 0)

    if rel_found == 0:
        return 0.0

    if rel_found < 0:
        return 1.000

    rr = 1.0 / rel_found
    return rr


def calculate_p_at_10(queryname, trec_data, qrels_data):
    if queryname not in trec_data or queryname not in qrels_data:
        return 0.0

    trec_results = trec_data[queryname]
    qrels = qrels_data[queryname]

    num_rel = sum(1 for relevance in qrels.values() if relevance > 0)

    rel_found = sum(1 for doc in trec_results[:10] if qrels.get(doc["docid"], 0) > 0)

    p_at_10 = rel_found / 10.0
    return p_at_10


def calculate_recall_at_10(queryname, trec_data, qrels_data):
    if queryname not in trec_data or queryname not in qrels_data:
        return 0.0

    trec_results = trec_data[queryname]
    qrels = qrels_data[queryname]

    num_rel = sum(1 for relevance in qrels.values() if relevance > 0)

    if num_rel == 0:
        return 0.0

    rel_found = sum(1 for doc in trec_results[:10] if qrels.get(doc["docid"], 0) > 0)

    recall_at_10 = rel_found / float(num_rel)
    return recall_at_10


def calculate_f1_at_10(queryname, trec_data, qrels_data):
    if queryname not in trec_data or queryname not in qrels_data:
        return 0.0

    trec_results = trec_data[queryname]
    qrels = qrels_data[queryname]

    num_rel = sum(1 for relevance in qrels.values() if relevance > 0)

    if num_rel == 0:
        return 0.0

    rel_found = sum(1 for doc in trec_results[:10] if qrels.get(doc["docid"], 0) > 0)

    precision_at_10 = rel_found / 10.0
    recall_at_10 = rel_found / float(num_rel)

    if precision_at_10 == 0 or recall_at_10 == 0:
        return 0.0
    f1_at_10 = 2 * (precision_at_10 * recall_at_10) / (precision_at_10 + recall_at_10)

    return f1_at_10


def calculate_p_at_20_percent_recall(queryname, trec_data, qrels_data):
    if queryname not in trec_data or queryname not in qrels_data:
        return 0.0

    trec_results = trec_data[queryname]
    qrels = qrels_data[queryname]

    num_rel = sum(1 for relevance in qrels.values() if relevance > 0)

    if num_rel == 0:
        return 0.0

    rel_found = sum(1 for doc in trec_results if qrels.get(doc["docid"], 0) > 0)

    p_at_20_percent_recall = 0.0

    for k in range(1, len(trec_results) + 1):
        rel_found_k = sum(
            1 for doc in trec_results[:k] if qrels.get(doc["docid"], 0) > 0
        )
        recall_k = rel_found_k / float(num_rel)
        precision_k = rel_found_k / float(k)

        if recall_k >= 0.20:
            p_at_20_percent_recall = max(p_at_20_percent_recall, precision_k)

    return p_at_20_percent_recall


def calculate_average_precision(queryname, trec_data, qrels_data):
    if queryname not in trec_data or queryname not in qrels_data:
        return 0.0

    trec_results = trec_data[queryname]
    qrels = qrels_data[queryname]

    num_rel = sum(1 for relevance in qrels.values() if relevance > 0)

    if num_rel == 0:
        return 0.0

    rel_found = sum(1 for doc in trec_results if qrels.get(doc["docid"], 0) > 0)

    avg_precision = 0.0
    relevant_count = 0

    for k, doc in enumerate(trec_results):
        if qrels.get(doc["docid"], 0) > 0:
            relevant_count += 1
            precision_k = relevant_count / float(k + 1)
            avg_precision += precision_k

    avg_precision /= num_rel

    return avg_precision


def eval(trecrunFile, qrelsFile, output_file):
    trec = {}
    qrel = {}

    with open(trecrunFile, "r") as file:
        for line in file:
            queryname, _, docid, rank, score, _ = line.strip().split()
            rank = int(rank)
            score = float(score)

            if queryname not in trec:
                trec[queryname] = []

            trec[queryname].append({"docid": docid, "rank": rank, "score": score})

    # Reading qrels file
    with open(qrelsFile, "r") as file:
        for line in file:
            queryname, _, docid, relevance = line.strip().split()
            relevance = int(relevance)

            if queryname not in qrel:
                qrel[queryname] = {}

            qrel[queryname][docid] = relevance

    trec_data = trec
    qrels_data = qrel

    metrics_per_query = {}
    num_rel_sum = 0
    rel_found_sum = 0
    ndcg_at_k_sum = 0.0
    rr_sum = 0.0
    p_at_10_sum = 0.0
    recall_at_10_sum = 0.0
    f1_at_10_sum = 0.0
    p_at_20_percent_recall_sum = 0.0
    ap_sum = 0.0

    with open(output_file, "w") as f:
        for queryname in trec_data:
            trec_results = trec_data[queryname]
            qrels = qrels_data[queryname]

            num_rel = sum(1 for relevance in qrels.values() if relevance > 0)
            rel_found = sum(1 for doc in trec_results if qrels.get(doc["docid"], 0) > 0)

            num_rel_sum += num_rel
            rel_found_sum += rel_found

            ndcg_at_k = calculate_ndcg_at_k(queryname, trec_data, qrels_data)
            rr = calculate_rr(queryname, trec_data, qrels_data)
            p_at_10 = calculate_p_at_10(queryname, trec_data, qrels_data)
            recall_at_10 = calculate_recall_at_10(queryname, trec_data, qrels_data)
            f1_at_10 = calculate_f1_at_10(queryname, trec_data, qrels_data)
            p_at_20_percent_recall = calculate_p_at_20_percent_recall(
                queryname, trec_data, qrels_data
            )
            ap = calculate_average_precision(queryname, trec_data, qrels_data)

            metrics_per_query[queryname] = {
                "NDCG@20": ndcg_at_k,
                "numRel": num_rel,
                "relFound": rel_found,
                "RR": rr,
                "P@10": p_at_10,
                "Recall@10": recall_at_10,
                "F1@10": f1_at_10,
                "P@20%": p_at_20_percent_recall,
                "AP": ap,
            }

            ndcg_at_k_sum += ndcg_at_k
            rr_sum += rr
            p_at_10_sum += p_at_10
            recall_at_10_sum += recall_at_10
            f1_at_10_sum += f1_at_10
            p_at_20_percent_recall_sum += p_at_20_percent_recall
            ap_sum += ap

            f.write(
                f"NDCG@20   {queryname:<10}   {metrics_per_query[queryname]['NDCG@20']:.4f}\n"
            )
            f.write(
                f"numRel    {queryname:<10}   {metrics_per_query[queryname]['numRel']:<10}\n"
            )
            f.write(
                f"relFound  {queryname:<10}   {metrics_per_query[queryname]['relFound']:<10}\n"
            )
            f.write(
                f"RR        {queryname:<10}   {metrics_per_query[queryname]['RR']:.4f}\n"
            )
            f.write(
                f"P@10      {queryname:<10}   {metrics_per_query[queryname]['P@10']:.4f}\n"
            )
            f.write(
                f"R@10      {queryname:<10}   {metrics_per_query[queryname]['Recall@10']:.4f}\n"
            )
            f.write(
                f"F1@10     {queryname:<10}   {metrics_per_query[queryname]['F1@10']:.4f}\n"
            )
            f.write(
                f"P@20%     {queryname:<10}   {metrics_per_query[queryname]['P@20%']:.4f}\n"
            )
            f.write(
                f"AP        {queryname:<10}   {metrics_per_query[queryname]['AP']:.4f}\n"
            )

        num_queries = len(trec_data)
        mean_ndcg_at_k = ndcg_at_k_sum / num_queries
        mean_rr = rr_sum / num_queries
        mean_p_at_10 = p_at_10_sum / num_queries
        mean_recall_at_10 = recall_at_10_sum / num_queries
        mean_f1_at_10 = f1_at_10_sum / num_queries
        mean_p_at_20_percent_recall = p_at_20_percent_recall_sum / num_queries
        mean_ap = ap_sum / num_queries

        f.write(f"NDCG@20    all   {mean_ndcg_at_k:.4f}\n")
        f.write(f"numRel     all   {num_rel_sum}\n")
        f.write(f"relFound   all   {rel_found_sum}\n")
        f.write(f"MRR        all   {mean_rr:.4f}\n")
        f.write(f"P@10       all   {mean_p_at_10:.4f}\n")
        f.write(f"R@10       all   {mean_recall_at_10:.4f}\n")
        f.write(f"F1@10      all   {mean_f1_at_10:.4f}\n")
        f.write(f"P@20%      all   {mean_p_at_20_percent_recall:.4f}\n")
        f.write(f"MAP        all   {mean_ap:.4f}\n")


if __name__ == "__main__":
    argv_len = len(sys.argv)
    runFile = (
        sys.argv[1]
        if argv_len >= 2
        else r"C:\Users\jayes\Desktop\Spring 23\446\P2\P2python\P2python\src\msmarcofull-ql.trecrun"
    )
    qrelsFile = (
        sys.argv[2]
        if argv_len >= 3
        else r"C:\Users\jayes\Desktop\Spring 23\446\P2\P2python\P2python\src\msmarco.qrels"
    )
    outputFile = sys.argv[3] if argv_len >= 4 else "ql.eval"

    eval(runFile, qrelsFile, outputFile)
