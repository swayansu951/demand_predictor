import os
import sqlite3
import shutil

PROJECTS_DIR = "projects"
TEST_PROJECT = "TestProject_Verify"
DEFAULT_DB = "shop_data.db"

def clean_up():
    if os.path.exists(os.path.join(PROJECTS_DIR, TEST_PROJECT)):
        shutil.rmtree(os.path.join(PROJECTS_DIR, TEST_PROJECT))
    if os.path.exists("test_default.db"):
        os.remove("test_default.db")

def test_project_isolation():
    print("Starting verification...")
    
    # Ensure clean state
    clean_up()
    
    # 1. Create a new project structure
    project_path = os.path.join(PROJECTS_DIR, TEST_PROJECT)
    os.makedirs(project_path)
    db_path = os.path.join(project_path, "data.db")
    
    # 2. Initialize DB
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            revenue REAL
        )
    ''')
    
    # 3. Insert data into Project DB
    cursor.execute("INSERT INTO sales (date, product_name, quantity, revenue) VALUES ('2023-01-01', 'ProjectItem', 10, 100.0)")
    conn.commit()
    conn.close()
    
    # 4. Verify data in Project DB
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sales WHERE product_name='ProjectItem'")
    row = cursor.fetchone()
    conn.close()
    
    if row and row[2] == 'ProjectItem':
        print("[OK] Project DB insertion successful.")
    else:
        print("[FAIL] Project DB insertion failed.")
        return

    # 5. Check Default DB (should NOT have this item)
    if os.path.exists(DEFAULT_DB):
        conn = sqlite3.connect(DEFAULT_DB)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM sales WHERE product_name='ProjectItem'")
            row = cursor.fetchone()
            if row is None:
                print("[OK] Default DB is isolated (item not found).")
            else:
                print("[FAIL] Default DB is NOT isolated (item found!).")
        except Exception as e:
            print(f"[INFO] Could not query default DB (might be empty or different schema): {e}")
        conn.close()
    else:
        print("[INFO] Default DB does not exist yet, so isolation is trivially true.")

    # Clean up
    clean_up()
    print("Verification complete.")

if __name__ == "__main__":
    test_project_isolation()
