import sqlite3
import json
import os
 
# Path to the SQLite database
db_path = 'northwind.db'
 
# Path to the metadata file
metadata_file = 'metadata.json'
 
def get_existing_metadata():
    """Read the existing metadata file."""
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r') as file:
            return json.load(file)
    return {}
 
def update_metadata(new_metadata):
    """Update the metadata file."""
    with open(metadata_file, 'w') as file:
        json.dump(new_metadata, file, indent=4)
 
def get_current_tables(cursor):
    """Get the list of tables in the current database."""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [row[0] for row in cursor.fetchall()]
 
def table_exists(cursor, table_name):
    """Check if a table exists in the database."""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
    return cursor.fetchone() is not None
 
def rename_table():
    """Rename the table from 'Order Details' to 'Orderdetails'."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if table_exists(cursor, "Order Details"):
        cursor.execute('ALTER TABLE "Order Details" RENAME TO Orderdetails;')
        conn.commit()
        print("Table 'Order Details' renamed to 'Orderdetails'.")
    else:
        print("Table 'Order Details' does not exist.")
    conn.close()
 
def add_test_table():
    """Add a test table to the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id TEXT,
        question TEXT,
        response TEXT,
        answer TEXT,
        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')
    conn.commit()
    conn.close()
    print("chats table added.")
 
def drop_test_table():
    """Drop the test table from the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS chats;')
    conn.commit()
    conn.close()
    print("chats table dropped.")
 
def get_table_metadata(cursor, table_name):
    """Get metadata for a specific table."""
    cursor.execute(f'PRAGMA table_info("{table_name}");')
    columns = cursor.fetchall()
    metadata = {
        'columns': [],
        'primary_keys': []
    }
    for col in columns:
        column_info = {
            'name': col[1],
            'type': col[2],
            'notnull': bool(col[3]),
            'default_value': col[4],
            'primary_key': bool(col[5])
        }
        metadata['columns'].append(column_info)
        if col[5]:
            metadata['primary_keys'].append(col[1])
    return metadata
 
def main():
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
   
    # Rename the table
    rename_table()
   
    # Get the current tables in the database
    current_tables = get_current_tables(cursor)
   
    # Get the existing metadata
    existing_metadata = get_existing_metadata()
   
    # Update the metadata with current table information
    new_metadata = {'tables': {}}
    for table in current_tables:
        new_metadata['tables'][table] = get_table_metadata(cursor, table)
   
    # Determine new tables that have been added
    new_tables = [table for table in current_tables if table not in existing_metadata.get('tables', {})]
   
    if new_tables:
        print(f"New tables detected: {new_tables}")
        # Update the metadata file
        update_metadata(new_metadata)
        print("Metadata file updated.")
    else:
        print("No new tables detected.")
   
    # Close the database connection
    conn.close()
 
if __name__ == '__main__':
    add_test_table()
    main()