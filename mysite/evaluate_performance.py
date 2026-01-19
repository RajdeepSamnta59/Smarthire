import os
import sys
import django
import time
import pandas as pd
from django.conf import settings

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JobPortal.settings')
django.setup()

from mysite.models import PostJob, Apply_job
from mysite import screen

def evaluate():
    print("--- Performance Matrix Evaluation ---")
    
    # 1. Select a Job for evaluation (or create a dummy one)
    job = PostJob.objects.first()
    if not job:
        print("No jobs found in database. Please post a job first.")
        return

    print(f"Evaluating against Job: {job.title} ({job.company_name})")
    print(f"Required Skills: {job.required_skills}")
    
    # 2. Get Resumes (using existing Apply_job entries for this job, or all)
    # For broader testing, let's use all resumes in the system and pretend they applied to this job
    # But `screen.res` expects Apply_job objects.
    # So we will fetch actual applicants for this job.
    applicants = Apply_job.objects.filter(company_name=job.company_name, title=job.title, cv__isnull=False)
    
    if not applicants.exists():
        print("No applicants found for this job.")
        return

    print(f"Found {applicants.count()} applicants.")

    # 3. Measure Execution Time
    start_time = time.time()
    
    # Run the ranking algorithm
    results = screen.res(applicants, job)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\nExecution Time: {duration:.4f} seconds")
    print(f"Average Time per Resume: {duration/applicants.count():.4f} seconds")
    
    # 4. Analyze Results
    df = pd.DataFrame(results)
    
    if df.empty:
        print("No results returned.")
        return
        
    print("\n--- Top 5 Candidates ---")
    print(df[['rank', 'name', 'score', 'skills_match', 'experience']].head(5).to_string(index=False))
    
    print("\n--- Score Distribution ---")
    print(df['score'].describe())
    
    # 5. Recommendations
    print("\n--- Recommendations ---")
    if duration > 5.0:
        print("- Performance Warning: Ranking is taking too long. Consider optimizing TF-IDF or caching.")
    else:
        print("- Performance: Good.")
        
    if df['score'].max() < 10.0:
        print("- Data Quality Warning: Top scores are very low. Check if resume parsing is working correctly or if job requirements are too strict.")

if __name__ == "__main__":
    evaluate()
