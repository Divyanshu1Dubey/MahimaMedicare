import ssl
import smtplib
import socket
import time
import logging
from django.core.mail.backends.smtp import EmailBackend

# Set up logging
logger = logging.getLogger(__name__)

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
                logger.info(f"Attempting connection to {config['host']}:{config['port']}")
                
                # Set a reasonable timeout
                timeout = getattr(self, 'timeout', 30)
                
                self.connection = self.connection_class(
                    config['host'], config['port'],
                    local_hostname=getattr(self, 'local_hostname', None),
                    timeout=timeout,
                )
                
                logger.info(f"Connected to {config['host']}:{config['port']}")
                
                # Handle TLS/SSL
                if config['port'] == 465:  # SSL port
                    logger.info("Using SSL connection (port 465)")
                    # For SSL port, connection is already encrypted
                    pass
                elif not self.use_ssl and self.use_tls:
                    logger.info("Starting TLS connection")
                    self.connection.ehlo()
                    # Use unverified context for starttls
                    self.connection.starttls(context=ssl._create_unverified_context())
                    self.connection.ehlo()
                    logger.info("TLS connection established")
                
                # Login if credentials provided
                if self.username and self.password:
                    logger.info(f"Attempting login for user: {self.username}")
                    # Clean up password - remove spaces that might be in app password
                    clean_password = self.password.replace(' ', '')
                    self.connection.login(self.username, clean_password)
                    logger.info("Login successful")
                
                logger.info("Email connection established successfully")
                return True
                
            except (smtplib.SMTPException, OSError, socket.gaierror) as e:
                logger.warning(f"Connection failed for {config['host']}:{config['port']} - {str(e)}")
                # Close any partial connection
                if hasattr(self, 'connection') and self.connection:
                    try:
                        self.connection.quit()
                    except:
                        pass
                    self.connection = None
                
                # If this is the last configuration, re-raise the error
                if config == configurations[-1]:
                    logger.error(f"All connection configurations failed. Last error: {str(e)}")
                    if not self.fail_silently:
                        raise
                else:
                    # Wait a bit before trying next configuration
                    time.sleep(1)
                    continue
        
        return False
    
    def send_messages(self, email_messages):
        """
        Send messages with additional error handling and retry logic.
        """
        if not email_messages:
            return 0
        
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                # Ensure we have a fresh connection
                if hasattr(self, 'connection') and self.connection:
                    try:
                        self.connection.quit()
                    except:
                        pass
                    self.connection = None
                
                # Open a new connection
                connection_result = self.open()
                logger.info(f"Connection attempt {attempt + 1}: {'Success' if connection_result else 'Failed'}")
                
                if not connection_result:
                    logger.warning(f"Failed to open connection on attempt {attempt + 1}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * (attempt + 1))
                        continue
                    else:
                        logger.error("All connection attempts failed")
                        return 0
                
                # Send the messages
                result = super().send_messages(email_messages)
                logger.info(f"Email send result: {result} messages sent")
                return result
                
            except smtplib.SMTPServerDisconnected as e:
                logger.warning(f"SMTP server disconnected on attempt {attempt + 1}: {e}")
                # Close the connection and retry
                if hasattr(self, 'connection') and self.connection:
                    try:
                        self.connection.quit()
                    except:
                        pass
                    self.connection = None
                
                if attempt < max_retries - 1:  # Don't sleep on the last attempt
                    time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                    continue
                else:
                    # Last attempt failed
                    if not self.fail_silently:
                        raise
                    logger.error(f"All {max_retries} email send attempts failed")
                    return 0
                    
            except (smtplib.SMTPException, OSError, socket.error) as e:
                logger.warning(f"Email sending failed on attempt {attempt + 1}: {e}")
                # Close the connection
                if hasattr(self, 'connection') and self.connection:
                    try:
                        self.connection.quit()
                    except:
                        pass
                    self.connection = None
                
                if attempt < max_retries - 1:  # Don't sleep on the last attempt
                    time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                    continue
                else:
                    # Last attempt failed
                    if not self.fail_silently:
                        raise
                    logger.error(f"All {max_retries} email send attempts failed")
                    return 0
                    
            except Exception as e:
                logger.error(f"Unexpected error during email sending: {e}")
                if not self.fail_silently:
                    raise
                return 0
        
        return 0
    
    def close(self):
        """
        Safely close the connection.
        """
        if hasattr(self, 'connection') and self.connection:
            try:
                self.connection.quit()
            except Exception as e:
                logger.warning(f"Error closing SMTP connection: {e}")
            finally:
                self.connection = None
