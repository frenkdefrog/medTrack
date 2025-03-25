"""
Általános célú email küldő modul.
"""
from flask_mail import Message
from app import mail

def send_email(app, recipient, subject, body, sender=None):
    """
    Általános célú email küldő függvény.

    Args:
        app: Flask alkalmazás példány
        recipient (str): Címzett email címe
        subject (str): Email tárgya
        body (str): Email törzse
        sender (tuple|str|None): Feladó. Ha None, akkor az alkalmazás alapértelmezett feladóját használja

    Returns:
        bool: True ha sikeres a küldés, False ha nem
    """
    app.logger.debug(f"Attempting to send email to {recipient}")
    try:
        # Sender beállítása
        if sender is None:
            sender = app.config['MAIL_DEFAULT_SENDER']
            if not sender:
                sender = ("medTrack", app.config['MAIL_USERNAME'])
            elif isinstance(sender, str):
                sender = (sender, app.config['MAIL_USERNAME'])

        # Debug információk
        app.logger.debug(f"Mail settings:")
        app.logger.debug(f"Server: {app.config['MAIL_SERVER']}")
        app.logger.debug(f"Port: {app.config['MAIL_PORT']}")
        app.logger.debug(f"TLS: {app.config['MAIL_USE_TLS']}")
        app.logger.debug(f"Username: {app.config['MAIL_USERNAME']}")

        
        # Message objektum létrehozása
        msg = Message(
            subject=subject,
            sender=sender,
            recipients=[recipient],
            body=body
        )
        app.logger.debug("whataaffaacck2222")
        # Email küldése explicit timeout kezeléssel
        try:
            with mail.connect() as conn:
                app.logger.debug("conn object is created...")
                if hasattr(conn, 'host'):
                    conn.host.timeout = 10
                
                app.logger.debug("Attempting to send email...")
                conn.send(msg)
                app.logger.info(f"Email successfully sent to {recipient}")
                return True

        except Exception as smtp_error:
            app.logger.error(f"SMTP Error: {str(smtp_error)}")
            return False

    except Exception as e:
        app.logger.error(f"Error in send_email: {str(e)}")
        return False
