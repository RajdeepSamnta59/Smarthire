import warnings
try:
    import textract
    TEXTRACT_AVAILABLE = True
except Exception:
    textract = None
    TEXTRACT_AVAILABLE = False
import re
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.neighbors import NearestNeighbors
import PyPDF2
import pathlib
from json import load, dumps
from operator import getitem
from collections import OrderedDict
from .text_process import normalize
import os

import nltk
try:
    import nltk.data
    nltk.data.find('tokenizers/punkt')
except Exception:
    import nltk
    nltk.download('punkt')

from nltk.tokenize import word_tokenize
import mysite.configurations as regex
from datetime import date
from mysite.resume_parser import parse_resume
from django.conf import settings

# Weights for ranking
WEIGHT_SKILLS = 0.4
WEIGHT_CONTENT = 0.3
WEIGHT_EXP = 0.2
WEIGHT_CGPA = 0.1

def get_text_from_file(filepath):
    """
    Extract text from a file (PDF, DOC, DOCX)
    """
    ext = os.path.splitext(filepath)[1].lower()
    text = ""
    try:
        if ext == '.pdf':
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f, strict=False)
                for page in reader.pages:
                    text += page.extract_text() + " "
        elif ext in ['.doc', '.docx']:
            if TEXTRACT_AVAILABLE:
                text = textract.process(filepath).decode('utf-8')
            else:
                return "" # Handle missing textract
        
        # Clean text
        text = text.replace('\n', ' ').replace('\r', ' ')
        return text
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return ""

def calculate_jaccard_similarity(doc_skills, job_skills):
    if not job_skills:
        return 0.0
    
    doc_set = set(doc_skills.lower().split(', '))
    job_set = set(job_skills.lower().split(', '))
    
    # Remove empty strings
    doc_set.discard('')
    job_set.discard('')
    
    if not job_set:
        return 0.0
        
    intersection = len(doc_set.intersection(job_set))
    union = len(doc_set.union(job_set))
    
    return intersection / union if union > 0 else 0.0

def res(resumes_data, job_data):
    """
    Main ranking function.
    resumes_data: QuerySet of Apply_job
    job_data: PostJob object
    """
    result_arr = []
    
    # Prepare Job Description Text for TF-IDF
    job_desc_text = f"{job_data.details} {job_data.responsibilities} {job_data.required_skills}"
    try:
        norm_job_desc = normalize(word_tokenize(job_desc_text))
        job_desc_str = ' '.join(norm_job_desc)
    except:
        job_desc_str = ""
        
    # Vectorizer for TF-IDF
    vectorizer = CountVectorizer(stop_words='english')
    transformer = TfidfTransformer()
    
    # We need to fit vectorizer on all documents (Job + Resumes) to have same vocabulary
    # But for simplicity and existing logic, we can just fit on Job + Current Resume pair or all at once.
    # Let's collect all texts first.
    
    candidate_texts = []
    candidates = []
    
    base_media_path = os.path.join(settings.MEDIA_ROOT)
    
    print(f"Processing {len(resumes_data)} resumes...")
    
    for candidate in resumes_data:
        # File path
        if not candidate.cv:
            continue
            
        file_path = os.path.join(base_media_path, str(candidate.cv))
        
        # 1. Extract Text
        if candidate.parsed_text:
            text = candidate.parsed_text
        else:
            text = get_text_from_file(file_path)
            if not text:
                continue
            candidate.parsed_text = text
            candidate.save()
            
        # 2. Parse Structured Data (if not already parsed or we want to refresh)
        # For now, let's always refresh to ensure new parser logic is applied
        parsed_data = parse_resume(text)
        
        # 3. Update Candidate Object
        candidate.skills = parsed_data['skills']
        candidate.cgpa = parsed_data['cgpa']
        candidate.experience_years = parsed_data['experience']
        candidate.college = parsed_data['college']
        if parsed_data['email']:
            candidate.email = parsed_data['email'] # Update email if found in resume
        
        # 4. Calculate Scores
        
        # A. Skills Score (Jaccard)
        skills_score = calculate_jaccard_similarity(candidate.skills, job_data.required_skills)
        
        # B. Experience Score
        # If candidate exp >= job min exp, full score. Else proportional.
        if job_data.min_experience > 0:
            exp_score = min(candidate.experience_years / job_data.min_experience, 1.0)
        else:
            exp_score = 1.0
            
        # C. CGPA Score
        if job_data.min_cgpa > 0:
            cgpa_score = min(candidate.cgpa / job_data.min_cgpa, 1.0)
        else:
            cgpa_score = 1.0
            
        # D. Content Similarity (TF-IDF) - Deferred to batch step or calculated here pairwise
        # Let's do pairwise for simplicity or add to list for batch
        candidate_texts.append(text)
        candidates.append({
            'obj': candidate,
            'skills_score': skills_score,
            'exp_score': exp_score,
            'cgpa_score': cgpa_score,
            'text': text
        })

    # Batch TF-IDF
    if candidates:
        all_docs = [job_desc_str] + [c['text'] for c in candidates]
        try:
            tfidf_matrix = transformer.fit_transform(vectorizer.fit_transform(all_docs))
            # Job vector is at index 0
            job_vector = tfidf_matrix[0]
            
            # Calculate similarity for each candidate
            # We can use cosine similarity or NearestNeighbors
            # Existing used NearestNeighbors, let's stick to cosine for simplicity or NN
            # Cosine similarity is dot product of normalized vectors
            from sklearn.metrics.pairwise import cosine_similarity
            
            # cosine_similarity returns matrix
            similarities = cosine_similarity(job_vector, tfidf_matrix[1:])
            
            for i, c in enumerate(candidates):
                content_score = similarities[0][i]
                
                # Final Weighted Score
                final_score = (
                    (c['skills_score'] * WEIGHT_SKILLS) +
                    (content_score * WEIGHT_CONTENT) +
                    (c['exp_score'] * WEIGHT_EXP) +
                    (c['cgpa_score'] * WEIGHT_CGPA)
                )
                
                c['obj'].similarity_score = final_score * 100 # Scale to 0-100
                c['obj'].save()
                
                result_arr.append({
                    'rank': 0, # To be assigned
                    'name': c['obj'].name,
                    'email': c['obj'].email,
                    'score': final_score * 100,
                    'skills_match': c['skills_score'] * 100,
                    'experience': c['obj'].experience_years,
                    'cgpa': c['obj'].cgpa,
                    'college': c['obj'].college,
                    'skills': c['obj'].skills,
                    'cv_url': c['obj'].cv.url
                })
                
        except Exception as e:
            print(f"Error in TF-IDF: {e}")
            
    # Sort by score
    result_arr.sort(key=lambda x: x['score'], reverse=True)
    
    # Assign Rank
    for i, item in enumerate(result_arr):
        item['rank'] = i + 1
        
    return result_arr
