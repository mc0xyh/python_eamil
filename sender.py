import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QMessageBox, QFileDialog)
from PyQt5.QtWebEngineWidgets import QWebEngineView
import mail
from qts import *
from qframelesswindow import FramelessMainWindow
from qfluentwidgets import PushButton, FluentIcon, BodyLabel, LineEdit, setThemeColor, PrimaryPushButton, MessageBox
import os

class SendWindows(FramelessMainWindow):
    def __init__(self):

        super().__init__()
        self.setWindowTitle("PyQt-Frameless-Window")
        self.titleBar.raise_()

        self.setWindowTitle("")
        self.setGeometry(500, 200, 1800, 1080)

        self.attachments_file_list = []
        self.sender = mail.EmailSender()
        self.bodyhtml = ''
        self.initUI()
        self.attbottoms = {}
    def initUI(self):
        """
        初始化用户界面布局。
        
        设置主窗口的布局结构，包括标题栏、左侧导航栏、中间邮件列表和右侧邮件内容显示区域。
        对各个区域的样式和交互进行定制，确保界面的美观和易用。
        """
        self.setWindowTitle("Frameless Main Window")
        setThemeColor("#0078D4")
        # 创建主布局，设置无边距
        main_layout = QVBoxLayout()

        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加自定义标题栏
        title_bar = CustomTitleBar("Send Email",self)
        main_layout.addWidget(title_bar)
        
        # 创建内容布局，设置无边距
        content_layout = QVBoxLayout()
        main_layout.addLayout(content_layout)

        # 创建导航栏区域
        send_to_widget = QWidget()
        send_to_widget.setContentsMargins(15,0,15,0)
        send_to_layout = QHBoxLayout()
        send_to_widget.setLayout(send_to_layout)

        sento_label = BodyLabel("收件人")
        sento_label.setStyleSheet("font-size: 20px;font-weight: bold;font-family: 'Microsoft YaHei';")
        send_to_layout.addWidget(sento_label, 1)
        self.sendto_lineedit = LineEdit()
        self.sendto_lineedit.setFixedHeight(50)
        self.sendto_lineedit.setStyleSheet("font-size: 20px;")
        self.sendto_lineedit.setPlaceholderText("example@example.com")
        send_to_layout.addWidget(self.sendto_lineedit,18)
        # 设置导航栏区域在主布局中的权重
        content_layout.addWidget(send_to_widget, 1)

        subject_widget = QWidget()
        subject_widget.setContentsMargins(15,0,15,0)
        subject_layout = QHBoxLayout()
        subject_widget.setLayout(subject_layout)

        subject_label = BodyLabel("主题")
        subject_label.setStyleSheet("font-size: 20px;font-weight: bold;font-family: 'Microsoft YaHei';")
        subject_layout.addWidget(subject_label,1)
        self.subject_lineedit = LineEdit()
        self.subject_lineedit.setFixedHeight(50)
        self.subject_lineedit.setStyleSheet("font-size: 20px;")
        self.subject_lineedit.setPlaceholderText("Subject")
        subject_layout.addWidget(self.subject_lineedit,18)
        # 设置导航栏区域在主布局中的权重
        content_layout.addWidget(subject_widget, 1)


        # 创建邮件列表区域
        middle_widget = QWidget()
        middle_layout = QVBoxLayout()
        middle_widget.setLayout(middle_layout)
        
        # 初始化邮件列表，设置样式和点击事件
        self.webview = QWebEngineView()
        self.webview.setHtml(self.get_ckeditor_html())
        middle_layout.addWidget(self.webview)
        

        content_layout.addWidget(middle_widget, 15)
        attachment_widget = QWidget()
        self.attachment_layout = QHBoxLayout()  # 或者继续使用QHBoxLayout，根据您的布局需求

        attachment_widget.setLayout(self.attachment_layout)

        # 设置导航栏区域在主布局中的权重
        content_layout.addWidget(attachment_widget, 1)

        
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout()
        bottom_widget.setLayout(bottom_layout)
        # 添加一个伸缩 spacer 以占据左侧空间

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        bottom_layout.addSpacerItem(spacer)

        def add_attachment():
            """
            打开文件对话框允许用户选择文件，并可以进一步处理所选文件（例如，显示文件路径）。
            """
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(None, "选择附件", "", "All Files (*);;Text Files (*.txt);;Image Files (*.png *.xpm *.jpg);;PDF Files (*.pdf);;Document Files (*.doc *.docx)")
            
            if file_path:  # 检查用户是否选择了文件
                QMessageBox.information(None, "添加附件", f"您选择了以下文件作为附件：\n{file_path}")
                # 在这里可以添加更多处理文件的逻辑，如将文件路径保存至列表或上传文件等
                filename = os.path.basename(file_path)  # 获取文件名
                _, file_extension = os.path.splitext(filename)  # 分离文件名与后缀
                self.attachments_file_list.append(file_path)
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
                self.attbottoms[file_path] = PushButton(f"{filename}", icon=icon)
                self.attachment_layout.addWidget(self.attbottoms[file_path])

            else:
                QMessageBox.information(None, "操作取消", "没有选择任何文件。")


        bottom_addattachment_button = PushButton("添加附件", icon=FluentIcon.ADD)
        bottom_layout.addWidget(bottom_addattachment_button)
        bottom_addattachment_button.clicked.connect(add_attachment)
        bottom_send_button = PrimaryPushButton("发送邮件", icon=FluentIcon.SEND_FILL)
        bottom_send_button.clicked.connect(self.get_editor_content)
        bottom_layout.addWidget(bottom_send_button)



        # 设置导航栏区域在主布局中的权重
        content_layout.addWidget(bottom_widget, 1)



        # 设置主布局到主窗口的中心区域
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def get_ckeditor_html(self):
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <script src="https://cdn.ckeditor.com/ckeditor5/35.3.0/classic/ckeditor.js"></script>
        </head>
        <body>
            <div id="editor"></div>
            <script>
                let editor;
                ClassicEditor
                    .create(document.querySelector('#editor'))
                    .then(ed => {
                        editor = ed;
                    })
                    .catch(error => {
                        console.error(error);
                    });
            </script>
        </body>
        </html>
        '''

    def get_editor_content(self):
        script = '''
        (function() {
            return editor.getData();
        })();
        '''
        self.webview.page().runJavaScript(script, self.send_email)

    
    def send_email(self, html):
        """
        发送邮件的逻辑处理。
        """
        # 获取收件人、主题、正文
        recipient = self.sendto_lineedit.text()
        subject = self.subject_lineedit.text()
        body = html

        if self.sender.send_email(recipient, subject, body, True, self.attachments_file_list):
            w = MessageBox("发送成功", "邮件发送成功！", self)
            w.cancelButton.hide()
            if w.exec():
                self.window().close()
        else:
            w = MessageBox("发送失败", "邮件发送失败。", self)
            w.cancelButton.hide()
            if w.exec():
                self.window().close()
            

        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    email_client = SendWindows()
    email_client.show()
    sys.exit(app.exec_())
