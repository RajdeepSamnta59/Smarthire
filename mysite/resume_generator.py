import google.generativeai as genai
from django.conf import settings

def generate_resume_content(data):
    """
    Generates a resume based on the provided data using Google Gemini API.
    """
    
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    
    if not api_key or api_key == 'YOUR_API_KEY_HERE':
        # Fallback to mock if key is missing
        return _generate_mock_resume(data)
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        You are a professional resume writer. Create a clean, professional HTML resume for the following candidate.
        Return ONLY the HTML code (no markdown backticks, no explanations).
        Use inline CSS for styling to ensure it looks good.
        
        Details:
        Name: {data.get('fullname')}
        Email: {data.get('email')}
        Phone: {data.get('phone')}
        Summary: {data.get('summary')}
        Skills: {data.get('skills')}
        Experience: {data.get('experience')}
        Education: {data.get('education')}
        """
        
        response = model.generate_content(prompt)
        return response.text.replace('```html', '').replace('```', '')
        
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return _generate_mock_resume(data, error_message=str(e))

def _generate_mock_resume(data, error_message=None):
    # Returns a simple HTML string representing the resume (Fallback)
    
    warning_text = "Note: This is a generated placeholder. To get a professional AI-written resume, please add your Gemini API Key in settings.py."
    if error_message:
        warning_text = f"<strong>Gemini API Error:</strong> {error_message}<br>Showing placeholder resume."
    
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .header h1 {{ margin: 0; color: #2c3e50; }}
            .header p {{ margin: 5px 0; }}
            .section {{ margin-bottom: 20px; }}
            .section h2 {{ border-bottom: 2px solid #2c3e50; padding-bottom: 5px; color: #2c3e50; }}
            .content {{ margin-left: 20px; }}
            .warning {{ background: #fff3cd; color: #856404; padding: 10px; margin-bottom: 20px; border: 1px solid #ffeeba; }}
        </style>
    </head>
    <body>
        <div class="warning">
            {warning_text}
        </div>
        <div class="header">
            <h1>{data.get('fullname', 'Name')}</h1>
            <p>{data.get('email', 'Email')} | {data.get('phone', 'Phone')}</p>
        </div>
        
        <div class="section">
            <h2>Professional Summary</h2>
            <div class="content">
                <p>{data.get('summary', '')}</p>
            </div>
        </div>
        
        <div class="section">
            <h2>Skills</h2>
            <div class="content">
                <p>{data.get('skills', '')}</p>
            </div>
        </div>
        
        <div class="section">
            <h2>Experience</h2>
            <div class="content">
                <p>{data.get('experience', '').replace(chr(10), '<br>')}</p>
            </div>
        </div>
        
        <div class="section">
            <h2>Education</h2>
            <div class="content">
                <p>{data.get('education', '').replace(chr(10), '<br>')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content
