import json
import os
import sys

# Ensure db.py can be imported from the root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import Database


def seed_database(json_file_path="problems.json"):
    Database.initialize()
    db = Database.get_db()

    print("Clearing existing problem bank...")
    db.problems.delete_many({})

    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            problems_data = json.load(file)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return

    formatted_problems = []
    # Flatten if it's a list of arrays
    if isinstance(problems_data, list) and isinstance(problems_data[0], list):
        problems_data = [item for sublist in problems_data for item in sublist]

    # Assign a guaranteed unique ID to every problem
    for index, prob in enumerate(problems_data):
        # Create a unique string ID like "prob_1", "prob_2", etc.
        prob['_id'] = f"prob_{index + 1}"

        # Remove the old overlapping problem_id so it doesn't cause confusion
        if 'problem_id' in prob:
            del prob['problem_id']

        formatted_problems.append(prob)

    if formatted_problems:
        result = db.problems.insert_many(formatted_problems)
        print(f"Successfully seeded {len(result.inserted_ids)} problems.")

        # Recreate the index for the KFF algorithm
        db.problems.create_index([("skills", 1), ("difficulty", 1)])
        print("Created index for skills and difficulty.")
    else:
        print("No problems found to insert.")


if __name__ == "__main__":
    seed_database()