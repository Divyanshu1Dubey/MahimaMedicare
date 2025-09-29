#!/usr/bin/env python3
"""
Simple webhook server for GitHub auto-deployment
Run this on your Vultr server to listen for GitHub pushes
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import subprocess
import threading
import os

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/github-webhook':
            try:
                # Read the request
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                
                # Parse JSON
                data = json.loads(post_data.decode('utf-8'))
                
                print(f"Received webhook: {data}")
                
                # Trigger deployment in background
                threading.Thread(target=self.deploy).start()
                
                # Respond immediately
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status": "deployment_triggered"}')
                
            except Exception as e:
                print(f"Error: {e}")
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b'{"error": "deployment_failed"}')
        else:
            self.send_response(404)
            self.end_headers()
    
    def deploy(self):
        """Run the deployment script"""
        try:
            os.chdir('/var/www/mahima-medicare')
            result = subprocess.run(['bash', 'deploy_script.sh'], 
                                  capture_output=True, text=True, timeout=300)
            print("Deployment output:", result.stdout)
            if result.stderr:
                print("Deployment errors:", result.stderr)
        except Exception as e:
            print(f"Deployment failed: {e}")

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8080), WebhookHandler)
    print("Webhook server running on port 8080...")
    print("Ready to receive GitHub deployments!")
    server.serve_forever()