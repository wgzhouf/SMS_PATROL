#!/bin/python3
from ZFmail import ZFmail
import re
from email.header import decode_header
from datetime import datetime


def guess_charset(msg):
    charset = msg.get_charset()
    if charset is None:
        content_type = msg.get('Content-Type', '').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos + 8:].strip()
    return charset


def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value


def read_email(msg, mail_title=''):
    for header in ['Date', 'Subject']:
        value = msg.get(header, '')
        if value:
            if header == 'Subject':
                value = decode_str(value)
                if value != mail_title:
                    return 0
            elif header == 'Date':
                value = decode_str(value)
                current_time = datetime.now().strftime('%a, %d %b %Y')
                if not value.startswith(current_time):
                    return 0
    if (msg.is_multipart()):
        parts = msg.get_payload()
        for part in parts:
            content_disposition = part.get_content_disposition()
            if (content_disposition.startswith('attachment')):
                content_type = part.get_content_type()
                if content_type == 'text/plain' or content_type == 'text/html':
                    content = part.get_payload(decode=True)
                    charset = guess_charset(part)
                    if charset:
                        # 解析附件内容
                        content = content.decode(charset, 'ignore')
                        return checkBlackWords(content)


def checkBlackWords(content):
    black_words = [r'(.)*集会(.)*',
                   r'(.)*爆(.)*',
                   r'(.)*恐(.)*',
                   r'(.)*袭(.)*']
    criminals = []
    content_lines = content.split('\r\n')
    for line in content_lines:
        for r_black_word in black_words:
            if re.match(r_black_word, line):
                criminals.append(line)
    return criminals


if __name__ == '__main__':
    my_email = 'wgzhouf@189.cn'
    my_password = 'wg8412363'
    pop3_server = 'pop.189.cn'
    smtp_server = 'smtp.189.cn'
    _189_mail = ZFmail(pop3_server, smtp_server, my_email, my_password)
    _189_mail.login()
    last_email_index = _189_mail.get_mailreceivebox_len()

    badsms = '今天没发现异常短信'
    while True:
        msg = _189_mail.get_mail_by_id(last_email_index)
        result = read_email(msg, 'Sms_content')
        if result != 0:
            badsms = '\r\n'.join(result)
            break
        else:
            last_email_index -= 1
    send_status = _189_mail.send_mail('zhoufeng@yixin.im', '每日短信巡检结果', badsms)
    if send_status == 1:
        print('发送成功')
    else:
        print('发送失败')

    _189_mail.logout()
