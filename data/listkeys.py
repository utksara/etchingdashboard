import json
from typing import Set

def get_all_keys_from_file(file_path: str) -> Set[str]:
    """
    Recursively extracts all unique keys from a JSON file.

    This function reads a JSON file from the given path and traverses the
    entire data structure to collect all unique keys. It handles deeply
    nested dictionaries and lists.

    Args:
        file_path: The path to the JSON file to be read.

    Returns:
        A set of all unique keys found in the JSON data.
        An empty set is returned if an error occurs while reading the file.
    """
    def _get_keys(data, keys_set):
        """Helper function for recursive traversal."""
        if isinstance(data, dict):
            for key, value in data.items():
                keys_set.add(key)
                print(key)
                # _get_keys(value, keys_set)
        # elif isinstance(data, list):
        #     for item in data:
        #         _get_keys(item, keys_set)
                # print(k)
        return keys_set

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            return _get_keys(data, set())
    except FileNotFoundError:
        print(f"Error: The file at '{file_path}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file at '{file_path}' is not a valid JSON file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
    return set()

get_all_keys_from_file("etching_db.json")
