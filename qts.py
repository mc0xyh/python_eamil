from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout, QListWidgetItem, QStyledItemDelegate, QStyle, QPushButton, QLabel, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QFont, QColor, QPainter, QTextDocument
import random


# 定义一个自定义列表项类，继承自QListWidgetItem
class CustomListWidgetItem(QListWidgetItem):
    def __init__(self, subject, sender, date, id):
        # 调用父类构造函数
        super().__init__()
        # 存储邮件主题
        self.subject = subject
        # 存储发件人信息
        self.sender = sender
        # 存储日期信息
        self.date = date

        self.id = id
        # 在UserRole角色下存储当前对象，便于后续获取自定义数据
        self.setData(Qt.UserRole, self)

# 自定义项委托类，用于控制列表项的绘制与大小提示
class CustomItemDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        # 调用父类构造函数并指定父组件
        super().__init__(parent)
        # 设置文本与图像间的间距
        self.text_margin = 10  
        # 使用应用程序的默认字体
        self.font = QApplication.font()
        self.colors = {}

    def paint(self, painter, option, index):

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)

        item = index.data(Qt.UserRole)
        if not item:
            return

        subject = item.subject
        sender = item.sender
        date = item.date

        if self.colors.get(item.date, None) is None:
            self.colors[item.date] = QColor(random.choice(['#c6b1de','#9ad29a','#eeacb2','#ddc3b0','#bcc3c7', '#e0cea2', '#d2ccf8', '#f7c0e3']))

        rect = option.rect
        circle_diameter = 40  # 圆形直径
        circle_radius = circle_diameter / 2
        circle_pos_x = rect.left() + circle_radius  # 圆形左边缘位置

        if option.state & QStyle.State_Selected:
            painter.fillRect(rect, QColor("#cfe4fa"))

        # 绘制圆形
        painter.setPen(Qt.NoPen)  # 不绘制边框
        painter.setBrush(self.colors[item.date])  # 设置填充颜色为蓝色
        painter.drawEllipse(QRectF(circle_pos_x - circle_radius +10,
                                        rect.top() + circle_radius + 10,
                                        circle_diameter, circle_diameter))
        text_rect = QRectF(circle_pos_x - circle_radius+ 10.5, 
                          rect.top() + circle_radius + 8,  # 文字的垂直位置应根据你的布局调整
                          circle_diameter, circle_diameter)
        painter.setFont(QFont("微软雅黑", 14, QFont.Bold))  # 设置字体和大小
        painter.setPen(Qt.white)  # 设置文字颜色
        painter.drawText(text_rect, Qt.AlignCenter, sender[0].upper() if sender != '' else " ")  # 居中绘制文字

        # 准备富文本字符串，这里省略了html_text的具体定义，假设它与原代码相同
        # 准备富文本字符串
        html_text = f"""
        <!DOCTYPE html>
        <html>
        <body>
            <p class="message">
                <span style="font-family: '微软雅黑'; white-space: pre-wrap;font-size: 9pt;">{sender}</span><br/>
                <span style="font-family: '微软雅黑', sans-serif; font-size: 12pt; font-weight: bold;">{subject}</span><br/>
                <span style="color: grey;font-family: '微软雅黑', sans-serif; font-size: 8pt; font-weight: light;">{date}</span><br/>
                
            </p>
        </body>
        </html>
        """
        # 调整文本绘制起始位置以避免与圆形重叠
        text_offset_x = circle_pos_x + circle_diameter   # 文本开始绘制的X坐标，留出一定间距
        painter.translate(text_offset_x, rect.topLeft().y()+10)  # 只在X轴上平移

        document = QTextDocument()
        document.setDefaultFont(self.font)
        document.setHtml(html_text)
        document.drawContents(painter)

        painter.restore()
    def sizeHint(self, option, index):
        # 调用父类方法获取默认大小提示
        size = super().sizeHint(option, index)
        # 设置固定高度（考虑了图标尺寸和额外空间），可根据需要调整
        size.setHeight(100)  
        return size

class CustomTitleBar(QWidget):
    def __init__(self, title, parent=None):
        self.title = title
        super().__init__(parent)
        self.initUI()
        

    def initUI(self):
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor("#0f6cbd")) 
        self.setPalette(palette)

        layout = QHBoxLayout()
        self.setLayout(layout)

        title = QLabel("   "+self.title)
        title.setFont(QFont("微软雅黑", 12, QFont.Bold))
        title.setStyleSheet("color: white;")
        
        layout.addWidget(title)
        layout.addStretch()

        minimize_button = QPushButton("—")
        minimize_button.setFixedSize(30, 30)
        minimize_button.clicked.connect(self.minimize)
        minimize_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-family: "微软雅黑";
                font-size: 16px;
            }
            QPushButton:pressed {
                background-color: lightgray; /* 或者使用具体的灰色代码，例如 #abcdef */
            }
        """)
        layout.addWidget(minimize_button)

        maximize_button = QPushButton("□")
        maximize_button.setFixedSize(30, 30)
        maximize_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-family: "微软雅黑";
                font-size: 22px;
            }
            QPushButton:pressed {
                background-color: lightgray; /* 或者使用具体的灰色代码，例如 #abcdef */
            }
        """)
        maximize_button.clicked.connect(self.maximize)
        layout.addWidget(maximize_button)

        close_button = QPushButton("✕")
        close_button.setFixedSize(30, 30)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-family: "微软雅黑";
                font-size: 16px;
            }
            QPushButton:pressed {
                background-color: lightgray; /* 或者使用具体的灰色代码，例如 #abcdef */
            }
        """)
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

    def minimize(self):
        self.window().showMinimized()

    def maximize(self):
        if self.window().isMaximized():
            self.window().showNormal()
        else:
            self.window().showMaximized()

    def close(self):
        self.window().close()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos() - self.window().frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.window().move(event.globalPos() - self.dragPos)
            event.accept()
    
    def shadow_effect(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)
    
    