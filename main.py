import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QGraphicsDropShadowEffect, QPushButton, QSpacerItem, QSizePolicy, QFrame)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QColor
import mail
from qts import *
from qframelesswindow import FramelessMainWindow
from sender import *
from qfluentwidgets import PushButton, FluentIcon, Dialog, InfoBar,InfoBarPosition
import threading
import time
import win11toast
from functools import partial

class EmailClient(FramelessMainWindow):
    def __init__(self):

        super().__init__()
        self.setWindowTitle("PyQt-Frameless-Window")
        self.titleBar.raise_()
        # Imap相关
        self.receiver = mail.EmailReceiver()
        self.folders = self.receiver.getFolders()

        self.setWindowTitle("")
        self.setGeometry(500, 200, 1800, 1080)
        self.currentdisplay_mails=[]
        self.currentdisplay_folder=''
        self.currentdisplay_mailid = ''
        setThemeColor("#0078D4")


        self.initUI()
    def initUI(self):
        """
        初始化用户界面布局。
        
        设置主窗口的布局结构，包括标题栏、左侧导航栏、中间邮件列表和右侧邮件内容显示区域。
        对各个区域的样式和交互进行定制，确保界面的美观和易用。
        """
        self.setWindowTitle("Frameless Main Window")

        # 创建主布局，设置无边距
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加自定义标题栏
        title_bar = CustomTitleBar( "Python Email Cilent",self)
        main_layout.addWidget(title_bar)
        
        # 创建内容布局，设置无边距
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(content_layout)

        # 创建导航栏区域
        nav_widget = QWidget()
        nav_layout = QVBoxLayout()
        nav_layout.setContentsMargins(5, 20, 0, 0)
        nav_widget.setLayout(nav_layout)

         # 初始化文件夹列表，设置样式和点击事件
        self.folder_list = QListWidget()
        self.folder_list.itemClicked.connect(self.folder_clicked)
        # 设置列表项的样式，包括字体、颜色、背景等
        self.folder_list.setStyleSheet("""
            QListWidget {
                font-size: 18px;
                font-family: "微软雅黑";
                font-weight: light;
                border: none;
                padding-left: 10px;
                background-color: #f0f0f0;       
            }

            QListWidget::item {
                height: 45px;
                font-weight: bold;
                padding-left: 10px;
                margin-top: 5px;
                margin-bottom: 5px;
            }
                                       
            QListWidget:item:selected {
                background-color: #cfe4fa;
                font-family: "微软雅黑";
                color: black;
                font-weight: Bold;
                border-radius: 8px;
            }

            QListWidget:focus {
                outline: none;
                border-radius: 8px;
            }
        """)

        # 遍历文件夹列表，添加每个文件夹项
        for folder in self.folders:
            folder_item = QListWidgetItem(folder)
            folder_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            foldiconlist = {'Sent Messages': 2, 'Drafts' :1, 'Deleted Messages':4, 'Junk' :3, 'INBOX':5}
            folder_item.setIcon(QIcon(f'ui/icons/folder{str(foldiconlist.get(folder, 6))}.png'))
            self.folder_list.addItem(folder_item)
        
        # 设置图标大小和字体
        self.folder_list.setIconSize(QSize(24, 24))
        self.folder_list.setFont(QFont("微软雅黑", weight=QFont.Light))
        
        # 在导航栏添加文件夹列表
        nav_layout.addWidget(self.folder_list)
        
        # 创建并设置发送按钮
        button = QPushButton("发送")
        button.setStyleSheet("""
            QPushButton{
                background-color: #0078D4;
                border-radius: 8px;
                color: white;
                font-size: 16px;
                font-family: "微软雅黑";
                font-weight: bold;
                padding: 10px 20px;
                margin: 10px;
            }
            QPushButton:hover{
                background-color: #005EB8;
            }
        """)
        button.clicked.connect(self.send)
        nav_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        nav_layout.addWidget(button)
        
        # 设置导航栏区域在主布局中的权重
        content_layout.addWidget(nav_widget, 2)


        # 创建邮件列表区域
        middle_widget = QWidget()
        middle_layout = QVBoxLayout()
        middle_widget.setLayout(middle_layout)
        
        # 初始化邮件列表，设置样式和点击事件
        self.email_list = QListWidget()
        self.email_list.itemClicked.connect(self.view_email)
        middle_layout.addWidget(self.email_list)
        self.email_list.setStyleSheet("""QListWidget:item:selected {
                background-color: #cfe4fa;}""")
        # 设置自定义项委托，用于显示带有头像的邮件项
        self.email_list.setItemDelegate(CustomItemDelegate(self))
        
        # 设置阴影效果和样式
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setColor(QColor(0, 0, 0, 25))
        shadow_effect.setBlurRadius(10)
        shadow_effect.setXOffset(2)
        shadow_effect.setYOffset(2)
        self.email_list.setGraphicsEffect(shadow_effect)
        self.email_list.setStyleSheet("""
            QListWidget {
                border: 2px solid transparent;
                background-color: white;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 10px;
            }
            QListWidget::item:selected {
                background-color: #cfe4fa;
                color: black;
            }
        """)
        # 设置邮件列表区域在主布局中的权重
        content_layout.addWidget(middle_widget, 3)

        # 创建邮件内容显示区域
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)
        
        # 创建用于显示操作按钮
        option_layout = QHBoxLayout()
        # 将附件布局添加到邮件内容视图下方
        right_layout.addLayout(option_layout)
        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        option_layout.addSpacerItem(spacer)
        deletebotton = PushButton("删除", icon=FluentIcon.DELETE)
        deletebotton.clicked.connect(self.delete)
        movebotton = PushButton("移动", icon=FluentIcon.MOVE)
        option_layout.addWidget(movebotton)
        option_layout.addWidget(deletebotton)
        

        # 初始化邮件内容视图
        self.email_content = QWebEngineView()
        #self.email_content.setGraphicsEffect(shadow_effect)
        right_layout.addWidget(self.email_content)
        self.email_content.setHtml("""
            <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body, html {
                        height: 100%;
                        margin: 0;
                        display: flex;
                        justify-content: center; /* 水平居中 */
                        align-items: center; /* 垂直居中 */
                        flex-direction: column; /* 让内容按列排列 */
                    }
                </style>
            </head>
            <body>
                <p style="font-family:微软雅黑; font-weight: lighter;">Please choose a folder</p>
                <p style="font-family:微软雅黑; font-weight: lighter;"></pstyle>to display the emails to read :)</p>
            </br>
                <img src="https://res.public.onecdn.static.microsoft/assets/mail/illustrations/noMailSelected/v2/light.svg" alt="邮件图标" width="256px" height="256px">
            </body>
            </html>
                                   """)

        # 设置邮件内容显示区域在主布局中的权重
        content_layout.addWidget(right_widget, 8)

        # 创建用于显示附件的横向布局
        self.attachment_layout = QHBoxLayout()

        # 将附件布局添加到邮件内容视图下方
        right_layout.addLayout(self.attachment_layout)
        

        # 设置主布局到主窗口的中心区域
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # 加载收件箱邮件
        threading.Thread(target=self.checker).start()


    def send(self):
        email_s = SendWindows()
        email_s.show()
    
    def delete(self):
        w = Dialog("删除邮件", "你确定要删除邮件吗？", self)
        w.yesButton.setText("确定")
        w.cancelButton.setText("取消")
        if w.exec():
            ia = InfoBar.success(
                title='成功',
                content="邮件删除成功！",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
            ia.show()
            print('确认')
            self.receiver.deletemail(f'"{self.currentdisplay_folder}"', self.currentdisplay_mailid)
            self.email_list.clear()
            self.currentdisplay_mails=self.receiver.getEmails(f'"{self.currentdisplay_folder}"')
            for mail in self.currentdisplay_mails:
                self.email_list.addItem(CustomListWidgetItem(mail[3], mail[1], mail[4], mail[0]))
        else:
            print('取消')
        

    def folder_clicked(self, item):
        print(f"Clicked folder: {item.text()}")
        self.email_content.setHtml(r'<head><style>body {display: flex;justify-content: center;align-items: center;height: 100vh; margin: 0; }img {max-width: 100%; height: auto; }</style></head><body><img src="https://img.zcool.cn/community/01fa576111f1f111013eaf7020a42b.gif" width="192" height="108"></body>')
        self.currentdisplay_folder = item.text()
        self.email_list.clear()
        self.currentdisplay_mails = self.receiver.getEmails(f'"{item.text()}"')
        for mail in self.currentdisplay_mails:
            self.email_list.addItem(CustomListWidgetItem(mail[3], mail[1], mail[4], mail[0]))
        self.email_content.setHtml('')

    def view_email(self, item):
        item_data = item.data(Qt.UserRole)
        self.currentdisplay_mailid=item_data.id

        self.email_content.setHtml(r'<head><style>body {display: flex;justify-content: center;align-items: center;height: 100vh; margin: 0; }img {max-width: 100%; height: auto; }</style></head><body><img src="https://img.zcool.cn/community/01fa576111f1f111013eaf7020a42b.gif" width="192" height="108"></body>')

        item = self.receiver.getEmailById(f'"{self.currentdisplay_folder}"', self.currentdisplay_mailid)
        self.email_content.setHtml(f'<body style="margin: 5px;padding: 5px;"><h2 style="font-family: 微软雅黑; font-weight: bold;">{item[3]}</h2><p><b>From:</b> {item[1]}</p><p><b>Date:</b> {item[4]}</p><hr></br>{item[5]}</body>')
        self.clear_layout(self.attachment_layout)
        #处理附件
        if item[6]:
            for filename, filecontent in item[6]:
                print(filename)
                _, file_extension = os.path.splitext(filename)  # 分离文件名与后缀
                if file_extension in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".efic", ".svg"]:
                    icon =FluentIcon.PHOTO
                elif file_extension in [".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".pdf"]:
                    icon = FluentIcon.DOCUMENT
                elif file_extension in [".mp4", ".avi", ".mkv", ".flv", ".wmv", ".mov"]:
                    icon = FluentIcon.VIDEO
                elif file_extension in [".mp3", ".wav", ".flac", ".aac", ".ogg"]:
                    icon = FluentIcon.MUSIC
                else:
                    icon = FluentIcon.MAIL
                attbottom = PushButton(f"{filename}", icon=icon)
                attbottom.clicked.connect(partial(self.save_attachments, filename, filecontent))
                self.attachment_layout.addWidget(attbottom, alignment=Qt.AlignLeft)
    


    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    # Recursively clear layouts
                    self.clear_layout(item.layout())

    
    def save_attachments(self, filename, content):
        """
        保存附件到指定路径。

        :param attachments: 包含附件元组的列表，每个元组包含文件名和文件内容。
        :param save_path: 附件保存路径。
        """
        # 获取当前工作目录
        current_dir = os.getcwd()
        # 指定保存附件的子目录
        save_path = os.path.join(current_dir, 'attachments')
        
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        filepath = os.path.join(save_path, filename)
        with open(filepath, 'wb') as f:
            f.write(content)

        os.startfile(filepath, 'open')
    
    def checker(self):
        while True:
            print("循环运行中...")
            time.sleep(15)
            if self.receiver.inboxLoop() == True:
                win11toast.toast("你有一封新邮件", "快点去查看新邮件吧~")
                self.email_list.setCurrentRow(self.folders.index("INBOX"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    email_client = EmailClient()
    email_client.show()
    sys.exit(app.exec_())
