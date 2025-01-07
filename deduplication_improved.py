import os
import sys
import hashlib
from tabulate import tabulate
from typing import List, Dict, Tuple

BUF_SIZE = 65536  # 64 KB

COMPARISON_METHOD_HASH = 1
COMPARISON_METHOD_SIZE = 2


def get_all_files_in_folder(path: str) -> List[str]:
    """Retrieve all files in the specified folder."""
    files = []
    for dirpath, _, filenames in os.walk(path):
        files.extend([os.path.join(dirpath, file) for file in filenames])
        break  # Only get files from the top level
    return files


def get_md5_hash_of_file(path: str) -> str:
    """Calculate the MD5 hash of a file."""
    md5 = hashlib.md5()
    with open(path, 'rb') as file:
        while chunk := file.read(BUF_SIZE):
            md5.update(chunk)
    return md5.hexdigest()


def display_data(table_data: List[Tuple[str, str]]) -> None:
    """Display duplicate file information in a tabular format."""
    headers = ["Size [bytes] / MD5 hash", "File paths"]
    print(tabulate(table_data, headers=headers, showindex=True, tablefmt="rounded_grid"))


def deduplicate_folder(files_with_hash_or_size: Dict[str, List[str]]) -> None:
    """Delete duplicate files based on the provided hash or size data."""
    for key, file_paths in files_with_hash_or_size.items():
        if len(file_paths) > 1:
            for file_to_delete in file_paths[1:]:
                print(f"Deleting file: '{file_to_delete}'")
                os.remove(file_to_delete)


def main():
    if len(sys.argv) < 2:
        input_folder = input("Please paste the folder to be analyzed:\n")
    else:
        input_folder = sys.argv[1]

    if not os.path.isdir(input_folder):
        print("Error: Provided path is not a valid folder.")
        sys.exit(1)

    comparison_method = None
    while not comparison_method:
        try:
            print("How would you like to compare the files?")
            print(f"{COMPARISON_METHOD_HASH}: Hash")
            print(f"{COMPARISON_METHOD_SIZE}: File size")
            comparison_method = int(input("Enter your choice: "))
            if comparison_method not in [COMPARISON_METHOD_HASH, COMPARISON_METHOD_SIZE]:
                raise ValueError("Invalid choice.")
        except ValueError as e:
            print(f"Error: {e}. Please enter 1 or 2.")
            comparison_method = None

    file_paths = get_all_files_in_folder(input_folder)
    files_with_hash_or_size: Dict[str, List[str]] = {}

    if comparison_method == COMPARISON_METHOD_HASH:
        print("Comparing files by hash...")
        for file_path in file_paths:
            try:
                file_hash = get_md5_hash_of_file(file_path)
                files_with_hash_or_size.setdefault(file_hash, []).append(file_path)
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

    elif comparison_method == COMPARISON_METHOD_SIZE:
        print("Comparing files by size...")
        for file_path in file_paths:
            try:
                file_size = os.stat(file_path).st_size
                files_with_hash_or_size.setdefault(file_size, []).append(file_path)
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

    duplicates = {
        key: paths
        for key, paths in files_with_hash_or_size.items()
        if len(paths) > 1
    }

    if not duplicates:
        print("No duplicates found!")
        return

    table_data = [(key, "\n".join(paths)) for key, paths in duplicates.items()]
    display_data(table_data)

    try:
        deduplicate = int(input("Would you like to run deduplication?\n1: Yes\n2: No\n"))
        if deduplicate == 1:
            deduplicate_folder(duplicates)
    except ValueError:
        print("Invalid input. Exiting without deduplication.")


if __name__ == "__main__":
    main()
