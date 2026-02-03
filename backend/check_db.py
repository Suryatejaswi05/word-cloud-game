import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from hackathon.models import AppUserMember
from django.db import connection

try:
    print(f"Count: {AppUserMember.objects.count()}")
    print("Table exists.")
except Exception as e:
    print(f"Error: {e}")
    # List tables
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        print("Tables:", tables)
