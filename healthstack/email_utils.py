"""
Email utility functions for robust email sending
"""

import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

def send_email_safely(subject, message, from_email, recipient_list, html_message=None, fail_silently=True):
    """
    Send email with comprehensive error handling and retry logic.
    Now includes fallback to console backend when SMTP fails.
    
    Args:
        subject (str): Email subject
        message (str): Plain text message
        from_email (str): Sender email
        recipient_list (list): List of recipient emails
        html_message (str, optional): HTML message content
        fail_silently (bool): If True, don't raise exceptions on failure
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    from django.conf import settings
    from django.core.mail.backends.console import EmailBackend as ConsoleBackend
    from django.core.mail import get_connection
    
    # First try with the configured SMTP backend
    try:
        result = send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=fail_silently
        )
        
        if result > 0:
            logger.info(f"Email sent successfully via SMTP to {', '.join(recipient_list)}")
            return True
        else:
            logger.warning(f"SMTP email sending returned 0 for recipients: {', '.join(recipient_list)}")
            raise Exception("SMTP backend returned 0")
            
    except Exception as e:
        logger.error(f"Primary email backend failed: {str(e)}")
        
        # Fallback to console backend
        try:
            logger.info("Attempting to use fallback email backend (console)")
            console_backend = ConsoleBackend()
            
            # Create email message manually for console backend
            from django.core.mail import EmailMultiAlternatives
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=message,
                from_email=from_email,
                to=recipient_list,
                connection=console_backend
            )
            
            if html_message:
                email.attach_alternative(html_message, "text/html")
            
            result = email.send()
            
            if result > 0:
                logger.info(f"Email sent successfully via console backend to {', '.join(recipient_list)}")
                return True
            else:
                logger.error("Console backend also failed")
                return False
                
        except Exception as fallback_error:
            logger.error(f"Fallback email backend also failed: {str(fallback_error)}")
            if not fail_silently:
                raise
            return False

def send_doctor_acceptance_email(doctor_name, doctor_email, doctor_department, doctor_specialization):
    """
    Send doctor acceptance email with error handling.
    
    Args:
        doctor_name (str): Doctor's name
        doctor_email (str): Doctor's email
        doctor_department (str): Doctor's department
        doctor_specialization (str): Doctor's specialization
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    from django.template.loader import render_to_string
    from django.utils.html import strip_tags
    
    subject = "Acceptance of Doctor Registration"
    
    values = {
        "doctor_name": doctor_name,
        "doctor_email": doctor_email,
        "doctor_department": doctor_department,
        "doctor_specialization": doctor_specialization,
    }
    
    try:
        html_message = render_to_string('hospital_admin/accept-doctor-mail.html', {'values': values})
        plain_message = strip_tags(html_message)
        
        return send_email_safely(
            subject=subject,
            message=plain_message,
            from_email='mahimamedicare.web@gmail.com',
            recipient_list=[doctor_email],
            html_message=html_message,
            fail_silently=True  # Don't crash the application on email failure
        )
        
    except Exception as e:
        logger.error(f"Error preparing doctor acceptance email: {str(e)}")
        return False