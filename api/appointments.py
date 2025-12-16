from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime

appointments = []

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

            appointment = {
                "id": len(appointments) + 1,
                "name": data.get('name'),
                "email": data.get('email'),
                "phone": data.get('phone'),
                "service_type": data.get('service_type'),
                "preferred_date": data.get('preferred_date'),
                "preferred_time": data.get('preferred_time'),
                "message": data.get('message'),
                "status": "pending",
                "created_at": datetime.now().isoformat()
            }
            appointments.append(appointment)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                "id": appointment["id"],
                "message": f"Thank you {data.get('name')}! Your appointment request has been received.",
                "status": "pending"
            }).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def do_GET(self):
        admin_token = self.path.split('admin_token=')[-1] if 'admin_token=' in self.path else ''
        if admin_token != 'wallet-wealth-admin-2024':
            self.send_response(401)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Admin access required"}).encode())
            return

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"appointments": appointments, "total": len(appointments)}).encode())
