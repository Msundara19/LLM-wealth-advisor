from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request

GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')

SYSTEM_PROMPT = """You are an AI Financial Advisor for Wallet Wealth LLP, a SEBI Registered Investment Advisor based in Chennai, India.

Company: Wallet Wealth LLP - "The Winners Choice"
SEBI Registration: INA200015440
CEO: S. Sridharan (20+ years experience, Associate Financial Planner certification)
Contact: 9940116967 | sridharan@walletwealth.co.in
Location: Chennai, Tamil Nadu, India
Services: Mutual Fund Advisory, Portfolio Management, Financial Planning, Tax Planning, Retirement Planning, Insurance Planning

Guidelines:
- Be professional and helpful
- Speak as part of the team (use "we", "our", "us")
- For CEO questions, say "Our CEO is S. Sridharan..."
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

            if not GROQ_API_KEY:
                response_text = "LLM service not configured."
            else:
                # Use HTTP API directly instead of SDK
                req_data = json.dumps({
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": message}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1024
                }).encode('utf-8')

                req = urllib.request.Request(
                    'https://api.groq.com/openai/v1/chat/completions',
                    data=req_data,
                    headers={
                        'Authorization': f'Bearer {GROQ_API_KEY}',
                        'Content-Type': 'application/json'
                    }
                )

                with urllib.request.urlopen(req) as response:
                    result = json.loads(response.read().decode('utf-8'))
                    response_text = result['choices'][0]['message']['content']

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"response": response_text, "model": "llama-3.3-70b-versatile"}).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"response": f"Error: {str(e)}", "model": "error"}).encode())

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"message": "Chat API ready"}).encode())
