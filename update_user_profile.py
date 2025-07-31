import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_PATH = os.path.join(BASE_DIR, "long_term_memory.json")


def get_user_profile(user_id: str, memory_path: str = MEMORY_PATH) -> dict:
    """Retrieve the user profile from memory."""
    if not os.path.exists(memory_path):
        return {}

    with open(memory_path, "r", encoding="utf-8") as f:
        memory = json.load(f)

    return memory.get(user_id, {})

def update_user_profile(new_data: dict, user_id: str, memory_path: str = MEMORY_PATH) -> dict:
    """Update user profile stored in a JSON file with new extracted data."""

    # Step 1: Load existing memory
    if os.path.exists(memory_path):
        with open(memory_path, "r", encoding="utf-8") as f:
            memory = json.load(f)
    else:
        memory = {}

    # Step 2: Get existing user profile (or empty template)
    current = get_user_profile(user_id, memory_path)
    if not current:
        current = {"name": "", "studies": "", "age": "", "gender": "", "likes": []}
    
    # Step 3: Update fields
    for field in ["name", "studies", "age", "gender"]:
        if field in new_data and new_data[field]:
            current[field] = new_data[field]

    # Step 4: Merge likes (normalize all)
    def normalize_like(s: str) -> str:
        return s.strip().capitalize()

    if "likes" in new_data and isinstance(new_data["likes"], list):
        new_likes = set(normalize_like(like) for like in new_data["likes"] if isinstance(like, str) and like.strip())
        existing_likes = set(normalize_like(like) for like in current.get("likes", []))
        current["likes"] = list(existing_likes.union(new_likes))

    # Step 5: Write updated profile back to memory
    memory[user_id] = current
    with open(memory_path, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)

    return current
