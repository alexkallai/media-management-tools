import sys
import os
import hashlib
from tabulate import tabulate

# # BUF_SIZE is totally arbitrary, change for your app!
BUF_SIZE = 65536  # lets read stuff in 64kb chunks!

input_folder = ""
files_with_hash_or_size = {}
comparison_method = None

def get_all_files_in_folder(path: str):
    f = []
    for (dirpath, dirnames, filenames) in os.walk(path):
        f.extend(filenames)
        break
    return f

def get_md5_hash_of_file(path: str):
    md5 = hashlib.md5()
    with open(path, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()

def print_data(table_data):
    headers = ["Size [bytes] / MD5 hash", "File paths"]
    print(tabulate(headers=headers, showindex=True, tabular_data=table_data, tablefmt="rounded_grid"))

def deduplicate_folder(table_data):
        # Run deduplication
        for duplicate_size, _ in table_data:
            list_of_duplicate_files_for_size = files_with_hash_or_size[duplicate_size]
            files_to_delete = list_of_duplicate_files_for_size[1:]
            for path in files_to_delete:
                print(f"Deleting file: '{path}'")
                os.remove(path)
            pass

if __name__ == "__main__":
    os.system('cls')
    if len(sys.argv) > 1:
        if sys.argv[1] in ["help", "h", "--help", "-help", "-h", "--h"]:
            print("TODO")
            quit()
        input_folder = sys.argv[1]
        print(f"The folder path received is: {input_folder}")
    if len(sys.argv) > 2:
        input_folder = sys.argv[1]
        try:
            comparison_method = int(sys.argv[2])
        except Exception as e:
            print(e)
            print("Second argument incorrect, check help")
            print("Exiting...")
            exit
        print(f"The folder path received is: {input_folder}")
    else:
        input_folder = input("Please paste the folder to be analyzed:\n")

    while True and not comparison_method:
        os.system('cls')
        comparison_method = int(input("How would you like to compare the files?\n1. Hash\n2. File size\n"))
        if comparison_method in [1, 2]:
            break

    file_paths = get_all_files_in_folder(input_folder)
    if comparison_method == 1:
        # Hash
        for file_name in file_paths:
            full_path = os.path.join(input_folder, file_name)
            hash_of_file = get_md5_hash_of_file(full_path)
            if hash_of_file in files_with_hash_or_size.keys():
                files_with_hash_or_size[hash_of_file].append(full_path)
            else:
                files_with_hash_or_size.update({hash_of_file: [full_path]})

    if comparison_method == 2:
        # Size
        for file_name in file_paths:
            full_path = os.path.join(input_folder, file_name)
            file_size_in_bytes = os.stat(full_path).st_size
            if file_size_in_bytes in files_with_hash_or_size.keys():
                files_with_hash_or_size[file_size_in_bytes].append(full_path)
            else:
                files_with_hash_or_size.update({file_size_in_bytes: [full_path]})

    table_data = [(key, "\n".join(values)) for key, values in files_with_hash_or_size.items() if len(values) > 1]

    os.system('cls')
    if len(table_data) == 0:
        print("Found no duplicates!")
        quit()

    print_data(table_data)

    deduplicate = int(input("Would you like to run deduplication?\n1: Yes\n2: No\n"))
    if deduplicate == 1:
        deduplicate_folder(table_data=table_data)