import os
import hashlib
from collections import defaultdict

def find_duplicate_files(directory):
    """
    Finds duplicate files in a directory based on their content hash.

    Args:
        directory (str): The path to the directory to scan.

    Returns:
        dict: A dictionary where keys are hashes of duplicate files and
              values are lists of paths to those files.
    """
    hashes = defaultdict(list)
    duplicates = {}

    print(f"Scanning files in {directory}...")

    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            try:
                hasher = hashlib.md5()
                with open(file_path, 'rb') as f:
                    while chunk := f.read(8192):
                        hasher.update(chunk)
                file_hash = hasher.hexdigest()
                hashes[file_hash].append(file_path)
            except (IOError, OSError) as e:
                print(f"Could not read file: {file_path} - {e}")
                continue

    print("Comparing file hashes...")
    for file_hash, file_paths in hashes.items():
        if len(file_paths) > 1:
            duplicates[file_hash] = file_paths

    return duplicates

def delete_duplicates(duplicates_dict):
    """
    Deletes duplicate files, keeping one copy from each set.

    Args:
        duplicates_dict (dict): A dictionary of duplicates from find_duplicate_files.
    """
    if not duplicates_dict:
        return

    total_deleted = 0
    for file_hash, paths in duplicates_dict.items():
        # Keep the first file, delete the rest
        files_to_delete = paths[1:]
        print(f"\n--- Duplicate Set (Hash: {file_hash}) ---")
        print(f"Keeping: {paths[0]}")
        for path in files_to_delete:
            try:
                print(f"Deleting: {path}")
                os.remove(path)
                total_deleted += 1
            except OSError as e:
                print(f"Error deleting file {path}: {e}")
    
    print(f"\nTotal files deleted: {total_deleted}")


def main():
    """
    Main function to run the duplicate file check and print results.
    """
    # Assuming the script is run from the root of the project
    data_directory = os.path.join(os.getcwd(), 'data', 'PlantVillage')

    if not os.path.isdir(data_directory):
        print(f"Error: Directory not found at {data_directory}")
        print("Please ensure the PlantVillage dataset is in the 'data' folder.")
        return

    duplicate_files = find_duplicate_files(data_directory)

    if not duplicate_files:
        print("\nNo duplicate files found.")
    else:
        print(f"\nFound {len(duplicate_files)} sets of duplicate files.")
        delete_duplicates(duplicate_files)

if __name__ == "__main__":
    main()
