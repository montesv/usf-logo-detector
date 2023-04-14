import yagmail

class yag:

    def send_mail(self, email):
        yagmail.register("USF.Logo.Detector@gmail.com","USFTeam$")
        yag = yagmail.SMTP("USF.Logo.Detector@gmail.com")
        yag.send(email, "USF LOGO VIOLATONS", "here's some",
                 attachments=['Attachment1.png', 'Attachment2.png', 'Attachment3.png'])