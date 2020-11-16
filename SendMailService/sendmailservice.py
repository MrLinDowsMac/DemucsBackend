from nameko.rpc import rpc
from nameko_sendgrid import SendGrid
from sendgrid.helpers.mail import *

class SendMailService:
    name = "sendmailservice"
    
    sendgrid = SendGrid()
    
    @rpc
    def send_email(self, address, subject, body):
        from_email = Email("test@musicseparate.com")
        to_email = Email(address)
        #subject = "Sending with SendGrid is Fun"
        content = Content("text/plain", body)
        message = Mail(from_email, subject, to_email, content)
        #pylint: disable=no-member
        self.sendgrid.client.mail.send.post(message)