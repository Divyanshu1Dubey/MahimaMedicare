"""
Custom runserver command that handles HTTPS requests gracefully
"""

from django.core.management.commands.runserver import Command as RunserverCommand
from django.core.servers.basehttp import ThreadedWSGIServer, WSGIRequestHandler
import socket

class QuietWSGIRequestHandler(WSGIRequestHandler):
    """Custom request handler that suppresses HTTPS error messages"""
    
    def log_message(self, format, *args):
        # Only log if it's not an HTTPS error
        if "You're accessing the development server over HTTPS" not in format % args:
            super().log_message(format, *args)
    
    def handle(self):
        """Handle requests and catch SSL errors silently"""
        try:
            super().handle()
        except (ConnectionResetError, BrokenPipeError, socket.error):
            # Silently ignore connection errors from HTTPS attempts
            pass

class QuietThreadedWSGIServer(ThreadedWSGIServer):
    """Custom server that uses our quiet request handler"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.RequestHandlerClass = QuietWSGIRequestHandler

class Command(RunserverCommand):
    """Custom runserver command"""
    
    def get_handler(self, *args, **options):
        """Return the default WSGI handler for the runner."""
        return super().get_handler(*args, **options)
    
    def run(self, **options):
        """Run the server with custom handler"""
        # Use our quiet server
        self.httpd_cls = QuietThreadedWSGIServer
        super().run(**options)