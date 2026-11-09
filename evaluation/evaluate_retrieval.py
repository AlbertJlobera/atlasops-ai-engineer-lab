import json
from pathlib import Path

from app.graph.nodes.retrieval import retrieve
from app.graph.nodes.answerability import judge_answerability


GOLDEN_DATASET_PATH = Path(
    r"C:\Ai Proyecto\AI_Engineer_Lab_01_AtlasOps\evaluation\golden_dataset.json"
)


def load_golden_dataset():
    with open(GOLDEN_DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def is_relevant(doc, item):
    source = Path(doc.metadata.get("source", "")).name

    for expected in item.get("expected_chunks", []):

        if source != expected.get("source"):
            continue

        if doc.metadata.get("section") != expected.get("section"):
            continue

        expected_subsection = expected.get("subsection")

        if expected_subsection is not None:
            if doc.metadata.get("subsection") != expected_subsection:
                continue

        return True

    return False


def evaluate_retrieval(golden_dataset):
    hit_at_1 = 0
    hit_at_3 = 0
    mrr_sum = 0
    answerable_count = 0

    for item in golden_dataset:

        if not item["answerable"]:
            continue

        answerable_count += 1

        results = retrieve(
            question=item["question"],
            k=3
        )

        relevant_ranks = []

        for rank, (doc, score) in enumerate(results, start=1):
            if is_relevant(doc, item):
                relevant_ranks.append(rank)

        if 1 in relevant_ranks:
            hit_at_1 += 1

        if relevant_ranks:
            hit_at_3 += 1

            first_relevant_rank = min(relevant_ranks)
            mrr_sum += 1 / first_relevant_rank

    return {
        "hit_at_1": hit_at_1 / answerable_count,
        "hit_at_3": hit_at_3 / answerable_count,
        "mrr": mrr_sum / answerable_count,
    }


def evaluate_answerability(golden_dataset):
    correct = 0
    total = 0

    for item in golden_dataset:

        results = retrieve(
            question=item["question"],
            k=3
        )

        prediction = judge_answerability(
            question=item["question"],
            results=results
        )

        expected = (
            "ANSWERABLE"
            if item["answerable"]
            else "NOT_ANSWERABLE"
        )

        if prediction == expected:
            correct += 1

        total += 1

    return correct / total


def main():
    golden_dataset = load_golden_dataset()

    retrieval_metrics = evaluate_retrieval(golden_dataset)
    answerability_accuracy = evaluate_answerability(golden_dataset)

    print("=" * 80)
    print("RETRIEVAL METRICS")
    print("=" * 80)

    print(f"Hit@1: {retrieval_metrics['hit_at_1']:.3f}")
    print(f"Hit@3: {retrieval_metrics['hit_at_3']:.3f}")
    print(f"MRR:   {retrieval_metrics['mrr']:.3f}")

    print("\n" + "=" * 80)
    print("ANSWERABILITY")
    print("=" * 80)

    print(f"Accuracy: {answerability_accuracy:.3f}")


if __name__ == "__main__":
    main()