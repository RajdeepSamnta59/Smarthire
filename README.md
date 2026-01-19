# SmartHire — Smart Recruitment System

A small, friendly  app to help recruiters screen resumes and generate neat resumes for candidates. Built with simple parsing tools and a lightweight ranking flow so you can prototype hiring workflows quickly.

**Highlights**
- Easy resume parsing: basic email, phone, skills and CGPA extraction (`mysite/resume_parser.py`).
- Resume generation: HTML resume generator with a Gemini-backed option and a safe fallback (`mysite/resume_generator.py`).
- Ranking & evaluation helpers to compare applicants against job requirements (`mysite/evaluate_performance.py`).

**Quick start**
1. Create and activate a virtualenv (Windows PowerShell):

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
``` 

2. Install deps and run migrations:

```bash
pip install -r requirements.txt
python manage.py migrate
```

3. Run the dev server:

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/ to explore the app and the templates in `mysite/templates/mysite`.

**Where to look next**
- Job logic & models: `mysite/models.py` and `mysite/views.py`
- Resume parsing: `mysite/resume_parser.py`
- Resume generation: `mysite/resume_generator.py`
- Evaluation and testing helpers: `mysite/evaluate_performance.py` and `mysite/tests.py`


---
