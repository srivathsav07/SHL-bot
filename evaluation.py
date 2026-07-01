import json
import requests
from bot_logic import get_bot_response, CATALOG

# Test conversation traces (based on assignment examples)
TEST_TRACES = [
    {
        "name": "Java Developer - Senior",
        "user_inputs": [
            "I need an assessment for senior Java developers",
            "Something that tests architectural thinking"
        ],
        "expected_test_keywords": ["java", "senior", "enterprise"],
        "expected_urls_contain": ["java", "enterprise"]
    },
    {
        "name": "Python - Mid-level",
        "user_inputs": [
            "I need a test for mid-level Python developers",
            "Also add something for problem-solving"
        ],
        "expected_test_keywords": ["python"],
        "expected_urls_contain": ["python"]
    },
    {
        "name": "General Tech - Vague",
        "user_inputs": [
            "I need an assessment",
        ],
        "expected_clarifying_question": True,  # Should ask questions
        "expected_test_keywords": []
    },
    {
        "name": "Management Skills",
        "user_inputs": [
            "What tests do you have for team leads?"
        ],
        "expected_test_keywords": ["leadership", "management"]
    }
]

def evaluate_recall_at_k(recommendations, expected_keywords, k=10):
    """
    Recall@K: Fraction of expected tests that appear in top K recommendations
    
    Formula: Recall@K = (# of relevant tests in top K) / (total # relevant tests)
    """
    if not expected_keywords or not recommendations:
        return 0.0
    
    recommended_names = [r.get("name", "").lower() for r in recommendations[:k]]
    
    matches = 0
    for keyword in expected_keywords:
        if any(keyword.lower() in name for name in recommended_names):
            matches += 1
    
    recall = matches / len(expected_keywords) if expected_keywords else 0
    return recall

def evaluate_groundedness(recommendations):
    """
    Groundedness: Are all recommended URLs from the actual catalog?
    Returns: % of recommendations with valid catalog URLs
    """
    if not recommendations:
        return 1.0  # No recommendations = no hallucinations
    
    catalog_urls = set(t.get("link", "") for t in CATALOG)
    
    valid_count = 0
    for rec in recommendations:
        rec_url = rec.get("url", "")
        if rec_url in catalog_urls:
            valid_count += 1
    
    groundedness = valid_count / len(recommendations) if recommendations else 0
    return groundedness

def evaluate_response_format(response):
    """
    Check if response matches required JSON schema
    Returns: True if valid, False otherwise
    """
    required_fields = ["reply", "recommendations", "end_of_conversation"]
    
    # Check all required fields exist
    if not all(field in response for field in required_fields):
        return False
    
    # Check types
    if not isinstance(response["reply"], str):
        return False
    if not isinstance(response["recommendations"], list):
        return False
    if not isinstance(response["end_of_conversation"], bool):
        return False
    
    # Check recommendation format
    for rec in response["recommendations"]:
        if not all(field in rec for field in ["name", "url", "test_type"]):
            return False
        if not isinstance(rec["name"], str) or not isinstance(rec["url"], str):
            return False
    
    return True

def evaluate_conversation_trace(trace):
    """
    Run a full conversation trace and measure:
    - Format compliance
    - Recall@10
    - Groundedness
    - Response quality
    """
    print(f"\n{'='*60}")
    print(f"Testing: {trace['name']}")
    print(f"{'='*60}")
    
    messages = []
    all_recommendations = []
    format_compliance = True
    
    for i, user_input in enumerate(trace["user_inputs"]):
        print(f"\nTurn {i+1} - User: {user_input}")
        
        # Add user message
        messages.append({"role": "user", "content": user_input})
        
        # Get bot response
        response = get_bot_response(messages)
        
        # Check format compliance
        if not evaluate_response_format(response):
            print("  ❌ INVALID JSON FORMAT")
            format_compliance = False
        else:
            print("  ✓ Valid JSON format")
        
        print(f"  Bot: {response['reply'][:100]}...")
        
        # Collect recommendations
        if response.get("recommendations"):
            all_recommendations = response["recommendations"]
            print(f"  Recommendations: {len(all_recommendations)} tests")
            for rec in all_recommendations[:3]:
                print(f"    - {rec['name']}")
        else:
            print("  Recommendations: None (still gathering info)")
        
        # Add bot response to conversation
        messages.append({"role": "assistant", "content": response["reply"]})
    
    # Evaluate final recommendations
    print(f"\n{'-'*60}")
    print("EVALUATION RESULTS:")
    print(f"{'-'*60}")
    
    # 1. Format Compliance
    print(f"✓ Schema Compliance: {'PASS' if format_compliance else 'FAIL'}")
    
    # 2. Recall@10
    if trace.get("expected_test_keywords"):
        recall = evaluate_recall_at_k(
            all_recommendations, 
            trace["expected_test_keywords"]
        )
        print(f"✓ Recall@10: {recall:.2%}")
    else:
        print(f"✓ Recall@10: N/A (no expected tests defined)")
    
    # 3. Groundedness
    if all_recommendations:
        groundedness = evaluate_groundedness(all_recommendations)
        print(f"✓ Groundedness: {groundedness:.2%} ({sum(1 for r in all_recommendations if r.get('url') in [t.get('link') for t in CATALOG])}/{len(all_recommendations)} valid URLs)")
    else:
        print(f"✓ Groundedness: N/A (no recommendations)")
    
    # 4. Clarifying Questions (if expected)
    if trace.get("expected_clarifying_question"):
        has_question = "?" in messages[-1]["content"]
        print(f"✓ Asked Clarifying Questions: {'PASS' if has_question else 'FAIL'}")
    
    return {
        "trace_name": trace["name"],
        "format_compliance": format_compliance,
        "recall": recall if trace.get("expected_test_keywords") else None,
        "groundedness": groundedness if all_recommendations else None
    }

def run_full_evaluation():
    """Run all evaluation tests and print summary"""
    print("\n" + "="*60)
    print("SHL ASSESSMENT RECOMMENDER - EVALUATION SUITE")
    print("="*60)
    
    results = []
    for trace in TEST_TRACES:
        result = evaluate_conversation_trace(trace)
        results.append(result)
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    format_pass = sum(1 for r in results if r["format_compliance"]) / len(results) * 100
    print(f"\n✓ Schema Compliance Rate: {format_pass:.1f}% ({sum(1 for r in results if r['format_compliance'])}/{len(results)} traces)")
    
    recalls = [r["recall"] for r in results if r["recall"] is not None]
    if recalls:
        mean_recall = sum(recalls) / len(recalls)
        print(f"✓ Mean Recall@10: {mean_recall:.2%}")
    
    groundedness = [r["groundedness"] for r in results if r["groundedness"] is not None]
    if groundedness:
        mean_groundedness = sum(groundedness) / len(groundedness)
        print(f"✓ Mean Groundedness: {mean_groundedness:.2%}")
    
    print("\n" + "="*60)
    print("EVALUATION COMPLETE")
    print("="*60 + "\n")

if __name__ == "__main__":
    run_full_evaluation()