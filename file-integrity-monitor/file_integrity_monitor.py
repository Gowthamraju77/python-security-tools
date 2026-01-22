import hashlib
import os

# Function to calculate SHA-256 hash of a file
def calculate_hash(file_path):
    """
    Reads the file in binary mode and calculates SHA-256 hash
    """
    sha256 = hashlib.sha256()

    try:
        with open(file_path, "rb") as file:
            # Read file in chunks to support large files
            for chunk in iter(lambda: file.read(4096), b""):
                sha256.update(chunk)

        return sha256.hexdigest()

    except FileNotFoundError:
        print("❌ File not found!")
        return None


# Function to save hash to a file
def save_hash(file_path, hash_value):
    with open("stored_hash.txt", "w") as f:
        f.write(hash_value)
    print("✅ Hash saved successfully.")


# Function to load stored hash
def load_hash():
    if not os.path.exists("stored_hash.txt"):
        print("❌ No stored hash found.")
        return None

    with open("stored_hash.txt", "r") as f:
        return f.read().strip()


# Main program
if __name__ == "__main__":
    file_path = input("Enter file path to monitor: ")

    print("\n1. Generate and store hash")
    print("2. Verify file integrity")
    choice = input("Choose an option (1/2): ")

    if choice == "1":
        hash_value = calculate_hash(file_path)
        if hash_value:
            save_hash(file_path, hash_value)
            print("Generated Hash:", hash_value)

    elif choice == "2":
        current_hash = calculate_hash(file_path)
        stored_hash = load_hash()

        if current_hash and stored_hash:
            if current_hash == stored_hash:
                print("✅ File integrity intact. No changes detected.")
            else:
                print("⚠️ File has been modified! Integrity compromised.")

    else:
        print("❌ Invalid option.")