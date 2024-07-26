import smtplib
import ssl
from django.core.mail.backends.smtp import EmailBackend
import certifi

class CustomSMTPBackend(EmailBackend):
    def open(self):
        try:
            self.connection = smtplib.SMTP(self.host, self.port)
            # Create SSL context with certificate verification
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            self.connection.starttls(context=ssl_context)
            self.connection.login(self.username, self.password)
            return True
        except Exception as e:
            self._close()
            raise e
