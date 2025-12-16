from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({
            "message": "Welcome to Wallet Wealth LLM Advisor API",
            "status": "running",
            "llm_configured": bool(os.environ.get('GROQ_API_KEY', ''))
        }).encode())
