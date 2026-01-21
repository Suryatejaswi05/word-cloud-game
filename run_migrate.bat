@echo off
cd /d "c:\Users\Tharunya\full stack\word claude\team22\backend"
call "c:\Users\Tharunya\full stack\word claude\team22\.venv\Scripts\activate"
python manage.py migrate
pause