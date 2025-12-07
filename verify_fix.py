import os
import time

# Mock environment
UPLOAD_DIR = "test_uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Clean start
for f in os.listdir(UPLOAD_DIR):
    os.remove(os.path.join(UPLOAD_DIR, f))

# Scenario 1: First Upload
filename = "data.xlsx"
timestamp1 = int(time.time())
saved_name1 = f"{timestamp1}_{filename}"
with open(os.path.join(UPLOAD_DIR, saved_name1), 'w') as f:
    f.write("content 1")
print(f"Created initial file: {saved_name1}")

# Verify it exists
files = os.listdir(UPLOAD_DIR)
assert len(files) == 1
assert saved_name1 in files

# Scenario 2: Second Upload (Duplicate)
print("Simulating second upload...")
new_filename = "data.xlsx" # Same name
# Logic under test
existing_files = os.listdir(UPLOAD_DIR)
for existing_file in existing_files:
    try:
        parts = existing_file.split('_', 1)
        if len(parts) > 1:
            stored_filename = parts[1]
            if stored_filename == new_filename:
                print(f"Found duplicate: {existing_file}. Removing...")
                os.remove(os.path.join(UPLOAD_DIR, existing_file))
    except Exception:
        continue

timestamp2 = int(time.time()) + 10 # ensure diff timestamp
saved_name2 = f"{timestamp2}_{new_filename}"
with open(os.path.join(UPLOAD_DIR, saved_name2), 'w') as f:
    f.write("content 2")

# Verify result
files = os.listdir(UPLOAD_DIR)
print(f"Final files: {files}")

assert len(files) == 1, f"Expected 1 file, found {len(files)}"
assert saved_name2 in files
assert saved_name1 not in files
print("SUCCESS: Duplicate removed, new file kept.")

# Cleanup
for f in os.listdir(UPLOAD_DIR):
    os.remove(os.path.join(UPLOAD_DIR, f))
os.rmdir(UPLOAD_DIR)
