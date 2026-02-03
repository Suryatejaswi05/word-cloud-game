import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection

def check_table(table_name):
    with connection.cursor() as cursor:
        try:
            cursor.execute(f"DESCRIBE {table_name}")
            print(f"\nTable {table_name} exists. Columns:")
            for row in cursor.fetchall():
                print(row)
        except Exception as e:
            print(f"\nTable {table_name} does NOT exist or Error: {e}")

check_table('hackathon_answerevent')
check_table('hackathon_shareevent')
check_table('hackathon_word_v2')
