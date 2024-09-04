import imaplib
import config
import re
import email
from email.policy import default
import chardet
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os


def decode_payload(payload):
    detected_encoding = chardet.detect(payload)['encoding']
    if detected_encoding:
        return payload.decode(detected_encoding)
    else:
        return payload.decode('utf-8', errors='ignore')
    
class EmailReceiver:
    def __init__(self):
        # 连接、登录IMAP服务器
        self.imap = imaplib.IMAP4_SSL(config.IMAP_SERVER)
        self.imap.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
        # 获取所有文件夹
        self.folders = []
        self.getMailFolders()
        self.last_mail_id = None
    
    def getMailFolders(self) -> None:
        """
        获取IMAP邮箱中的所有文件夹。
        通过调用IMAP的list方法来获取邮箱中的所有文件夹列表，
        然后使用正则表达式提取文件夹名称，并将其添加到folders列表中。
        """
        # 调用IMAP的list方法来获取所有文件夹的列表
        status, folders = self.imap.list()
        print(folders)
        # 遍历文件夹列表
        for folder in folders:
            # 使用正则表达式提取文件夹名称
            folder_name = re.search(rb'"/" "(.*?)"', folder).group(1).decode()
            # 将提取的文件夹名称添加到folders列表中
            if 'NoSelect' not in str(folder):
                self.folders.append(folder_name)

    def getEmails(self, folder: str) -> list:
        # 选择文件夹
        self.imap.select(folder)

        # 搜索所有邮件，并获取邮件ID
        status, email_ids_data = self.imap.search(None, 'ALL')
        if status != 'OK':
            print(f"无法获取邮件ID")
            return []
        # 分割邮件ID字符串，转换为列表
        email_ids = email_ids_data[0].split()
        # 初始化存储邮件信息的列表
        mails = []
        # 遍历每个邮件ID，获取相应的邮件信息
        for email_id in email_ids:
            # 获取邮件的基本信息，不包括内容和附件
            status, msg_data = self.imap.fetch(email_id, '(BODY.PEEK[HEADER.FIELDS (FROM TO SUBJECT DATE)])')
            if status != 'OK':
                print(f"获取ID为 {email_id} 的邮件时出错")
                continue

            # msg_data 是一个包含元组的列表，每个元组包含一个邮件部分
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    # 从邮件数据中解析邮件头
                    msg_header = email.message_from_bytes(response_part[1], policy=email.policy.default)
                    
                    # 提取邮件头部的基本信息
                    mail_info = [
                        email_id.decode(),  # 邮件ID
                        msg_header['From'],  # 发件人
                        msg_header['To'],  # 收件人
                        msg_header['Subject'],  # 主题
                        msg_header['Date']  # 日期
                    ]
                    # 添加邮件信息到列表
                    mails.append(mail_info)
        
        # 返回按时间倒序排列的邮件信息列表
        return list(reversed(mails))
    
    def getEmailById(self, folder: str, email_id) -> list:
        """
        从指定的IMAP文件夹中获取所有邮件的信息。

        :param folder: 邮件文件夹名称，用于通过IMAP协议选择特定的邮件夹
        :return: 包含邮件信息的列表，每封邮件的信息是一个列表，包含ID、发件人、收件人、主题、date、HTML、附件
        """
        # 选择IMAP服务器上的特定文件夹
        self.imap.select(folder)

        # 获取特定邮件的完整信息
        status, msg_data = self.imap.fetch(email_id, '(RFC822)')
        raw_email = msg_data[0][1]
        # 从字节字符串创建邮件对象
        msg = email.message_from_bytes(raw_email, policy=default)
        mail = []
        mail.append(email_id)
        mail.append(msg['From'])
        mail.append(msg['To'])
        mail.append(msg['Subject'])
        mail.append(msg['date'])

        text_body = ''
        html_body = ''
        attachments = []

        # 检查邮件是否是多部分消息
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                if content_type == 'text/plain' and 'attachment' not in content_disposition:
                    payload = part.get_payload(decode=True)
                    text_body = decode_payload(payload)
                elif content_type == 'text/html' and 'attachment' not in content_disposition:
                    payload = part.get_payload(decode=True)
                    html_body = decode_payload(payload)
                elif 'attachment' in content_disposition:
                    filename = part.get_filename()
                    payload = part.get_payload(decode=True)
                    attachments.append((filename, payload))
        else:
            # 处理非多部分消息的正文
            content_type = msg.get_content_type()
            payload = msg.get_payload(decode=True)
            if content_type == 'text/plain':
                text_body = decode_payload(payload)
            elif content_type == 'text/html':
                html_body = decode_payload(payload)

        mail.append(text_body+'\n'+str(html_body))
        mail.append(attachments)
    
        return list(mail)



    def deletemail(self, folder, mailid):
        """
        删除指定文件夹中的邮件。

        :param folder: 邮件所在的文件夹名称。
        :param mailid: 要删除的邮件的ID（UID）。
        """
        try:
            # 选择邮件文件夹，并设置为可写模式
            status, _ = self.imap.select(folder, readonly=False)
            if status != 'OK':
                print(f"无法选择文件夹 {folder}")
                return
            
            # Search for the email by ID
            result, data = self.imap.search(None, 'HEADER', 'Message-ID', mailid)
            if result != 'OK':
                print("Failed to search for the email")
                return
            
            # If email is found, mark it for deletion
            for num in data[0].split():
                self.imap.store(num, '+FLAGS', '\\Deleted')
            # 确保邮件被真正删除
            status, _ = self.imap.expunge()
            if status != 'OK':
                print(f"无法真正删除邮件 {mailid}")
                return
            
            print(f"邮件 {mailid} 已从文件夹 {folder} 中删除")
        
        except Exception as e:
            print(f"删除邮件时发生错误: {e}")
        finally:
            # 根据需要关闭连接，频繁打开和关闭连接可能不是最佳实践
            pass


    def inboxLoop(self):
        try:
            # 选择IMAP服务器上的特定文件夹
            self.imap.select("INBOX")
            # 搜索该文件夹中的所有邮件
            status, data = self.imap.search(None, 'ALL')
            email_ids = data[0].split()  # 将字节字符串拆分成单个邮件ID
            if self.last_mail_id != None and email_ids != self.last_mail_id:
                self.last_mail_id = email_ids
                return True
            else:
                self.last_mail_id = email_ids
        except:
            print("无法连接到IMAP服务器")
            
        

    def save_attachments(self, attachments, save_path):
        """
        保存附件到指定路径。

        :param attachments: 包含附件元组的列表，每个元组包含文件名和文件内容。
        :param save_path: 附件保存路径。
        """
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        for filename, content in attachments:
            filepath = os.path.join(save_path, filename)
            with open(filepath, 'wb') as f:
                f.write(content)

        
    def getFolders(self):
        return self.folders
    
    




class EmailSender:
    def __init__(self):
        # 连接到SMTP服务器
        self.smtp_server = smtplib.SMTP_SSL(config.SMTP_SERVER, config.SMTP_PORT)
        self.smtp_server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)

    def send_email(self, to_address, subject, body, is_html=False, attachments=None):
        """
        发送电子邮件。

        :param to_address: 收件人邮箱地址
        :param subject: 邮件主题
        :param body: 邮件正文内容
        :param is_html: 是否为HTML格式邮件，默认为False
        :param attachments: 附件文件路径列表，默认为None

        """
        # 创建邮件对象
        msg = MIMEMultipart()
        msg['From'] = config.EMAIL_ADDRESS
        msg['To'] = to_address
        msg['Subject'] = subject

        # 根据是否为HTML格式设置邮件正文
        if is_html:
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))

        if attachments:
            for attachment_path in attachments:
                if os.path.exists(attachment_path):
                    with open(attachment_path, 'rb') as f:
                        part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
                    part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
                    msg.attach(part)
                else:
                    print(f"附件文件不存在: {attachment_path}")

        # 发送邮件
        try:
            self.smtp_server.send_message(msg)
            print("邮件发送成功")
            return True
        except Exception as e:
            print(f"邮件发送失败: {e}")
            return False
        finally:
            # 关闭SMTP连接
            self.smtp_server.quit()



if __name__ == "__main__":
    receiver = EmailReceiver()
    receiver.getMailFolders()
    print(receiver.folders)
    print(receiver.getEmails('"INBOX"'))
    print(receiver.getEmailById('"INBOX"', '1'))
    print()
