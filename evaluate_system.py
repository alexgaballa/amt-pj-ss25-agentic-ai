import json
from typing import List, Dict
import sys
from dotenv import load_dotenv

load_dotenv()
# LLM-as-a-Judge imports
try:
    from judges import PollMultihopCorrectness, MTBenchChatBotResponseQuality
except ImportError:
    print("[ERROR] judges library not found. Please install with: pip install judges")
    sys.exit(1)

"""
Evaluation Script Instructions:
- Prepare a JSON file (e.g., 'system_outputs.json') with a list of dicts, each containing:
    {
        "prompt": "...",
        "system_response": "...",
        "reference": "..."  # Fill in the golden standard answer here
    }
- You can fill in or update the 'reference' field manually after running your system.
- This script will evaluate each system_response against the reference using LLM-as-a-Judge.
- Results will be saved to 'evaluation_results.json'.
"""

INPUT_FILE = "system_outputs.json"  # Change this if your file is named differently
OUTPUT_FILE = "evaluation_results.json"

# 1. Load prompts, system responses, and references from JSON file
def load_eval_cases(filename: str) -> List[Dict]:
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

# 2. LLM-as-a-Judge evaluation functions
def llm_judge_correctness(prompt: str, system_response: str, reference: str) -> Dict:
    judge = PollMultihopCorrectness(model="openai/gpt-4.1-mini")
    result = judge.judge(input=prompt, output=system_response, expected=reference)
    return result

def llm_judge_quality(prompt: str, system_response: str, reference: str) -> Dict:
    judge = MTBenchChatBotResponseQuality(model="openai/gpt-4.1-mini")
    result = judge.judge(input=prompt, output=system_response, expected=reference)
    return result

# 3. Main evaluation loop
def main():
    eval_cases = load_eval_cases(INPUT_FILE)
    results = []
    print(f"\n[INFO] Evaluating {len(eval_cases)} system responses from {INPUT_FILE}...\n")
    for idx, case in enumerate(eval_cases):
        prompt = case.get("prompt", "")
        system_response = case.get("system_response", "")
        reference = case.get("reference", "")
        print(f"\n--- Prompt {idx+1}/{len(eval_cases)} ---\n{prompt}")
        print("[INFO] System response:\n", system_response)
        print("[INFO] Reference answer:\n", reference)
        print("[INFO] Running LLM-as-a-Judge evaluation...")
        print(f"Prompt: {prompt}\nSystem response: {system_response}\nReference: {reference}")
        correctness_obj = llm_judge_correctness(prompt, system_response, reference)
        quality_obj = llm_judge_quality(prompt, system_response, reference)

        # Convert to dict for JSON serialization
        if hasattr(correctness_obj, "dict"):
            correctness = correctness_obj.dict()
        else:
            correctness = vars(correctness_obj)
        if hasattr(quality_obj, "dict"):
            quality = quality_obj.dict()
        else:
            quality = vars(quality_obj)

        results.append({
            "prompt": prompt,
            "system_response": system_response,
            "reference": reference,
            "correctness": correctness,
            "quality": quality
        })
    # 4. Save results
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n[INFO] Evaluation complete. Results saved to {OUTPUT_FILE}\n")

if __name__ == "__main__":
    print(f"""
[INFO] This script will:
- Read prompts, system responses, and references from '{INPUT_FILE}'
- Score each response for correctness and quality using LLM-as-a-Judge
- Save results to '{OUTPUT_FILE}'

[IMPORTANT] Please fill in the 'reference' fields in your input file for best evaluation accuracy.
[DEPENDENCY] Install the judges library: pip install judges
""")
    main() 