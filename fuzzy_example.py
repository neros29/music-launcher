# fuzzy_sort.py
# This script sorts a list of strings by similarity to a user-provided query string.
# It uses the `thefuzz` library for fuzzy string matching.

# Install the library if you haven't already:
#   pip install thefuzz

import sys
from thefuzz import fuzz, process

def main():
    # Example list of candidate strings
    candidates = [
        "apple pie",
        "banana split",
        "cherry tart",
        "date cake",
        "elderberry crumble",
        "fig roll",
        "grape sorbet",
        "honeydew melon"
    ]

    # Get query from command line argument, or prompt if none provided
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("Enter search string: ").strip()

    if not query:
        print("No query provided. Exiting.")
        return

    # Use process.extract to get list of (match, score) sorted by score descending
    # You can specify the scorer (default is fuzz.WRatio, which is good for general use)
    matches = process.extract(query, candidates, scorer=fuzz.WRatio, limit=None)
    for i in candidates:
        print(f"pie apple {fuzz.partial_token_sort_ratio('pie apple', i)} {i}")
    print(f"\nResults for '{query}':\n")
    for match, score in matches:
        print(f"{score:3d}  {match}")

if __name__ == "__main__":
    main()
