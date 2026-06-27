import urllib.request
import json

import sys

def test_server(custom_prompt=None):
    url = "http://127.0.0.1:8000/parse"
    prompt = custom_prompt or "Organize new leads from Gmail into Salesforce and notify Slack"
    payload = {
        "user_input": prompt
    }
    
    print(f"Calling: {url}")
    print(f"Payload: {json.dumps(payload)}")
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as response:
            status_code = response.getcode()
            body = response.read().decode('utf-8')
            print(f"Status Code: {status_code}")
            print("Response Body:")
            print(json.dumps(json.loads(body), indent=2))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}")
        print("Response Body:")
        print(e.read().decode('utf-8'))
    except Exception as e:
        print(f"Error calling server: {e}")

if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else None
    test_server(p)
