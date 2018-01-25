import poplib
import smtplib
from email.parser import Parser
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr


class ZFmail():
    def __init__(self, pop3_server='', smtp_server='', username='', password=''):
        self.read_mail_server = poplib.POP3(pop3_server)
        self.send_mail_server = smtplib.SMTP(smtp_server, 25)
        self.username = username
        self.password = password

    def login(self):
        # print(self.read_mail_server.welcome().decode('utf-8'))
        self.read_mail_server.user(self.username)
        self.read_mail_server.pass_(self.password)

        self.send_mail_server.login(self.username, self.password)

    def logout(self):
        self.read_mail_server.quit()
        self.send_mail_server.quit()

    def get_mailreceivebox_len(self):
        resp, mails, octets = self.read_mail_server.list()
        lenth = len(mails)
        return lenth

    def get_mail_by_id(self, index=1):
        resp, lines, octets = self.read_mail_server.retr(index)
        msg_content = b'\r\n'.join(lines)
        msg = Parser().parsestr(msg_content.decode('utf-8'))
        return msg

    def send_mail(self, to_addr='', EmailTitle='', content=''):
        target = []
        target.append(to_addr)
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['From'] = ZFmail._format_addr(self.username)
        msg['To'] = ZFmail._format_addr(to_addr)
        msg['Subject'] = Header(EmailTitle, 'utf-8').encode()
        try:
            self.send_mail_server.sendmail(self.username, target, msg.as_string())
        except Exception as e:
            return 0
        return 1

    @staticmethod
    def _format_addr(s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

