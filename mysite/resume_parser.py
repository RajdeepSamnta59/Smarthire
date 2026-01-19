import re

def extract_email(text):
    email = re.findall(r"([^@|\s]+@[^@]+\.[^@|\s]+)", text)
    if email:
        try:
            return email[0].split()[0].strip(';')
        except IndexError:
            return None
    return None

def extract_phone(text):
    # Regex for finding phone numbers
    phone = re.findall(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})', text)
    if phone:
        number = ''.join(phone[0])
        if len(number) > 10:
            return '+' + number
        else:
            return number
    return None

def extract_cgpa(text):
    # Look for patterns like "CGPA: 3.5", "GPA 3.5/4.0", "8.5/10"
    # This regex looks for a float number followed by /4.0 or /10.0 or just labelled as CGPA
    
    # Pattern 1: Explicit CGPA/GPA label
    pattern1 = r"(?:CGPA|GPA|SGPA)[\s:=-]+(\d+(?:\.\d+)?)"
    match = re.search(pattern1, text, re.IGNORECASE)
    if match:
        try:
            val = float(match.group(1))
            if val <= 10.0: # Sanity check
                return val
        except:
            pass
            
    # Pattern 2: X.X/Y.Y format
    pattern2 = r"(\d+(?:\.\d+)?)\s*/\s*(?:4\.0|10\.0|10|4)"
    match = re.search(pattern2, text)
    if match:
        try:
            val = float(match.group(1))
            return val
        except:
            pass
            
    return 0.0

def extract_experience(text):
    # This is tricky. We can look for "X years experience" or calculate from dates.
    # Reusing/Refining logic from existing screen.py or writing new simple regex.
    
    # Simple regex for "X years"
    pattern = r"(\d+(?:\.\d+)?)\s+(?:years?|yrs?)\s+(?:of\s+)?experience"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        try:
            return float(match.group(1))
        except:
            pass
            
    # If explicit mention not found, we might rely on the existing date-based logic in screen.py
    # But for this parser, let's return 0.0 if not explicitly found, and let screen.py handle the fallback.
    return 0.0

def extract_skills(text, skills_db=None):
    if skills_db is None:
        # A basic list of common tech skills
        skills_db = [
            'python', 'java', 'c++', 'c#', 'javascript', 'typescript', 'html', 'css', 'react', 'angular', 'vue',
            'django', 'flask', 'spring', 'springboot', 'node.js', 'express', 'sql', 'mysql', 'postgresql', 'mongodb',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git', 'linux', 'machine learning', 'deep learning',
            'nlp', 'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn', 'data analysis', 'rest api', 'graphql'
        ]
    
    found_skills = []
    text_lower = text.lower()
    for skill in skills_db:
        # Simple substring match, but can be improved with word boundaries
        # \b ensures we don't match "java" in "javascript" if we check java first, 
        # but "javascript" is in list, so it's fine. 
        # Better: re.search(r'\b' + re.escape(skill) + r'\b', text_lower)
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            found_skills.append(skill)
            
    return ", ".join(found_skills)

def extract_college(text):
    # Heuristic: Look for keywords like "University", "Institute", "College"
    # and try to grab the surrounding text.
    # This is hard to do perfectly without NER.
    
    # Regex to capture "University of X" or "X University" or "X Institute of Technology"
    # This is a naive approach.
    
    keywords = [
        r"([A-Z][a-zA-Z\s&]+University)",
        r"([A-Z][a-zA-Z\s&]+Institute of [a-zA-Z\s]+)",
        r"([A-Z][a-zA-Z\s&]+College)",
        r"(IIT\s+[a-zA-Z]+)",
        r"(NIT\s+[a-zA-Z]+)",
        r"(BITS\s+[a-zA-Z]+)"
    ]
    
    for pattern in keywords:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
            
    return ""

def parse_resume(text):
    return {
        "email": extract_email(text),
        "phone": extract_phone(text),
        "cgpa": extract_cgpa(text),
        "experience": extract_experience(text),
        "skills": extract_skills(text),
        "college": extract_college(text)
    }
