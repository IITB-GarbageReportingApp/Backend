import smtplib

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('gulshankumar060102@gmail.com', 'edmn govy vjid yvng')
server.sendmail(
    'gulshankumar060102@gmail.com',
    'gulshan.iitb@gmail.com',
    'This is a test email sent via Python!'
)
server.quit()
