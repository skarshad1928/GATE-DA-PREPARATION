from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ai.models import PromptBundle


DIFFICULTY_ORDER = ["Easy", "Medium", "Hard"]

# Every blueprint below maps 1:1 onto a numbered section of the official
# GATE 2027 (IIT Madras) Data Science and Artificial Intelligence syllabus.
# No section is treated as "extra" or optional -- all seven carry equal
# weight in the app, matching the exam's own structure.
PRACTICE_BLUEPRINTS = {
    "prob_stats": {
        "title": "Probability & Statistics",
        "summary": "Section 1 of the GATE DA syllabus: counting, probability, distributions, and statistical inference.",
        "section_name": "Probability and Statistics",
        "prompt_attrs": ("prob_stats_system_prompt", "prob_stats_generate_prompt"),
        "topic_groups": {
            "Counting & Probability Basics": [
                "Permutations & Combinations",
                "Probability Axioms",
                "Sample Space & Events",
                "Independent Events",
                "Mutually Exclusive Events",
            ],
            "Conditional & Joint Probability": [
                "Marginal Probability",
                "Conditional Probability",
                "Joint Probability",
                "Bayes Theorem",
                "Conditional Expectation",
                "Conditional Variance",
            ],
            "Descriptive Statistics": [
                "Mean, Median, Mode",
                "Standard Deviation",
                "Correlation",
                "Covariance",
            ],
            "Random Variables & Distributions": [
                "Discrete Random Variables & PMF",
                "Uniform Distribution",
                "Bernoulli Distribution",
                "Binomial Distribution",
                "Continuous Random Variables & PDF",
                "Exponential Distribution",
                "Poisson Distribution",
                "Normal & Standard Normal Distribution",
                "t-Distribution",
                "Chi-Squared Distribution",
                "Cumulative Distribution Function",
                "Conditional PDF",
            ],
            "Inferential Statistics": [
                "Central Limit Theorem",
                "Confidence Interval",
                "z-Test",
                "t-Test",
                "Chi-Squared Test",
            ],
        },
        "default_patterns": [
            "GATE DA Core",
            "Numerical Answer Type (NAT) Style",
            "Multiple Select (MSQ) Style",
            "Conceptual Trap Questions",
        ],
    },
    "linear_algebra": {
        "title": "Linear Algebra",
        "summary": "Section 2 of the GATE DA syllabus: vector spaces, matrices, systems of equations, and decompositions.",
        "section_name": "Linear Algebra",
        "prompt_attrs": ("linear_algebra_system_prompt", "linear_algebra_generate_prompt"),
        "topic_groups": {
            "Vector Spaces": [
                "Vector Space",
                "Subspaces",
                "Linear Dependence & Independence",
            ],
            "Matrices & Special Matrices": [
                "Matrix Operations",
                "Projection Matrix",
                "Orthogonal Matrix",
                "Idempotent Matrix",
                "Partition Matrix & Properties",
                "Quadratic Forms",
            ],
            "Systems of Linear Equations": [
                "Systems of Linear Equations & Solutions",
                "Gaussian Elimination",
            ],
            "Eigenvalues, Rank & Decompositions": [
                "Eigenvalues & Eigenvectors",
                "Determinant",
                "Rank & Nullity",
                "Projections",
                "LU Decomposition",
                "Singular Value Decomposition (SVD)",
            ],
        },
        "default_patterns": [
            "GATE DA Core",
            "Numerical Answer Type (NAT) Style",
            "Multiple Select (MSQ) Style",
            "Conceptual Trap Questions",
        ],
    },
    "calculus_optimization": {
        "title": "Calculus & Optimization",
        "summary": "Section 3 of the GATE DA syllabus: single-variable calculus, Taylor series, and optimization.",
        "section_name": "Calculus and Optimization",
        "prompt_attrs": (
            "calculus_optimization_system_prompt",
            "calculus_optimization_generate_prompt",
        ),
        "topic_groups": {
            "Single Variable Calculus": [
                "Functions of a Single Variable",
                "Limits",
                "Continuity",
                "Differentiability",
                "Taylor Series",
            ],
            "Optimization": [
                "Maxima & Minima",
                "Optimization in a Single Variable",
            ],
        },
        "default_patterns": [
            "GATE DA Core",
            "Numerical Answer Type (NAT) Style",
            "Multiple Select (MSQ) Style",
            "Conceptual Trap Questions",
        ],
    },
    "programming_dsa": {
        "title": "Programming, DSA",
        "summary": "Section 4 of the GATE DA syllabus: Python, core data structures, and classic algorithms.",
        "section_name": "Programming, Data Structures and Algorithms",
        "prompt_attrs": ("programming_dsa_system_prompt", "programming_dsa_generate_prompt"),
        "topic_groups": {
            "Python Programming": [
                "Python Fundamentals",
                "Python Data Handling",
            ],
            "Basic Data Structures": [
                "Stacks",
                "Queues",
                "Linked Lists",
                "Trees",
                "Hash Tables",
            ],
            "Searching & Sorting": [
                "Linear Search",
                "Binary Search",
                "Selection Sort",
                "Bubble Sort",
                "Insertion Sort",
            ],
            "Divide and Conquer": [
                "Merge Sort",
                "Quick Sort",
            ],
            "Graph Theory & Algorithms": [
                "Graph Theory Basics",
                "Graph Traversals (BFS/DFS)",
                "Shortest Path Algorithms",
            ],
        },
        "default_patterns": [
            "GATE DA Core",
            "Numerical Answer Type (NAT) Style",
            "Multiple Select (MSQ) Style",
            "Conceptual Trap Questions",
        ],
    },
    "dbms": {
        "title": "Database Mgmt & Warehousing",
        "summary": "Section 5 of the GATE DA syllabus: ER/relational modelling, SQL, indexing, and data warehousing.",
        "section_name": "Database Management and Warehousing",
        "prompt_attrs": ("dbms_system_prompt", "dbms_generate_prompt"),
        "topic_groups": {
            "Data Modelling": [
                "ER-Model",
                "Relational Model",
                "Relational Algebra",
                "Tuple Calculus",
            ],
            "SQL & Constraints": [
                "SQL",
                "Integrity Constraints",
                "Normal Forms",
            ],
            "Storage & Indexing": [
                "File Organization",
                "Indexing",
                "Data Types",
            ],
            "Data Transformation": [
                "Normalization",
                "Discretization",
                "Sampling",
                "Compression",
            ],
            "Data Warehousing": [
                "Multidimensional Data Models",
                "Concept Hierarchies",
                "Measures: Categorization & Computation",
            ],
        },
        "default_patterns": [
            "GATE DA Core",
            "Numerical Answer Type (NAT) Style",
            "Multiple Select (MSQ) Style",
            "Conceptual Trap Questions",
        ],
    },
    "machine_learning": {
        "title": "Machine Learning",
        "summary": "Section 6 of the GATE DA syllabus: supervised & unsupervised learning, evaluation, and dimensionality reduction.",
        "section_name": "Machine Learning",
        "prompt_attrs": ("machine_learning_system_prompt", "machine_learning_generate_prompt"),
        "topic_groups": {
            "Supervised Learning: Regression": [
                "Simple Linear Regression",
                "Multiple Linear Regression",
                "Ridge Regression",
            ],
            "Supervised Learning: Classification": [
                "Logistic Regression",
                "k-Nearest Neighbour",
                "Naive Bayes Classifier",
                "Linear Discriminant Analysis",
                "Support Vector Machine",
                "Decision Trees",
            ],
            "Model Evaluation": [
                "Bias-Variance Trade-off",
                "Leave-One-Out Cross-Validation",
                "k-Fold Cross-Validation",
            ],
            "Neural Networks": [
                "Multi-Layer Perceptron",
                "Feed-Forward Neural Network",
            ],
            "Unsupervised Learning": [
                "k-Means / k-Medoid Clustering",
                "Hierarchical Clustering (Single-Linkage)",
                "Hierarchical Clustering (Complete-Linkage)",
            ],
            "Dimensionality Reduction": [
                "Principal Component Analysis (PCA)",
            ],
        },
        "default_patterns": [
            "GATE DA Core",
            "Numerical Answer Type (NAT) Style",
            "Multiple Select (MSQ) Style",
            "Conceptual Trap Questions",
        ],
    },
    "artificial_intelligence": {
        "title": "Artificial Intelligence",
        "summary": "Section 7 of the GATE DA syllabus: search, logic, and reasoning under uncertainty.",
        "section_name": "AI",
        "prompt_attrs": (
            "artificial_intelligence_system_prompt",
            "artificial_intelligence_generate_prompt",
        ),
        "topic_groups": {
            "Search": [
                "Uninformed Search",
                "Informed Search",
                "Adversarial Search",
            ],
            "Logic": [
                "Propositional Logic",
                "Predicate Logic",
            ],
            "Reasoning Under Uncertainty": [
                "Conditional Independence Representation",
                "Exact Inference: Variable Elimination",
                "Approximate Inference: Sampling",
            ],
        },
        "default_patterns": [
            "GATE DA Core",
            "Numerical Answer Type (NAT) Style",
            "Multiple Select (MSQ) Style",
            "Conceptual Trap Questions",
        ],
    },
}

# Ordered list of section keys, matching the syllabus PDF's own numbering.
# Used anywhere the app needs to render all sections "in syllabus order".
SECTION_ORDER = [
    "prob_stats",
    "linear_algebra",
    "calculus_optimization",
    "programming_dsa",
    "dbms",
    "machine_learning",
    "artificial_intelligence",
]


def load_text_file(path: str | Path) -> str:
    with Path(path).open("r", encoding="utf-8") as handle:
        return handle.read().strip()


def load_json_file(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def ensure_parent_directory(path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def get_prompt_bundle(settings, blueprint_key: str) -> "PromptBundle":
    from ai.models import PromptBundle

    blueprint = PRACTICE_BLUEPRINTS[blueprint_key]
    system_attr, generation_attr = blueprint["prompt_attrs"]
    return PromptBundle(
        system_prompt_path=str(getattr(settings, system_attr)),
        generation_prompt_path=str(getattr(settings, generation_attr)),
    )


def flatten_topics(topic_groups: dict[str, list[str]]) -> list[str]:
    flattened: list[str] = []
    for topics in topic_groups.values():
        flattened.extend(topics)
    return flattened


def recommend_difficulty(
    accuracy: float,
    attempts: int,
    current_difficulty: str = "Medium",
) -> str:
    current = current_difficulty if current_difficulty in DIFFICULTY_ORDER else "Medium"
    index = DIFFICULTY_ORDER.index(current)
    if attempts < 3:
        return current
    if accuracy >= 80 and index < len(DIFFICULTY_ORDER) - 1:
        return DIFFICULTY_ORDER[index + 1]
    if accuracy < 50 and index > 0:
        return DIFFICULTY_ORDER[index - 1]
    return current


def build_recent_question_summaries(
    questions: list[dict[str, Any]],
    limit: int = 5,
) -> list[str]:
    summaries: list[str] = []
    for item in questions[:limit]:
        topic = item.get("topic", "Unknown Topic")
        subtopic = item.get("subtopic", "Unknown Subtopic")
        question = str(item.get("question", "")).strip().replace("\n", " ")
        short_question = question[:110] + ("..." if len(question) > 110 else "")
        summaries.append(f"{topic} / {subtopic}: {short_question}")
    return summaries


def summarize_attempts(attempts: list[dict[str, Any]]) -> dict[str, Any]:
    total_attempts = len(attempts)
    correct_attempts = sum(1 for item in attempts if item.get("is_correct") is True)
    accuracy = round((correct_attempts / total_attempts) * 100, 2) if total_attempts else 0.0

    avg_time = 0.0
    if total_attempts:
        time_values = [int(item.get("time_taken_seconds") or 0) for item in attempts]
        avg_time = round(sum(time_values) / total_attempts, 2)

    topic_stats: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"attempts": 0, "correct": 0, "time_taken_seconds": 0}
    )
    difficulty_stats: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"attempts": 0, "correct": 0}
    )

    for item in attempts:
        topic = str(item.get("topic") or "Unknown")
        topic_stats[topic]["attempts"] += 1
        topic_stats[topic]["correct"] += 1 if item.get("is_correct") is True else 0
        topic_stats[topic]["time_taken_seconds"] += int(item.get("time_taken_seconds") or 0)

        difficulty = str(item.get("difficulty") or "Unknown")
        difficulty_stats[difficulty]["attempts"] += 1
        difficulty_stats[difficulty]["correct"] += 1 if item.get("is_correct") is True else 0

    topic_rows: list[dict[str, Any]] = []
    for topic, values in topic_stats.items():
        topic_attempts = values["attempts"]
        topic_accuracy = round((values["correct"] / topic_attempts) * 100, 2)
        topic_rows.append(
            {
                "topic": topic,
                "attempts": topic_attempts,
                "correct": values["correct"],
                "accuracy": topic_accuracy,
                "avg_time_seconds": round(values["time_taken_seconds"] / topic_attempts, 2),
            }
        )
    topic_rows.sort(key=lambda row: (-row["accuracy"], -row["attempts"], row["topic"]))

    difficulty_rows: list[dict[str, Any]] = []
    for difficulty, values in difficulty_stats.items():
        attempt_count = values["attempts"]
        difficulty_rows.append(
            {
                "difficulty": difficulty,
                "attempts": attempt_count,
                "accuracy": round((values["correct"] / attempt_count) * 100, 2),
            }
        )

    strong_topics = [
        row["topic"] for row in topic_rows if row["attempts"] >= 2 and row["accuracy"] >= 80
    ]
    weak_topics = [
        row["topic"] for row in topic_rows if row["attempts"] >= 2 and row["accuracy"] < 50
    ]

    return {
        "attempts": total_attempts,
        "correct": correct_attempts,
        "accuracy": accuracy,
        "average_time_seconds": avg_time,
        "topic_rows": topic_rows,
        "difficulty_rows": difficulty_rows,
        "strong_topics": strong_topics,
        "weak_topics": weak_topics,
    }
