import sqlite3

def list_files_in_db(db_path="database.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, modified_time, root_folder_name FROM files WHERE is_directory = 0")
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    files = list_files_in_db()
    for f in files:
        print(f)

