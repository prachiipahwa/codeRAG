import json
import os
import sys
from evaluation.metrics import StandardMetrics
from src.retrieval.hybrid_search import HybridRetriever
from src.workspace_manager import WorkspaceManager

def run_evaluation(project_name: str):
    print(f"Starting Evaluation Suite for project: {project_name}")
    
    try:
        retriever = HybridRetriever(project_name)
    except Exception as e:
        print(f"Failed to initialize retriever (make sure indexes are built for this project): {e}")
        return

    dataset_path = os.path.join(os.path.dirname(__file__), "evaluation", "eval_dataset.json")
    if not os.path.exists(dataset_path):
        print("Evaluation dataset not found.")
        return
        
    with open(dataset_path, "r") as f:
        dataset = json.load(f)

    total_precision_at_3 = 0.0
    total_recall_at_3 = 0.0
    total_mrr = 0.0

    print(f"Running queries for {len(dataset)} examples...")
    for idx, item in enumerate(dataset):
        query = item["question"]
        expected_sources = item["expected_sources"]

        print(f"  Q{idx+1}: {query}")
        # Note: retriever now returns (docs, debug_trace)
        retrieved_docs, _ = retriever.retrieve(query)
        
        p3 = StandardMetrics.calculate_precision_at_k(retrieved_docs, expected_sources, k=3)
        r3 = StandardMetrics.calculate_recall_at_k(retrieved_docs, expected_sources, k=3)
        mrr = StandardMetrics.calculate_mrr(retrieved_docs, expected_sources)

        total_precision_at_3 += p3
        total_recall_at_3 += r3
        total_mrr += mrr
        
        print(f"    P@3: {p3:.2f} | R@3: {r3:.2f} | MRR: {mrr:.2f}")

    num_queries = len(dataset)
    avg_p3 = total_precision_at_3 / num_queries
    avg_r3 = total_recall_at_3 / num_queries
    avg_mrr = total_mrr / num_queries

    print("\n--- FINAL EVALUATION RESULTS ---")
    print(f"Average Precision@3 : {avg_p3:.3f}")
    print(f"Average Recall@3    : {avg_r3:.3f}")
    print(f"Mean Reciprocal Rank: {avg_mrr:.3f}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python evaluate.py <project_name>")
        projects = WorkspaceManager.get_projects()
        if projects:
            print(f"Available projects: {', '.join(projects)}")
        sys.exit(1)
        
    run_evaluation(sys.argv[1])
