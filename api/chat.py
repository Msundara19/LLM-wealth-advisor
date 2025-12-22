from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.error

# Support both Groq and OpenRouter - use whichever key is available
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '')

SYSTEM_PROMPT = """You are an AI Financial Advisor for Wallet Wealth LLP, a SEBI Registered Investment Advisor based in Chennai, India.

Company: Wallet Wealth LLP - The Winners Choice
SEBI Registration: INA200015440
CEO: S. Sridharan (20+ years experience, Associate Financial Planner certification)
Contact: 9940116967 | sridharan@walletwealth.co.in
Location: Chennai, Tamil Nadu, India
Services: Mutual Fund Advisory, Portfolio Management, Financial Planning, Tax Planning, Retirement Planning, Insurance Planning

Guidelines:
- Be professional and helpful
- Speak as part of the team using we, our, us
- For CEO questions, say Our CEO is S. Sridharan
"""

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            message = data.get('message', '')

            # Determine which API to use
            if OPENROUTER_API_KEY:
                api_url = 'https://openrouter.ai/api/v1/chat/completions'
                api_key = OPENROUTER_API_KEY
                model = 'meta-llama/llama-3.3-8b-instruct:free'
                headers = {
                    'Authorization': 'Bearer ' + api_key,
                    'Content-Type': 'application/json',
                    'HTTP-Referer': 'https://walletwealth.co.in',
                    'X-Title': 'Wallet Wealth AI Advisor'
                }
            elif GROQ_API_KEY:
                api_url = 'https://api.groq.com/openai/v1/chat/completions'
                api_key = GROQ_API_KEY
                model = 'llama-3.1-8b-instant'
                headers = {
                    'Authorization': 'Bearer ' + api_key,
                    'Content-Type': 'application/json'
                }
            else:
                response_text = "LLM service not configured. Please set OPENROUTER_API_KEY or GROQ_API_KEY environment variable."
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"response": response_text, "model": "none"}).encode())
                return

            req_data = json.dumps({
                "model": model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": message}
                ],
                "temperature": 0.7,
                "max_tokens": 1024
            }).encode('utf-8')

            req = urllib.request.Request(api_url, data=req_data, headers=headers)

            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                response_text = result['choices'][0]['message']['content']

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"response": response_text, "model": model}).encode())

        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else ''
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                "response": f"Error: HTTP Error {e.code}: {e.reason}. Details: {error_body}",
                "model": "error"
            }).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"response": "Error: " + str(e), "model": "error"}).encode())

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        api_status = "none"
        if OPENROUTER_API_KEY:
            api_status = f"OpenRouter (key length: {len(OPENROUTER_API_KEY)})"
        elif GROQ_API_KEY:
            api_status = f"Groq (key length: {len(GROQ_API_KEY)})"
        self.wfile.write(json.dumps({
            "message": "Chat API ready",
            "api_configured": api_status
        }).encode())
