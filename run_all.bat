@echo off
call .venv\Scripts\activate
python save_content.py
python collect_site_urls.py
pause