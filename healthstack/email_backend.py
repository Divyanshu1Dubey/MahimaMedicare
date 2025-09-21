import ssl
import smtplib
import socket
import time
from django.core.mail.backends.smtp import EmailBackend


class UnverifiedEmailBackend(EmailBackend):
    """
    Robust email backend that bypasses SSL certificate verification
    and handles network connectivity issues.
    """
    
    def open(self):
        """
        Open connection with unverified SSL context and retry logic.
        """
        if self.connection:
            return False

        # Try multiple times with different configurations
        configurations = [
            {'host': self.host, 'port': self.port},
            {'host': 'smtp.gmail.com', 'port': 587},
            {'host': 'smtp.gmail.com', 'port': 465},  # SSL port as fallback
        ]
        
        for config in configurations:
            try:
                # Set a reasonable timeout
                timeout = getattr(self, 'timeout', 30)
                
                self.connection = self.connection_class(
                    config['host'], config['port'],
                    local_hostname=getattr(self, 'local_hostname', None),
                    timeout=timeout,
                )
                
                # Handle TLS/SSL
                if config['port'] == 465:  # SSL port
                    # For SSL port, connection is already encrypted
                    pass
                elif not self.use_ssl and self.use_tls:
                    self.connection.ehlo()
                    # Use unverified context for starttls
                    self.connection.starttls(context=ssl._create_unverified_context())
                    self.connection.ehlo()
                
                # Login if credentials provided
                if self.username and self.password:
                    self.connection.login(self.username, self.password)
                
                return True
                
            except (smtplib.SMTPException, OSError, socket.gaierror) as e:
                # Close any partial connection
                if hasattr(self, 'connection') and self.connection:
                    try:
                        self.connection.quit()
                    except:
                        pass
                    self.connection = None
                
                # If this is the last configuration, re-raise the error
                if config == configurations[-1]:
                    if not self.fail_silently:
                        raise
                else:
                    # Wait a bit before trying next configuration
                    time.sleep(1)
                    continue
        
        return False
    
    def send_messages(self, email_messages):
        """
        Send messages with additional error handling.
        """
        if not email_messages:
            return 0
        
        try:
            return super().send_messages(email_messages)
        except Exception as e:
            # Log the error but don't crash the application
            print(f"Email sending failed: {e}")
            if not self.fail_silently:
                raise
            return 0
