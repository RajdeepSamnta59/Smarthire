import requests

url = 'http://127.0.0.1:8000/generate-resume/'
data = {
    'fullname': 'Test User',
    'email': 'test@example.com',
    'phone': '1234567890',
    'summary': 'Test Summary',
    'skills': 'Python, Django',
    'experience': 'Test Experience',
    'education': 'Test Education'
}

try:
    # Get the CSRF token first (if needed, but for this simple test we might hit CSRF issues if we don't handle cookies. 
    # However, since I disabled CSRF in the template (wait, I used {% csrf_token %}), I need to handle it.
    # Actually, simpler: I can just use the Django test client if I import it, or just try requests and see if it fails.
    # Using Django test client is safer and doesn't require the server to be running on a specific port if I set up the environment.
    # But the server IS running. Let's try requests first, if it fails due to CSRF, I'll use Django test client.
    
    # Better approach: Use Django Test Client in a script, so I don't need to worry about the running server port or CSRF as much (if I use @csrf_exempt or similar, but I didn't).
    # Actually, let's just use the internal Django testing tools.
    
    import os
    import sys
    import django
    from django.test import Client
    
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JobPortal.settings')
    django.setup()
    
    c = Client()
    response = c.post('/generate-resume/', data)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Success! Resume content generated.")
        print("Content Preview:", response.content.decode('utf-8')[:200])
    else:
        print("Failed.")
        print(response.content)

except Exception as e:
    print(f"Error: {e}")
