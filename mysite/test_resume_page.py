import os
import sys
import django
from django.test import Client

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JobPortal.settings')
django.setup()

c = Client()
response = c.get('/generate-resume/')

print(f"Status Code: {response.status_code}")
content = response.content.decode('utf-8')

if 'Generate Professional Resume' in content and '<form' in content:
    print("Success! Page renders with form.")
else:
    print("Failed. Content missing.")
    # print(content[:500]) # Debug
