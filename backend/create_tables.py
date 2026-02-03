import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection

sql_commands = [
    """
    CREATE TABLE IF NOT EXISTS hackathon_appuser (
      id bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
      team_no int UNSIGNED NULL UNIQUE,
      username varchar(150) NOT NULL UNIQUE,
      email varchar(254) NULL UNIQUE,
      phone varchar(32) NULL UNIQUE,
      password_salt_b64 varchar(64) NOT NULL DEFAULT '',
      password_hash_b64 varchar(128) NOT NULL DEFAULT '',
      password_iterations int UNSIGNED NOT NULL DEFAULT 1000,
      is_active bool NOT NULL DEFAULT 1,
      created_at datetime(6) NOT NULL,
      updated_at datetime(6) NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS hackathon_appusermember (
      id bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
      member_id varchar(64) NULL UNIQUE,
      name varchar(255) NOT NULL,
      email varchar(254) NULL,
      phone varchar(32) NOT NULL,
      created_at datetime(6) NOT NULL,
      updated_at datetime(6) NOT NULL,
      user_id bigint NOT NULL,
      CONSTRAINT hackathon_appusermember_user_id_fk_hackathon_appuser_id 
        FOREIGN KEY (user_id) REFERENCES hackathon_appuser (id) ON DELETE CASCADE,
      CONSTRAINT uniq_member_phone_per_team UNIQUE (user_id, phone)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS hackathon_authsession (
      id bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
      token_hash varchar(255) NOT NULL UNIQUE,
      created_at datetime(6) NOT NULL,
      expires_at datetime(6) NULL,
      revoked_at datetime(6) NULL,
      member_id bigint NULL,
      user_id bigint NOT NULL,
      CONSTRAINT hackathon_authsession_user_id_fk_hackathon_appuser_id 
        FOREIGN KEY (user_id) REFERENCES hackathon_appuser (id) ON DELETE CASCADE,
      CONSTRAINT hackathon_authsession_member_id_fk 
        FOREIGN KEY (member_id) REFERENCES hackathon_appusermember (id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS hackathon_otpchallenge (
      id bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
      phone varchar(20) NOT NULL,
      code varchar(10) NOT NULL,
      created_at datetime(6) NOT NULL,
      expires_at datetime(6) NULL,
      consumed_at datetime(6) NULL
    );
    """
]

with connection.cursor() as cursor:
    for sql in sql_commands:
        try:
            print(f"Executing SQL...")
            cursor.execute(sql)
            print("Success.")
        except Exception as e:
            print(f"Error: {e}")
