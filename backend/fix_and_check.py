import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection

def create_share_event_table():
    with connection.cursor() as cursor:
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hackathon_shareevent (
                    id bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
                    event_name varchar(100) NULL,
                    round_id bigint NULL,
                    player_id varchar(255) NULL,
                    created_at datetime(6) NOT NULL
                )
            """)
            print("Created hackathon_shareevent table.")
        except Exception as e:
            print(f"Error creating table: {e}")

def check_word_data():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM hackathon_word_v2")
        rows = cursor.fetchall()
        print(f"\nWord Rows ({len(rows)}):")
        for row in rows:
            print(row)

create_share_event_table()
check_word_data()
