from email.message import EmailMessage
import os
import email
import poplib
import smtplib

from email.header import decode_header

NTUMAIL_POP3_HOST = os.getenv('NTUMAIL_POP3_HOST')
NTUMAIL_POP3_PORT = int(os.getenv('NTUMAIL_POP3_PORT'))
NTUMAIL_SMTP_HOST = os.getenv('NTUMAIL_SMTP_HOST')
NTUMAIL_SMTP_PORT = int(os.getenv('NTUMAIL_SMTP_PORT'))

# 需要填入 Github Secret 的資料，參考 README.md
NTUMAIL_ADDRESS = os.getenv('NTUMAIL_ADDRESS')
NTUMAIL_PASSWORD = os.getenv('NTUMAIL_PASSWORD')
FORWARDING_ADDRESSES = os.getenv('FORWARDING_ADDRESSES')

NTUMAIL_USER = NTUMAIL_ADDRESS.split('@')[0]

if not all([NTUMAIL_ADDRESS, NTUMAIL_PASSWORD, FORWARDING_ADDRESSES]):
    raise ValueError('Missing required environment variables.')

def main():
    # POP3 SERVER: 從 NTUMAIL 收信
    mailbox = poplib.POP3_SSL(NTUMAIL_POP3_HOST, NTUMAIL_POP3_PORT)
    mailbox.user(NTUMAIL_ADDRESS)
    mailbox.pass_(NTUMAIL_PASSWORD)

    _, uid_list, _ = mailbox.uidl()
    uid_list: list[tuple[str, str]] = [uid.decode().split() for uid in uid_list]

    if not os.path.exists('fwds.txt'):
        with open('fwds.txt', 'w', encoding='utf-8') as f:
            f.writelines(f'{uid}\n' for _, uid in uid_list)
        mailbox.close()    
        return

    file = open('fwds.txt', 'a+', encoding='utf-8')
    file.seek(0)
    processed_email_uids = set(s.strip() for s in file.readlines())
    
    fwd_uid_list = [uid_item for uid_item in uid_list if uid_item[1] not in processed_email_uids]
    if len(fwd_uid_list) == 0:
        mailbox.close()
        return

    sender = smtplib.SMTP_SSL(NTUMAIL_SMTP_HOST, NTUMAIL_SMTP_PORT)
    sender.login(NTUMAIL_USER, NTUMAIL_PASSWORD)

    for index, uid in fwd_uid_list:
        if uid in processed_email_uids:
            continue  # 跳過已處理的郵件
        
        _, lines, _ = mailbox.retr(index)
        raw_message = b'\r\n'.join(lines)
        
        orig_msg = email.message_from_bytes(raw_message)
        orig_subject = orig_msg.get("Subject", "無主旨")
                    
        # 解碼原始標題
        orig_subject, encoding = decode_header(orig_subject)[0]
        if isinstance(orig_subject, bytes):
            orig_subject = orig_subject.decode(encoding or 'utf-8')
        
        orig_msg.replace_header("Subject", f'[NTUMail 轉寄] {orig_subject}')
        orig_msg.replace_header("From", NTUMAIL_ADDRESS)
        orig_msg.replace_header("To", FORWARDING_ADDRESSES)
        
        sender.send_message(orig_msg)
        
        file.write(f'{uid}\n')  # 記錄已處理的郵件 UID
        break

    mailbox.close()
    sender.quit()
    file.flush()
    file.close()

if __name__ == '__main__':
    main()