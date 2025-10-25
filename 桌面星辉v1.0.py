import sys
import os
import json
import time
import random
import win32gui
import win32con
import shutil
import datetime
from PyQt5.QtCore import (Qt, QTimer, QPropertyAnimation, QPoint,
                          pyqtProperty, QSize, QFileInfo, QPointF, QEasingCurve, QUrl)
from PyQt5.QtGui import (QPixmap, QDragEnterEvent, QDropEvent, QMovie, QPixmapCache,
                         QPainter, QColor, QFont, QBitmap, QIcon)
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton,
    QLabel, QMainWindow, QSystemTrayIcon,
    QMenu, QStyle, QSizePolicy, QDesktopWidget,
    QListWidget, QListWidgetItem, QFileDialog, QGridLayout, QScrollArea, QVBoxLayout,
    QSlider, QTabWidget, QGroupBox, QFormLayout, QComboBox, QLineEdit, QSplitter, QTextBrowser, QFrame,
    QProgressBar, QDialog, QMessageBox, QGraphicsDropShadowEffect, QTextEdit, QCheckBox,
    QDoubleSpinBox, QTableWidget, QHeaderView, QTableWidgetItem
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent


QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
QPixmapCache.setCacheLimit(10240)  # 设置10MB图片缓存

# 星辉是只帅气的公兽！
class VirtualPet(QWidget):
    # 状态常量定义
    STANDING = 0  # 站立状态
    CONFUSED = 1  # 发现任务管理器
    CLICKING = 2  # 正在关闭任务管理器
    HAPPY = 3  # 开心状态
    DRAGGING = 4  # 被拖动状态
    EATING = 5  # 进食状态
    ERROR = 6  # 错误状态
    SITTING = 7  # 坐下休息
    ENTERING_DOMAIN = 9  # 进入星辉邻域状态
    SLEEPING = 8  # 睡眠状态
    PEANUT_CUSHION = 11
    BIRTHDAY_MONTH = 10  # 10月
    BIRTHDAY_DAY = 8  # 8日

    def __init__(self):
        super().__init__()
        ico_path = os.path.join("images", "桌面星辉图标.ico")  # 设置窗口图标
        if os.path.exists(ico_path):
            self.setWindowIcon(QIcon(ico_path))
        self.init_settings()  # 初始化设置
        self.init_ui()  # 初始化界面

        # 检查今天是否是生日
        self.is_birthday = self.check_birthday()
        self.birthday_shown = False  # 标记生日对话是否已显示

        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        # 新增图形质量参数
        self.setAttribute(Qt.WA_OpaquePaintEvent, False)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.init_physics()  # 初始化物理系统
        self.init_animations()  # 初始化动画
        self.init_timers()  # 初始化定时器
        self.dialog_counter = 0  # 对话计数器
        self.domain_path = None  # 星辉邻域路径
        self.domain_dialog_timer = QTimer(self)  # 对话框显示定时器
        self.domain_dialog_timer.timeout.connect(self.hide_domain_dialog)
        self.setAttribute(Qt.WA_DeleteOnClose, False)  # 禁用自动释放
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)  # 强制置顶
        self.desktop_layout = None
        self.init_music()  # 初始化音乐系统
        self.last_wake_time = None  # 最后唤醒时间
        self.is_manual_wake = False  # 是否手动唤醒
        self.peanut_dialog = None  # 花生抱枕对话框
        self.peanut_phase = 0  # 花生抱枕阶段

    def check_birthday(self):
        """检查今天是否是星辉的生日（10月8日）"""
        today = datetime.datetime.now()
        return today.month == self.BIRTHDAY_MONTH and today.day == self.BIRTHDAY_DAY

    def show_birthday_dialog(self):
        """显示生日对话（Windows 11风格） - 修复窗口消失问题并居中显示"""
        # 创建对话框并确保它会一直显示
        self.birthday_dialog = QDialog(self)
        self.birthday_dialog.setWindowTitle("星辉生日快乐！")
        self.birthday_dialog.setWindowIcon(self.windowIcon())
        self.birthday_dialog.setFixedSize(400, 300)
        self.birthday_dialog.setWindowModality(Qt.ApplicationModal)  # 设置为应用模态

        # 应用控制面板同款样式
        self.birthday_dialog.setStyleSheet("""
            QDialog {
                background: white;
                border-radius: 8px;
                font-family: 'Segoe UI Variable';
            }
            QLabel {
                font-size: 14px;
                color: #1A1A1A;
            }
            QPushButton {
                background-color: #0078D4;
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
                min-width: 80px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #106EBE;
            }
            QPushButton:pressed {
                background-color: #005A9E;
            }
            #titleLabel {
                font-size: 18px;
                font-weight: bold;
                color: #DAA520;
            }
            #cakeLabel {
                border-radius: 12px;
                border: 2px solid #FFD700;
                background: #FFFCF0;
            }
        """)

        layout = QVBoxLayout(self.birthday_dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 标题
        title = QLabel("🎂 星辉生日快乐！ 🎂")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 蛋糕图片
        cake_frame = QFrame()
        cake_frame.setObjectName("cakeLabel")
        cake_layout = QVBoxLayout(cake_frame)
        cake_layout.setAlignment(Qt.AlignCenter)

        cake_path = os.path.join("images", "生日蛋糕.png")
        if os.path.exists(cake_path):
            cake_pixmap = QPixmap(cake_path).scaled(120, 120, Qt.KeepAspectRatio)
            cake_label = QLabel()
            cake_label.setPixmap(cake_pixmap)
            cake_layout.addWidget(cake_label)
        else:
            # 回退方案：显示文本蛋糕
            text_cake = QLabel("🎂")
            text_cake.setFont(QFont("Arial", 48))
            text_cake.setAlignment(Qt.AlignCenter)
            cake_layout.addWidget(text_cake)

        layout.addWidget(cake_frame)

        # 消息文本
        message = QLabel("今天是我的生日！你能陪我过吗？")
        message.setAlignment(Qt.AlignCenter)
        message.setWordWrap(True)
        layout.addWidget(message)

        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)

        btn_yes = QPushButton("是")
        btn_yes.setFixedSize(100, 40)
        btn_yes.clicked.connect(lambda: self.handle_birthday_response(True))

        btn_no = QPushButton("否")
        btn_no.setFixedSize(100, 40)
        btn_no.clicked.connect(lambda: self.handle_birthday_response(False))

        btn_layout.addStretch()
        btn_layout.addWidget(btn_yes)
        btn_layout.addWidget(btn_no)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        # ========== 关键修改：居中显示在屏幕上 ==========
        # 获取屏幕中心位置
        screen_geometry = QDesktopWidget().availableGeometry()
        screen_center = screen_geometry.center()

        # 计算窗口左上角位置
        x = screen_center.x() - self.birthday_dialog.width() // 2
        y = screen_center.y() - self.birthday_dialog.height() // 2

        # 移动窗口到屏幕中心
        self.birthday_dialog.move(x, y)

        # 显示对话框并确保它保持打开
        self.birthday_dialog.exec_()

    def handle_birthday_response(self, accepted):
        """处理生日响应"""
        # 关闭对话框
        if hasattr(self, 'birthday_dialog') and self.birthday_dialog:
            self.birthday_dialog.close()
            self.birthday_dialog = None

        if accepted:
            # 创建生日特效
            self.create_birthday_effect()

            # ========== 新增成就解锁 - 直接更新JSON文件 ==========
            # 成就数据文件路径
            config_path = os.path.join(os.getenv('LOCALAPPDATA'), 'StarPet')
            achievement_file = os.path.join(config_path, 'achievements.json')

            # 确保目录存在
            if not os.path.exists(config_path):
                os.makedirs(config_path)

            # 加载现有成就数据
            achievement_data = {}
            if os.path.exists(achievement_file):
                try:
                    with open(achievement_file, 'r') as f:
                        achievement_data = json.load(f)
                except Exception as e:
                    print(f"加载成就数据失败: {str(e)}")

            # 更新"陪星辉过第一个生日"成就
            if "first_birthday" not in achievement_data:
                achievement_data["first_birthday"] = 1

                # 保存更新后的成就数据
                try:
                    with open(achievement_file, 'w') as f:
                        json.dump(achievement_data, f)
                    print("已解锁成就: 陪星辉过第一个生日")
                except Exception as e:
                    print(f"保存成就数据失败: {str(e)}")
            # ===============================================

            # 显示确认对话框
            self.show_birthday_confirmation("太棒了！",
                                            "谢谢你！这是我收到的最好的礼物！\n我们一起吃蛋糕吧！",
                                            self.HAPPY)
        else:
            self.show_birthday_confirmation("失落...",
                                            "好吧，也许明年你会陪我...",
                                            self.SITTING)

    def show_birthday_confirmation(self, title, message, state):
        """显示生日确认对话框 - 修复窗口消失问题并居中显示"""
        # 创建对话框并确保它会一直显示
        confirm_dialog = QDialog(self)
        confirm_dialog.setWindowTitle(title)
        confirm_dialog.setWindowIcon(self.windowIcon())
        confirm_dialog.setFixedSize(350, 200)
        confirm_dialog.setWindowModality(Qt.ApplicationModal)  # 设置为应用模态

        confirm_dialog.setStyleSheet("""
            QDialog {
                background: white;
                border-radius: 8px;
                font-family: 'Segoe UI Variable';
            }
            QLabel {
                font-size: 14px;
                color: #1A1A1A;
            }
            QPushButton {
                background-color: #0078D4;
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
                min-width: 100px;
                font-size: 14px;
            }
            #titleLabel {
                font-size: 16px;
                font-weight: bold;
                color: #DAA520;
            }
        """)

        layout = QVBoxLayout(confirm_dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 标题
        title_label = QLabel(title)
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # 消息
        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

        # 确定按钮
        btn_ok = QPushButton("确定")
        btn_ok.setFixedSize(120, 40)
        btn_ok.clicked.connect(confirm_dialog.accept)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_ok)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        # ========== 关键修改：居中显示在屏幕上 ==========
        # 获取屏幕中心位置
        screen_geometry = QDesktopWidget().availableGeometry()
        screen_center = screen_geometry.center()

        # 计算窗口左上角位置
        x = screen_center.x() - confirm_dialog.width() // 2
        y = screen_center.y() - confirm_dialog.height() // 2

        # 移动窗口到屏幕中心
        confirm_dialog.move(x, y)

        # 改变宠物状态
        self.change_state(state)

        # 显示对话框并确保它保持打开
        confirm_dialog.exec_()

    def create_birthday_effect(self):
        """生日特效（蛋糕和彩带）"""
        try:
            # 蛋糕特效
            cake_label = QLabel(self)
            # 确保有生日蛋糕图片（需要添加到images文件夹）
            cake_path = os.path.join("images", "生日蛋糕.png")
            if os.path.exists(cake_path):
                cake_pixmap = QPixmap(cake_path).scaled(150, 150, Qt.KeepAspectRatio)
                cake_label.setPixmap(cake_pixmap)
                cake_label.move(self.width() // 2 - 75, self.height() // 2 - 50)
                cake_label.show()
            else:
                # 回退方案：显示文本蛋糕
                cake_label.setText("🎂")
                cake_label.setFont(QFont("Arial", 48))
                cake_label.setAlignment(Qt.AlignCenter)
                cake_label.setGeometry(self.width() // 2 - 75, self.height() // 2 - 50, 150, 150)
                cake_label.show()

            # 彩带动画
            confetti_path = os.path.join("images", "彩带.gif")
            if os.path.exists(confetti_path):
                self.confetti_movie = QMovie(confetti_path)
                confetti_label = QLabel(self)
                confetti_label.setMovie(self.confetti_movie)
                self.confetti_movie.start()
                confetti_label.setGeometry(0, 0, self.width(), self.height())
                confetti_label.show()

            # 5秒后移除特效
            QTimer.singleShot(10000, lambda: (
                cake_label.deleteLater(),
                confetti_label.deleteLater() if 'confetti_label' in locals() else None,
                self.confetti_movie.stop() if 'self.confetti_movie' in locals() else None
            ))
        except Exception as e:
            print(f"生日特效创建失败: {str(e)}")
            self.change_state(self.ERROR)

    def init_music(self):
        """完整音乐初始化"""
        self.media_player = QMediaPlayer()

        try:
            # 确保配置目录存在
            if not os.path.exists(ControlPanel.CONFIG_PATH):
                os.makedirs(ControlPanel.CONFIG_PATH)

            # 加载音频配置
            if os.path.exists(ControlPanel.AUDIO_CONFIG):
                with open(ControlPanel.AUDIO_CONFIG, 'r') as f:
                    config = json.load(f)
                    self.play_music(config.get('bgm'))
                    # 加载音量设置
                    self.media_player.setVolume(config.get('volume', 80))
        except Exception as e:
            print(f"音频初始化失败: {str(e)}")
            self.change_state(self.ERROR)

    def play_music(self, name):
        """动态加载audio文件夹中的音乐"""
        try:
            if name == "禁用" or not name:
                self.media_player.stop()
                return

            # 构建完整的文件路径
            file_path = os.path.join("audio", f"{name}.wav")

            # 增加文件存在性检查
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"音乐文件缺失: {file_path}")

            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
            self.media_player.play()
        except Exception as e:
            print(f"音乐播放失败: {str(e)}")
            self.change_state(self.ERROR)

    def init_settings(self):
        """初始化宠物参数配置（核心配置方法）"""
        # ------------------- 基础状态初始化 -------------------
        self.state = self.STANDING  # 初始状态设为站立

        # ------------------- 图像缩放系统 -------------------
        # 默认缩放比例（如果配置文件不存在或读取失败时使用）
        default_scale = 0.10  # 相当于原始尺寸的10%

        try:
            # 尝试读取配置文件（如果文件存在）
            if os.path.exists("config.json"):
                with open("config.json", "r") as f:
                    config = json.load(f)
                    # 使用配置文件中的缩放值，不存在则用默认值
                    self.IMG_SCALE = config.get("scale", default_scale)
            else:
                self.IMG_SCALE = default_scale

        except json.JSONDecodeError:
            print("⚠️ 配置文件格式错误，使用默认设置")
            self.IMG_SCALE = default_scale
        except Exception as e:
            print(f"⚠️ 读取配置失败: {str(e)}")
            self.IMG_SCALE = default_scale

        # ------------------- 尺寸计算系统 -------------------
        # 原始图片尺寸为3543x4488像素（需根据实际图片修改）
        self.BASE_SIZE = QSize(
            int(3543 * self.IMG_SCALE),  # 宽度计算
            int(4488 * self.IMG_SCALE)  # 高度计算
        )

        # ------------------- 物理引擎参数（关键优化）-------------------
        # 使用非线性缩放公式优化物理表现
        scale_factor = self.IMG_SCALE ** 0.7  # 指数缩放系数

        self.PHYSICS = {
            'gravity': 980 * scale_factor,  # 使用标准重力加速度 (9.8m/s²)
            'air_resistance': 0.97,  # 更真实的空气阻力系数
            'bounce': 0.7,  # 更弹性的反弹系数
            'ground_friction': 0.85,  # 更真实的地面摩擦力
            'terminal_velocity': 1500 * scale_factor  # 终端速度限制（最大下落速度）
        }

        # ------------------- 动画系统参数 -------------------
        self.sleep_frames = 8  # 睡觉动画总帧数
        self.sleep_frame_index = 0  # 当前睡觉动画帧
        self.sleep_pause_counter = 0  # 动画暂停计数器

        # ------------------- 星辉邻域路径 -------------------
        try:
            if os.path.exists("config.json"):
                with open("config.json", "r") as f:
                    config = json.load(f)
                    self.domain_path = config.get("domain_path")
            else:
                self.domain_path = None
        except Exception as e:
            print(f"路径读取失败: {str(e)}")
            self.domain_path = None

        # ------------------- 内存优化配置 -------------------
        self.setAttribute(Qt.WA_DeleteOnClose)  # 关闭时自动释放内存

    def init_ui(self):
        """初始化界面元素"""
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAcceptDrops(True)
        self.setFixedSize(self.BASE_SIZE)

        self.pet_label = QLabel(self)
        self.pet_label.setAlignment(Qt.AlignCenter)
        self.update_image("站立")

        # 初始位置：屏幕右下角外
        screen = QDesktopWidget().screenGeometry()
        self.move(screen.width(), screen.height() - self.BASE_SIZE.height())
        current_hour = datetime.datetime.now().hour
        if (current_hour >= 21) or (current_hour < 7):
            self.change_state(self.SLEEPING)

    def init_physics(self):
        """初始化物理系统参数"""
        self.velocity = QPointF(0, 0)  # 移动速度向量
        self.drag_pos = QPoint()  # 拖拽起始位置
        self.is_dragging = False  # 是否正在拖拽
        self.move_history = []  # 移动轨迹记录

    def init_animations(self):
        """初始化入场动画"""
        self.enter_anim = QPropertyAnimation(self, b"pos")
        self.enter_anim.setDuration(3000)  # 3秒动画时长
        screen = QDesktopWidget().screenGeometry()
        # 目标位置：屏幕右下角
        self.enter_anim.setEndValue(QPoint(
            screen.width() - self.BASE_SIZE.width() - 50,
            screen.height() - self.BASE_SIZE.height() - 50
        ))
        self.enter_anim.setEasingCurve(QEasingCurve.OutExpo)  # 缓动曲线
        self.enter_anim.start()  # 启动动画

    def init_timers(self):
        """初始化各种定时器"""
        # 任务管理器检测定时器（每秒检测一次）
        self.tm_timer = QTimer(self)
        self.tm_timer.timeout.connect(self.check_taskmanager)
        self.tm_timer.start(1000)

        # 拖拽动画定时器（4帧/秒）
        self.drag_anim_timer = QTimer(self)
        self.drag_anim_timer.timeout.connect(self.update_drag_animation)
        self.drag_frame = 0  # 当前拖拽动画帧

        # 待机检测定时器（每秒检测一次）
        self.idle_timer = QTimer(self)
        self.idle_timer.timeout.connect(self.check_idle)
        self.idle_timer.start(1000)
        self.last_active_time = time.time()  # 最后活动时间

        # 睡觉动画定时器（15帧/秒）
        self.sleep_anim_timer = QTimer(self)
        self.sleep_anim_timer.timeout.connect(self.update_sleep_animation)

        # 图片缓存清理定时器（每小时清理一次）
        self.cache_timer = QTimer(self)
        self.cache_timer.timeout.connect(self.clear_pixmap_cache)
        self.cache_timer.start(3600000)  # 每小时清理一次

        # 生物钟定时器（每分钟检查一次睡眠时间）
        self.biological_clock_timer = QTimer(self)
        self.biological_clock_timer.timeout.connect(self.check_sleep_schedule)
        self.biological_clock_timer.start(60000)  # 每分钟检查一次

    def check_sleep_schedule(self):
        """生物钟时间检查"""
        current_hour = datetime.datetime.now().hour
        is_sleep_time = (current_hour >= 21) or (current_hour < 7)  # 正确判断条件

        if self.is_manual_wake:
            if (datetime.datetime.now() - self.last_wake_time).seconds < 7200:
                return

        if is_sleep_time and self.state != self.SLEEPING:
            self.change_state(self.SLEEPING)
        elif not is_sleep_time and self.state == self.SLEEPING:
            self.change_state(self.STANDING)

    def clear_pixmap_cache(self):
        QPixmapCache.clear()
        self.pet_label.clear()

    def closeEvent(self, event):
        # 强制终止所有动画
        if self.enter_anim.state() == QPropertyAnimation.Running:
            self.enter_anim.stop()

        # 彻底断开信号槽
        self.tm_timer.timeout.disconnect()
        self.drag_anim_timer.timeout.disconnect()
        self.idle_timer.timeout.disconnect()
        self.sleep_anim_timer.timeout.disconnect()

        # 级联删除子对象
        self.pet_label.deleteLater()
        if hasattr(self, 'domain_window'):
            self.domain_window.deleteLater()

        super().closeEvent(event)

    def update_image(self, base_name=None):
        """升级版图像更新方法，支持睡眠动画"""
        try:
            # 状态优先判断：睡眠状态使用动画帧
            if self.state == self.SLEEPING:
                frame_num = self.sleep_frame_index + 1
                path = os.path.join("images", f"睡觉{frame_num}.png")
                anim_base = "睡觉"  # 动画基础名称
            else:
                # 原有逻辑：根据状态获取基础图片名
                if base_name is None:
                    state_map = {
                        self.STANDING: "站立",
                        self.CONFUSED: "疑惑",
                        self.CLICKING: "点击",
                        self.HAPPY: "开心",
                        self.DRAGGING: f"被拖动{self.drag_frame + 1}",
                        self.EATING: "进食",
                        self.ERROR: "错误",
                        self.SITTING: "坐下",
                        self.ENTERING_DOMAIN: "传送"
                    }
                    base_name = state_map.get(self.state, "站立")

                path = os.path.join("images", f"{base_name}.png")
                anim_base = base_name

            # 通用加载逻辑
            if not os.path.exists(path):
                raise FileNotFoundError(f"图片缺失: {os.path.basename(path)}")

            original_pixmap = QPixmap(path)
            original_size = original_pixmap.size()

            # 动态缩放计算（保持宽高比）
            scaled_width = int(original_size.width() * self.IMG_SCALE)
            scaled_height = int(original_size.height() * self.IMG_SCALE)
            scaled_size = QSize(scaled_width, scaled_height)

            # 高质量缩放
            pixmap = original_pixmap.scaled(
                scaled_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            # 更新显示
            self.setFixedSize(pixmap.size())
            self.pet_label.setFixedSize(pixmap.size())
            self.pet_label.setPixmap(pixmap)

            # 物理参数同步（仅非睡眠状态）
            if self.state != self.SLEEPING:
                self.BASE_SIZE = pixmap.size()
                scale_factor = self.IMG_SCALE ** 0.7
                self.PHYSICS['gravity'] = 1800 * scale_factor * 6

        except Exception as e:
            print(f"⚠️ 图像加载失败: {str(e)}")
            self._show_fallback_icon()

    # ------------------- 任务管理器相关 -------------------
    def check_taskmanager(self):
        """检测任务管理器窗口"""
        # 通过窗口类名查找更可靠
        hwnd = win32gui.FindWindow("TaskManagerWindow", None)
        if hwnd:
            if self.state != self.CLICKING:
                self.change_state(self.CONFUSED)
                QTimer.singleShot(1000, self.close_taskmanager)
        else:
            if self.state == self.CONFUSED:
                self.change_state(self.HAPPY)
                QTimer.singleShot(2000, lambda: self.change_state(self.STANDING))

    def close_taskmanager(self):
        """关闭任务管理器"""
        hwnd = win32gui.FindWindow("TaskManagerWindow", None)
        if hwnd:
            # 发送ALT+F4组合键（更可靠的关闭方式）
            win32gui.PostMessage(hwnd, win32con.WM_SYSCOMMAND, win32con.SC_CLOSE, 0)
            self.change_state(self.CLICKING)
            QTimer.singleShot(800, lambda: self.change_state(self.HAPPY))

    # ------------------- 状态管理系统 -------------------
    def change_state(self, new_state):
        """切换宠物状态"""
        if self.state == new_state:
            return

        if new_state == self.SLEEPING:
            if not hasattr(self, "sleep_anim_timer"):
                self.init_timers()  # 强制初始化（备用方案）
            self.sleep_anim_timer.start(66)  # 启动睡觉动画

            # 当进入睡眠状态时停止物理引擎
        if new_state == self.SLEEPING:
            if hasattr(self, "physics_timer") and self.physics_timer.isActive():
                self.physics_timer.stop()

        if self.state == new_state:
            return

        self.state = new_state
        self.last_active_time = time.time()  # 重置活动时间

        # 根据状态切换显示
        if self.state == self.STANDING:
            self.update_image("站立")
        elif self.state == self.CONFUSED:
            self.update_image("疑惑")
        elif self.state == self.CLICKING:
            self.update_image("点击")
        elif self.state == self.HAPPY:
            self.update_image("开心")
        elif self.state == self.DRAGGING:
            self.drag_anim_timer.start(250)  # 启动拖拽动画（250ms间隔）
        elif self.state == self.EATING:
            self.update_image("进食")
            QTimer.singleShot(3000, lambda: self.change_state(self.STANDING))
        elif self.state == self.ERROR:
            self.update_image("错误")
            QTimer.singleShot(2000, lambda: self.change_state(self.STANDING))
        elif self.state == self.SITTING:
            self.update_image("坐下")
        elif self.state == self.SLEEPING:
            self.sleep_anim_timer.start(66)  # 启动睡觉动画（约15帧/秒）
            self.sleep_frame_index = 0
            self.sleep_pause_counter = 0
        elif new_state == self.SLEEPING:
            self.sleep_anim_timer.start(66)  # 启动动画
            self.sleep_frame_index = 0
            self.sleep_pause_counter = 0
            self.update_image()  # 初始化第一帧
        elif new_state == self.PEANUT_CUSHION:
            # 更新为花生抱枕图片
            self.update_image("花生抱枕")

            # 重置阶段
            self.peanut_phase = 0

            # 停止其他动画定时器
            self.drag_anim_timer.stop()
            if hasattr(self, "sleep_anim_timer"):
                self.sleep_anim_timer.stop()

            # 重置活动时间（防止进入待机状态）
            self.last_active_time = time.time()

    # ------------------- 动画系统 -------------------
    def update_drag_animation(self):
        """更新拖拽动画（两帧循环）"""
        self.drag_frame = 1 - self.drag_frame
        self.update_image(f"被拖动{self.drag_frame + 1}")

    def update_sleep_animation(self):
        """更新睡觉动画"""
        if self.state != self.SLEEPING:  # 新增状态检查
            self.sleep_anim_timer.stop()
            return

        if self.sleep_pause_counter > 0:
            self.sleep_pause_counter -= 1
            return

        if self.sleep_frame_index < self.sleep_frames - 1:
            self.sleep_frame_index += 1
            self.update_image(f"睡觉{self.sleep_frame_index + 1}")
        else:
            self.sleep_pause_counter = 3  # 最后一帧暂停3次刷新
            self.sleep_frame_index = 0

    # ------------------- 交互系统 -------------------
    def mousePressEvent(self, event):
        if self.state == self.SLEEPING:  # 睡眠状态点击唤醒
            self.is_manual_wake = True
            self.last_wake_time = datetime.datetime.now()
            self.change_state(self.STANDING)
            QTimer.singleShot(7200000, lambda: setattr(self, 'is_manual_wake', False))  # 2小时后重置
            return

        if self.is_birthday and not self.birthday_shown:
            self.birthday_shown = True
            self.show_birthday_dialog()
            return

        if event.button() == Qt.RightButton:
            menu = QMenu(self)
            # ========== 新增Win11菜单样式 ==========
            menu.setStyleSheet("""
                QMenu {
                    background: white;
                    border: 1px solid #E0E0E0;
                    border-radius: 8px;
                    padding: 8px;
                    margin: 4px;
                }
                QMenu::item {
                    padding: 8px 32px 8px 16px;
                    border-radius: 4px;
                    margin: 2px;
                    color: #1A1A1A;
                }
                QMenu::item:selected {
                    background: rgba(0, 120, 212, 0.1);
                }
                QMenu::icon {
                    left: 8px;
                }
            """)
            # ========== 原有菜单项 ==========
            create_action = menu.addAction("📝 创建对话文件")
            create_action.triggered.connect(self.create_dialog_file)
            domain_action = menu.addAction("✨ 进入星辉邻域")
            domain_action.triggered.connect(self.enter_domain)
            control_panel_action = menu.addAction("⚙️ 控制面板")
            control_panel_action.triggered.connect(self.show_control_panel)
            menu.exec_(event.globalPos())
        else:  # 左键拖拽
            self.is_dragging = True
            # 记录拖拽起始位置（全局坐标 - 窗口坐标 = 偏移量）
            self.drag_pos = event.globalPos() - self.pos()
            # 初始化移动轨迹记录（用于计算速度）
            self.move_history = [(time.time(), event.globalPos())]
            # 切换为拖拽状态
            self.change_state(self.DRAGGING)
            # 重置活动时间（防止进入待机状态）
            self.last_active_time = time.time()

            # 关键修复：停止物理引擎（避免拖拽时与手动移动冲突）
            if hasattr(self, "physics_timer") and self.physics_timer.isActive():
                self.physics_timer.stop()

    def show_control_panel(self):
        """显示控制面板（带异常处理）"""
        try:
            # 关闭已存在的控制面板
            if hasattr(self, 'control_panel') and self.control_panel:
                self.control_panel.deleteLater()

            self.control_panel = ControlPanel(self)
            self.control_panel.show()
        except Exception as e:
            print(f"控制面板打开失败: {str(e)}")
            self.change_state(self.ERROR)

    def mouseMoveEvent(self, event):
        """鼠标移动事件（拖拽中持续触发）"""
        if self.is_dragging:
            # 计算新位置：当前全局坐标 - 拖拽偏移量
            new_pos = event.globalPos() - self.drag_pos
            # 添加移动阈值（小于2像素不更新，减少抖动）
            delta = new_pos - self.pos()
            if abs(delta.x()) < 2 and abs(delta.y()) < 2:
                return
            # 移动窗口到新位置
            self.move(new_pos)

            # 记录移动轨迹（最多保留10个点）
            self.move_history.append((time.time(), event.globalPos()))
            if len(self.move_history) > 10:
                self.move_history.pop(0)  # 移除最早的点

    def mouseReleaseEvent(self, event):
        """鼠标释放事件（结束拖拽）"""
        self.is_dragging = False
        # 停止拖拽动画
        self.drag_anim_timer.stop()
        # 恢复站立状态
        self.change_state(self.STANDING)
        # 更新活动时间
        self.last_active_time = time.time()

        if hasattr(self, "physics_timer") and self.physics_timer.isActive():
            self.physics_timer.stop()

        # 仅当有足够轨迹点时计算速度
        if len(self.move_history) >= 2:
            total_weight = 0
            weighted_vx = 0
            weighted_vy = 0

            # 取最后5个点计算加权平均速度（越新的点权重越高）
            for i in range(1, min(5, len(self.move_history))):
                # 获取相邻两个点的时间和坐标
                t_prev, pos_prev = self.move_history[-i - 1]
                t_curr, pos_curr = self.move_history[-i]
                delta_t = t_curr - t_prev

                if delta_t <= 0:
                    continue  # 避免除以零或负时间

                # 计算瞬时速度
                vx = (pos_curr.x() - pos_prev.x()) / delta_t
                vy = (pos_curr.y() - pos_prev.y()) / delta_t

                # 权重系数：越新的点权重越高（i=1时权重0.2，i=4时权重0.8）
                weight = i * 0.2
                weighted_vx += vx * weight
                weighted_vy += vy * weight
                total_weight += weight

            if total_weight > 0:
                # 计算加权平均速度并放大1.5倍（增强拖动效果）
                self.velocity = QPointF(
                    weighted_vx / total_weight * 1.5,
                    weighted_vy / total_weight * 1.5
                )

            # 启动物理引擎定时器（16ms≈60帧）
            self.physics_timer = QTimer(self)
            self.physics_timer.timeout.connect(self.update_physics)
            self.physics_timer.start(16)

    def update_physics(self):
        """物理引擎更新（增加数值安全性和边界检查）"""
        try:
            # 确保速度在合理范围内（防止溢出）
            self.velocity.setX(max(min(self.velocity.x(), 5000), -5000))
            self.velocity.setY(max(min(self.velocity.y(), 5000), -5000))

            # 计算速度模长（避免除零错误）
            speed = (self.velocity.x() ** 2 + self.velocity.y() ** 2) ** 0.5
            if speed == 0:
                speed = 0.001  # 防止除零

            # 动态空气阻力（确保最小值）
            air_resistance = max(
                self.PHYSICS['air_resistance'] - (speed / 5000) * 0.1,
                0.5  # 阻力最低限制
            )
            self.velocity *= air_resistance

            # 应用重力（添加随机扰动）
            gravity = self.PHYSICS['gravity'] * 0.016 * random.uniform(0.9, 1.1)
            self.velocity.setY(self.velocity.y() + gravity)

            # 计算新位置并处理屏幕边界
            screen = QDesktopWidget().screenGeometry()
            max_x = max(screen.width() - self.width(), 1)  # 防止负数
            max_y = max(screen.height() - self.height(), 1)
            new_pos = self.pos() + self.velocity.toPoint() * 0.016

            # X轴碰撞检测
            if new_pos.x() < 0:
                new_pos.setX(0)
                self.velocity.setX(-self.velocity.x() * self.PHYSICS['bounce'])
            elif new_pos.x() > max_x:
                new_pos.setX(max_x)
                self.velocity.setX(-self.velocity.x() * self.PHYSICS['bounce'])

            # Y轴碰撞检测
            if new_pos.y() < 0:
                new_pos.setY(0)
                self.velocity.setY(-self.velocity.y() * self.PHYSICS['bounce'])
            elif new_pos.y() > max_y:
                new_pos.setY(max_y)
                self.velocity.setY(-self.velocity.y() * self.PHYSICS['bounce'])
                self.velocity.setX(self.velocity.x() * self.PHYSICS['ground_friction'])

            # 应用最终位置
            self.move(new_pos)

            # 停止条件（速度低于阈值）
            if self.velocity.manhattanLength() < 5:
                self.physics_timer.stop()
                self.velocity = QPointF(0, 0)
                if self.state == self.STANDING and new_pos.y() >= max_y - 10:
                    self.change_state(self.SITTING)

        except Exception as e:
            print(f"物理引擎异常: {str(e)}")
            if hasattr(self, "physics_timer"):
                self.physics_timer.stop()
            self.velocity = QPointF(0, 0)

    # ------------------- 文件交互系统 -------------------
    def create_dialog_file(self):
        """创建对话文件"""
        # 新增检查：如果控制面板未初始化
        if not hasattr(self, 'control_panel') or self.control_panel is None:
            self.show_domain_dialog("请先打开控制面板看看吧")
            return

        current_count = self.control_panel.achievement_data.get("writer", 0)
        if current_count < 5:
            self.control_panel.achievement_data["writer"] = current_count + 1
            self.control_panel.save_achievements()
        self.dialog_counter += 1
        dialogs = [
            "今天的天气真好呢～(≧ω≦)",
            "工作太久啦，起来活动一下吧！",
            f"这是我们第{self.dialog_counter}次对话哦～",
            "秘密口令：双击有惊喜！",
            "系统状态：健康 (๑•̀ㅂ•́)و✧",
            "要记得经常保存工作进度呀！"
        ]
        content = random.choice(dialogs)

        # 在桌面生成文件
        desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        timestamp = time.strftime("%Y%m%d%H%M%S")
        file_path = os.path.join(desktop, f"星辉留言_{timestamp}.txt")

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"{content}\n\n—— {time.strftime('%Y-%m-%d %H:%M')}")

        self.change_state(self.HAPPY)
        QTimer.singleShot(2000, lambda: self.change_state(self.STANDING))
        self.control_panel.update_achievements()  # 每次创建文件时更新

    def dragEnterEvent(self, event):
        """拖放进入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def safe_remove(self, path):
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            print(f"文件删除失败: {str(e)}")

    def dropEvent(self, event):
        try:
            if not event.mimeData().hasUrls():
                return

            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if not path:  # 新增空路径检查
                    continue

                if path.lower().endswith(".txt"):
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if "秘密口令" in content:
                                self.jump_animation()
                            elif "状态" in content:
                                self.show_status_tooltip()
                    except Exception as e:
                        print(f"文件读取失败: {e}")
                    finally:
                        self.change_state(self.EATING)
                        QTimer.singleShot(3000, lambda p=path: self.safe_remove(p))
                else:
                    self.change_state(self.ERROR)

            event.acceptProposedAction()
        except Exception as e:
            print(f"拖放处理异常: {e}")
            self.change_state(self.ERROR)

    def mouseDoubleClickEvent(self, event):
        """处理宠物本体双击事件"""
        if event.button() == Qt.LeftButton:
            self.jump_animation()
            self.create_special_effect()  # 添加额外特效

    def create_special_effect(self):
        """双击惊喜特效"""
        # 检查资源文件是否存在
        star_path = os.path.join("images", "stars.gif")
        if not os.path.exists(star_path):
            # 回退方案：显示文字动画
            self.show_fallback_animation()
            return

        try:
            # 创建星星粒子特效
            self.star_label = QLabel(self)
            movie = QMovie(star_path)
            self.star_label.setMovie(movie)
            movie.start()
            # 定位到宠物中心
            self.star_label.move(self.width() // 2 - 50, self.height() // 2 - 50)
            self.star_label.show()

            # 2秒后清除
            QTimer.singleShot(2000, self.star_label.deleteLater)
        except Exception as e:
            print(f"特效创建失败: {str(e)}")
            self.show_fallback_animation()

    def show_fallback_animation(self):
        """显示回退的文字动画"""
        self.fallback_label = QLabel("✨✨✨", self)
        self.fallback_label.setAlignment(Qt.AlignCenter)
        self.fallback_label.setFont(QFont("Arial", 24))

        # 居中显示
        self.fallback_label.move(
            self.width() // 2 - 70,
            self.height() // 2 - 180
        )
        self.fallback_label.show()

        # 添加淡出动画
        fade_anim = QPropertyAnimation(self.fallback_label, b"windowOpacity")
        fade_anim.setDuration(1500)
        fade_anim.setStartValue(1.0)
        fade_anim.setEndValue(0.0)
        fade_anim.start()

        # 2秒后清除
        QTimer.singleShot(2000, self.fallback_label.deleteLater)

    def jump_animation(self):
        """跳跃动画"""
        anim = QPropertyAnimation(self, b"pos")
        anim.finished.connect(anim.deleteLater)
        anim.setDuration(800)
        anim.setEasingCurve(QEasingCurve.OutBack)
        current_pos = self.pos()
        anim.setKeyValueAt(0.5, current_pos - QPoint(0, 100))  # 跳跃高度
        anim.setEndValue(current_pos)
        anim.start()

    def show_status_tooltip(self):
        """显示状态提示"""
        self.setToolTip("当前状态：\n❤ 健康值：100%\n⚡ 能量值：80%")
        QTimer.singleShot(3000, lambda: self.setToolTip(""))

    # ------------------- 待机系统 -------------------
    def check_idle(self):
        """检测用户是否待机"""
        idle_time = time.time() - self.last_active_time
        if idle_time > 300:  # 5分钟进入睡眠
            if self.state != self.SLEEPING:
                self.change_state(self.SLEEPING)
        elif idle_time > 180:  # 3分钟坐下休息
            if self.state not in (self.SITTING, self.SLEEPING):
                self.change_state(self.SITTING)

    def enter_domain(self):
        """进入星辉邻域"""
        # 新增检查：如果控制面板未初始化
        if not hasattr(self, 'control_panel') or self.control_panel is None:
            self.show_domain_dialog("请先打开控制面板看看吧")
            return

        if not self.control_panel.achievement_data.get("pioneer", False):
            self.control_panel.achievement_data["pioneer"] = 1
            self.control_panel.save_achievements()
            self.control_panel.show_achievement_popup("pioneer")
        # 首次进入需要选择路径
        if not self.domain_path:
            self.ask_domain_path()
            return

        self.show_domain_window()
        if self.domain_path:
            self.control_panel.update_achievements()  # 每次进入邻域时更新

    def ask_domain_path(self):
        """请求存储路径"""
        path = QFileDialog.getExistingDirectory(self, "选择星辉邻域存储位置", os.path.expanduser("~"))
        if not path:
            self.change_state(self.STANDING)
            return

        # 验证路径有效性
        try:
            if not os.path.exists(path):
                raise FileNotFoundError("路径不存在")
            if not os.access(path, os.W_OK):
                raise PermissionError("无写入权限")
        except Exception as e:
            self.show_domain_dialog(f"路径无效: {str(e)}")
            self.change_state(self.ERROR)
            return

        self.domain_path = path
        try:
            with open("config.json", "r+") as f:
                config = json.load(f)
                config["domain_path"] = self.domain_path
                f.seek(0)
                json.dump(config, f)
                f.truncate()
        except Exception as e:
            self.show_domain_dialog(f"保存配置失败: {str(e)}")
            self.change_state(self.ERROR)
        else:
            self.show_domain_window()

    def show_domain_window(self):
        """显示星辉邻域窗口（仿Windows桌面）"""
        try:
            # 提前初始化 domain_window
            self.domain_window = QMainWindow()

            # 关闭已存在的窗口
            if self.domain_window.isVisible():
                self.domain_window.close()

            # 检查路径存在性和权限
            if not os.path.exists(self.domain_path):
                self.show_domain_dialog("❌ 路径不存在，请重新选择！")
                self.ask_domain_path()
                return
            if not os.access(self.domain_path, os.R_OK):
                self.show_domain_dialog("❌ 无路径读取权限！")
                return

            # 检查背景图片
            bg_path = os.path.join("images", "星辉领域背景.png")
            if not os.path.exists(bg_path):
                self.show_domain_dialog("❌ 背景图片缺失！")
                return

            # 更新宠物状态
            self.change_state(self.HAPPY)
            self.show_domain_dialog("✨ 欢迎来到星辉邻域！")

            # 配置窗口
            self.domain_window.setWindowTitle("星辉邻域")
            self.domain_window.setGeometry(100, 100, 800, 600)
            self.domain_window.setStyleSheet(f"""
                QMainWindow {{
                    background-image: url({bg_path});
                    background-size: cover;
                    background-position: center;
                }}
            """)

            # 创建桌面布局
            self.desktop_area = QWidget()
            self.desktop_area.setAcceptDrops(True)
            self.desktop_layout = QGridLayout(self.desktop_area)
            self.desktop_layout.setSpacing(10)

            # 添加滚动条
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(self.desktop_area)
            self.domain_window.setCentralWidget(scroll)

            # 加载文件
            self.update_domain_files()

            # 显示窗口
            self.domain_window.show()

        except Exception as e:
            print(f"[ERROR] 初始化失败: {str(e)}")
            self.show_domain_dialog("⚠️ 初始化失败，请检查日志！")
            self.change_state(self.ERROR)

    def show_file_menu(self, pos):
        """文件列表右键菜单"""
        menu = QMenu()
        new_file_action = menu.addAction("新建文件")
        new_folder_action = menu.addAction("新建文件夹")
        delete_action = menu.addAction("删除")
        # ...添加更多操作...
        menu.exec_(self.file_list.mapToGlobal(pos))

    def update_domain_files(self):
        """更新星辉邻域中的文件图标视图"""
        try:
            # 清空旧图标
            for i in reversed(range(self.desktop_layout.count())):
                item = self.desktop_layout.itemAt(i)
                if item.widget():
                    item.widget().deleteLater()

            # 再次检查路径
            if not os.path.exists(self.domain_path):
                raise FileNotFoundError("路径不存在")

            row, col = 0, 0
            max_cols = 5  # 每行显示5个图标（原为4）

            # 遍历目录
            for filename in os.listdir(self.domain_path):
                filepath = os.path.join(self.domain_path, filename)

                # 创建图标按钮
                icon_btn = QPushButton()
                icon_btn.setFixedSize(100, 100)  # 增大按钮尺寸
                icon_btn.setIconSize(QSize(80, 80))  # 增大图标尺寸
                icon_btn.setStyleSheet("QPushButton { border: none; }")

                # 设置图标类型（使用系统图标或自定义图标）
                if os.path.isdir(filepath):
                    icon_btn.setIcon(self.style().standardIcon(QStyle.SP_DirIcon))
                    # 如果要使用自定义图标：
                    # icon_btn.setIcon(QIcon("images/folder.png"))
                else:
                    icon_btn.setIcon(self.style().standardIcon(QStyle.SP_FileIcon))
                    # 如果要使用自定义图标：
                    # icon_btn.setIcon(QIcon("images/file.png"))

                # 创建文件名标签
                label = QLabel(filename)
                label.setAlignment(Qt.AlignCenter)
                label.setStyleSheet("""
                    font: 10pt '微软雅黑'; 
                    color: #333; 
                    max-width: 100px;  # 防止文件名过长
                    word-wrap: break-word;  # 自动换行
                """)

                # 将图标和标签放入容器
                container = QWidget()
                container_layout = QVBoxLayout(container)
                container_layout.addWidget(icon_btn)
                container_layout.addWidget(label)

                # 添加到网格布局
                self.desktop_layout.addWidget(container, row, col)

                # 更新行列索引
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.show_domain_dialog(f"❌ 加载失败: {str(e)}")
            self.change_state(self.ERROR)

    def mouseDoubleClickEvent(self, event):
        """处理双击事件：打开文件/进入文件夹"""
        try:
            # 获取点击位置
            click_pos = event.pos()

            # 50%概率触发原有特效，50%概率触发花生抱枕彩蛋
            if random.random() < 0.5:
                self.jump_animation()
                self.create_special_effect()  # 原有特效
            else:
                self.trigger_peanut_cushion()  # 新增花生抱枕彩蛋

        except Exception as e:
            print(f"双击事件错误: {e}")

    def dropEvent(self, event):
        try:
            if not event.mimeData().hasUrls():
                return

            valid_files = []
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if not path:  # 新增空路径检查
                    continue

                if path.lower().endswith(".txt"):
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if "秘密口令" in content:
                                self.jump_animation()
                            elif "状态" in content:
                                self.show_status_tooltip()
                    except Exception as e:
                        print(f"文件读取失败: {e}")
                    finally:
                        self.change_state(self.EATING)
                        valid_files.append(path)  # 记录有效的txt文件
                else:
                    self.change_state(self.ERROR)
                    # 跳过非txt文件，继续处理下一个
                    continue

            # 统一安排删除任务（只删除txt文件）
            for file_path in valid_files:
                QTimer.singleShot(0, lambda path=file_path: self.safe_remove(path))

            event.acceptProposedAction()
        except Exception as e:
            print(f"拖放处理异常: {e}")
            self.change_state(self.ERROR)

    def show_domain_dialog(self, text):
        """显示星辉对话框 - 优化版"""
        # 如果已有对话框，先移除
        if hasattr(self, 'domain_dialog') and self.domain_dialog:
            self.domain_dialog.deleteLater()

        # 创建新对话框
        self.domain_dialog = QLabel(self)
        self.domain_dialog.setText(text)
        self.domain_dialog.setStyleSheet("""
            QLabel {
                background: rgba(255, 255, 225, 0.92);
                border-radius: 12px;
                padding: 12px 18px;
                font: bold 15px 'Segoe UI Variable';
                color: #2C3E50;
                border: 2px solid #FFD700;
                min-width: 200px;
                max-width: 400px;
            }
        """)
        self.domain_dialog.setAlignment(Qt.AlignCenter)
        self.domain_dialog.setWordWrap(True)  # 关键：启用自动换行
        self.domain_dialog.setContentsMargins(15, 10, 15, 10)
        self.domain_dialog.adjustSize()

        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(3, 3)
        self.domain_dialog.setGraphicsEffect(shadow)

        # 定位到右上角，但确保不会超出屏幕
        dialog_width = self.domain_dialog.width()
        dialog_height = self.domain_dialog.height()

        # 计算安全位置
        screen_geometry = QDesktopWidget().availableGeometry()
        max_x = screen_geometry.width() - dialog_width - 20

        dialog_x = min(self.width() - dialog_width - 15, max_x)
        dialog_y = 15

        self.domain_dialog.move(dialog_x, dialog_y)
        self.domain_dialog.show()

        # 添加淡入动画
        self.domain_dialog.setWindowOpacity(0)

        fade_in = QPropertyAnimation(self.domain_dialog, b"windowOpacity")
        fade_in.setDuration(350)
        fade_in.setStartValue(0)
        fade_in.setEndValue(1)
        fade_in.start()

        # 3秒后自动隐藏
        self.domain_dialog_timer.start(3000)

    def hide_domain_dialog(self):
        """隐藏对话框"""
        self.domain_dialog.hide()
        self.domain_dialog_timer.stop()

    def update_peanut_dialog(self, text, phase):
        """更新花生对话框内容（不重置位置）"""
        # 确保阶段匹配
        if self.peanut_phase != phase:
            return

        # 确保对话框存在
        if hasattr(self, 'peanut_dialog') and self.peanut_dialog:
            # 获取当前位置
            current_pos = self.peanut_dialog.pos()

            # 更新文本
            self.peanut_dialog.setText(text)
            self.peanut_dialog.adjustSize()

            # 保持垂直位置不变，水平居中
            dialog_x = (self.width() - self.peanut_dialog.width()) // 2
            self.peanut_dialog.move(dialog_x, current_pos.y())

    def trigger_peanut_cushion(self):
        """触发花生抱枕彩蛋"""
        # 停止当前所有动画和状态
        if hasattr(self, "physics_timer") and self.physics_timer.isActive():
            self.physics_timer.stop()
        if self.drag_anim_timer.isActive():
            self.drag_anim_timer.stop()
        if self.sleep_anim_timer.isActive():
            self.sleep_anim_timer.stop()

        # 切换到花生抱枕状态
        self.change_state(self.PEANUT_CUSHION)
        self.peanut_phase = 1  # 第一阶段

        # 显示第一阶段对话 - 使用新的持续显示方法
        self.show_peanut_dialog("这是我很喜欢的一个抱枕！", phase=1)

        # 5秒后切换到第二阶段
        QTimer.singleShot(5000, lambda: self.next_peanut_phase(1))

    def next_peanut_phase(self, current_phase):
        """切换到花生抱枕下一阶段"""
        # 确保仍在花生抱枕状态且阶段匹配
        if self.state != self.PEANUT_CUSHION or self.peanut_phase != current_phase:
            return

        self.peanut_phase += 1

        if self.peanut_phase == 2:
            # 更新对话框内容
            self.show_peanut_dialog("是个花生抱枕！", phase=2)
            # 5秒后恢复原状态
            QTimer.singleShot(5000, lambda: self.recover_from_peanut(2))
        elif self.peanut_phase > 2:
            self.recover_from_peanut(2)

    def recover_from_peanut(self, expected_phase):
        """从花生抱枕状态恢复（带阶段验证）"""
        # 添加空值检查并验证阶段
        if self.state == self.PEANUT_CUSHION and self.peanut_phase == expected_phase:
            # 隐藏对话框（不删除）
            if hasattr(self, 'peanut_dialog') and self.peanut_dialog:
                # 使用淡出动画隐藏对话框
                fade_out = QPropertyAnimation(self.peanut_dialog, b"windowOpacity")
                fade_out.setDuration(1000)
                fade_out.setStartValue(1.0)
                fade_out.setEndValue(0.0)
                fade_out.finished.connect(self.peanut_dialog.hide)
                fade_out.start()

            # 恢复原状态
            if self.is_manual_wake:
                self.change_state(self.STANDING)
            else:
                current_hour = datetime.datetime.now().hour
                if (current_hour >= 21) or (current_hour < 7):
                    self.change_state(self.SLEEPING)
                else:
                    self.change_state(self.STANDING)

    def show_peanut_dialog(self, text, phase=1):
        """显示花生抱枕对话框（初始创建）"""
        # 确保对话框存在
        if not hasattr(self, 'peanut_dialog') or not self.peanut_dialog:
            # 创建新对话框
            self.peanut_dialog = QLabel(self)
            self.peanut_dialog.setStyleSheet("""
                background: rgba(255, 245, 200, 0.95);
                border: 2px solid #DAA520;
                border-radius: 15px;
                padding: 12px;
                font: bold 14px '微软雅黑';
                color: #8B4513;
                min-width: 200px;
            """)
            self.peanut_dialog.setAlignment(Qt.AlignCenter)
            self.peanut_dialog.setWordWrap(True)
            self.peanut_dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # 更新文本
        self.peanut_dialog.setText(text)
        self.peanut_dialog.adjustSize()

        # 定位对话框（宠物上方）
        dialog_x = (self.width() - self.peanut_dialog.width()) // 2
        dialog_y = -self.peanut_dialog.height() - 10
        self.peanut_dialog.move(dialog_x, dialog_y)

        # 确保对话框可见
        if not self.peanut_dialog.isVisible():
            self.peanut_dialog.show()

        # 添加入场动画
        anim = QPropertyAnimation(self.peanut_dialog, b"pos")
        anim.setDuration(500)
        anim.setStartValue(QPoint(dialog_x, -100))
        anim.setEndValue(QPoint(dialog_x, dialog_y))
        anim.setEasingCurve(QEasingCurve.OutBack)
        anim.start()


from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QSlider, QLabel, QStackedWidget, QComboBox
)


class ControlPanel(QWidget):
    CONFIG_PATH = os.path.join(os.getenv('LOCALAPPDATA'), 'StarPet')
    AUDIO_CONFIG = os.path.join(CONFIG_PATH, 'audio_config.json')
    THEME_CONFIG = os.path.join(CONFIG_PATH, 'theme_config.json')
    def __init__(self, pet):
        super().__init__()
        ico_path = os.path.join("images", "桌面星辉图标.ico")  # 设置窗口图标
        if os.path.exists(ico_path):
            self.setWindowIcon(QIcon(ico_path))
        self.pet = pet
        self.original_scale = pet.IMG_SCALE
        self.achievement_data = {
            "pioneer": 0,
            "writer": 0,
            "first_5star": 0,
            "first_birthday": 0,
            "ask_star": 0
        }
        self.abnormality_data = {
            "O-02-88": {
                "name": "星辉守护者",
                "risk_level": "ALEPH",
                "can_constellation": True,
                "description": "源自代码深渊的友善实体，会主动保护用户系统安全。\n特性：\n- 自动拦截危险进程\n- 吞噬恶意文件\n- 情绪化物理反馈",
                "quote": "\"星光闪烁之处，即是代码的归途\"",
                "img": "星辉守护者.png",
                "can_target": True  # 允许定轨
            },
            # 可添加更多条目
            "O-05-72": {
                "name": "松鼠",
                "risk_level": "ALEPH",
                "can_constellation": True,
                "description": "穿梭于系统枝桠的量子实体，会收集碎片化的数据果实。\n特性：\n- 以电磁脉冲为食\n- 在星辉邻域埋藏密钥\n- 通过点击频率传递信息\n- 对恶意程序展现出攻击性",
                "quote": "\「每个像素跃动都是我的足迹，每串代码震颤都是我的絮语\」",
                "img": "松鼠.png",
                "can_target": True
            },
            "O-03-99": {  # 新增文广老师编号
                "name": "文广",
                "risk_level": "ALEPH",
                "can_constellation": True,
                "description": "严谨而富有智慧的数学老师，以逻辑之光引导迷途。\n特性：\n- 解析复杂数学问题\n- 提升用户逻辑思维能力\n- 对错误计算零容忍",
                "quote": "\"公式不熟 一切免谈！！\"",
                "img": "文广.png",
                "can_target": True
            },
            "O-07-99": {
                "name": "皇上",
                "risk_level": "ZAYIN",  # 初始为ZAYIN级
                "can_constellation": True,
                "description": "仓鼠皇帝，喜欢在轮子上奔跑。",
                "quote": "朕的瓜子呢？",
                "img": "皇上.png",
                "can_target": True,
                # 满命后数据
                "aleph_data": {
                    "name": "仓皇大帝",
                    "risk_level": "ALEPH",
                    "description": "仓皇大帝，拥有掌控星辰的力量。它的轮子已化作金色战车，能驾驭星辉穿梭于数据宇宙。",
                    "quote": "众卿平身！朕即天命！",
                    "img": "仓皇大帝.png"
                }
            },
        }
        self.load_pity_data()
        self.pool_data = {
            "O-02-88": {
                "name": "星辉守护者卡池",
                "rate_up": ["O-02-88"],
                "5star_weights": {"O-02-88": 1.0},
                "base_5star_rate": 0.007
            },
            "O-05-72": {
                "name": "量子松鼠卡池",
                "rate_up": ["O-05-72"],
                "5star_weights": {"O-05-72": 1.0},
                "base_5star_rate": 0.008
            },
            "O-03-99": {
                "name": "文广卡池",
                "rate_up": ["O-03-99"],
                "5star_weights": {"O-03-99": 1.0},
                "base_5star_rate": 0.006
            },
            "O-07-99": {
                "name": "仓皇大帝卡池",
                "rate_up": ["O-07-99"],
                "5star_weights": {"O-07-99": 1.0},
                "base_5star_rate": 0.006
            },
        }
        self.constellation_data = {}  # 添加命之座数据存储
        self.load_constellations()
        self.wish_counter = {
            '4star_pity': 0,  # 四星保底计数
            '5star_pity': 0  # 五星保底计数
        }
        self.load_pity_data()

        self.current_theme = "light"  # 默认白昼模式
        self.load_theme_config()
        # 现在初始化UI
        self.image_cache = {}
        self.initUI()
        self.apply_theme()  # 应用当前主题
        self.setStyleSheet(self.get_stylesheet())

        self.tabs.addTab(self.create_abnormality_settings(), "📜 异想体档案")
        self.load_achievements()  # 新增成就加载
        self.tabs.addTab(self.create_achievement_gallery(), "🏆 成就徽章馆")  # 新增选项卡

        self.abnormality_manager = AbnormalityManager(self)

        # 加载配置
        self.load_config()
        self.current_abno_id = None  # 记录当前选中的异想体ID


    def create_achievement_gallery(self):
        """成就徽章馆 - 纯横向排列布局"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # 搜索栏
        search_box = QLineEdit()
        search_box.setPlaceholderText("搜索成就...")
        search_box.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E0E0E0;
                border-radius: 15px;
                padding: 8px 15px;
                font-size: 14px;
            }
        """)
        search_box.textChanged.connect(self.update_achievements)
        layout.addWidget(search_box)

        # ====== 关键修改：使用水平布局代替网格布局 ======
        # 创建水平滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:horizontal {
                height: 12px;
                background: #F0F0F0;
                border-radius: 6px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #C0C0C0;
                min-width: 30px;
                border-radius: 6px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
                height: 0px;
            }
        """)

        # 水平布局容器
        scroll_content = QWidget()
        self.horizontal_layout = QHBoxLayout(scroll_content)
        self.horizontal_layout.setSpacing(25)  # 卡片间距
        self.horizontal_layout.setContentsMargins(20, 10, 20, 20)
        self.horizontal_layout.addStretch()  # 添加弹性空间使卡片居中

        # 设置滚动区域内容
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        # ========== 修改结束 ==========

        # 成就数据
        self.achievements = {
            "pioneer": {
                "name": "星际开拓者",
                "desc": "首次进入星辉邻域",
                "icon": QPixmap("images/进入星辉邻域.png"),
                "progress": lambda: self.achievement_data.get("pioneer", 0),
                "max": 1
            },
            "writer": {
                "name": "星辰记录者",
                "desc": "创建对话文件",
                "icon": QPixmap("images/创建对话文件.png"),
                "progress": lambda: self.achievement_data.get("writer", 0),
                "max": 5
            },
            "first_5star": {
                "name": "星穹初绽",
                "desc": "首次获得五星物品",
                "icon": QPixmap("images/第一次出金.png"),
                "progress": lambda: self.achievement_data.get("first_5star", 0),
                "max": 1
            },
            "first_birthday": {
                "name": "星辉的生日",
                "desc": "陪星辉过第一个生日",
                "icon": QPixmap("images/陪星辉过生日.png"),  # 使用生日蛋糕图标
                "progress": lambda: self.achievement_data.get("first_birthday", 0),
                "max": 1,
                "hidden": True  # 标记为隐藏成就
            },
            "ask_star": {
                "name": "问星辉",
                "desc": "打开问星辉界面",
                "icon": QPixmap("images/问星辉.png"),
                "progress": lambda: self.achievement_data.get("ask_star", 0),
                "max": 1,
                "hidden": True  # 标记为隐藏成就
            }
        }

        # 初始化成就卡片
        self.update_achievements()
        return page

    def create_badge_card(self, key, data):
        """创建包含动态样式的成就卡片（带主题适配）"""
        # 如果成就被隐藏且尚未解锁则跳过
        if data.get("hidden", False) and data["progress"]() < 1:
            return None

        # 添加星形标记表示隐藏成就（如果已解锁）
        display_name = data["name"]
        if data.get("hidden", False) and data["progress"]() >= data["max"]:
            display_name = "★ " + data["name"] + " ★"

        # 创建卡片容器
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFixedSize(220, 260)
        frame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # 主布局
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # ========== 图标区域（带抗锯齿处理）==========
        icon_label = QLabel()
        if not data["icon"].isNull():
            # 使用高质量抗锯齿缩放
            target_size = QSize(100, 100)
            scaled = data["icon"].scaled(
                target_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            # 创建抗锯齿蒙版
            mask = QBitmap(target_size)
            mask.clear()
            mask_painter = QPainter(mask)
            mask_painter.setRenderHint(QPainter.Antialiasing)
            mask_painter.setBrush(Qt.color1)
            mask_painter.drawRoundedRect(0, 0, 100, 100, 15, 15)
            mask_painter.end()

            scaled.setMask(mask)
            icon_label.setPixmap(scaled)
        else:
            icon_label.setText("❌ 图标缺失")
            icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label, alignment=Qt.AlignCenter)

        # ========== 进度显示 ==========
        progress = QProgressBar()
        progress.setMaximum(data["max"])
        progress.setValue(data["progress"]())
        progress.setTextVisible(True)
        progress.setFormat(f"{data['progress']()}/{data['max']} 进度")

        # ========== 文字描述 ==========
        title_label = QLabel(display_name)
        title_label.setAlignment(Qt.AlignCenter)

        desc_label = QLabel(data["desc"])
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # ========== 动态主题样式 ==========
        if self.current_theme == "dark":
            # 黑夜模式样式
            if data["progress"]() >= data["max"]:
                # 已完成成就的黑夜样式 - 修改名称颜色为白色
                frame_style = """
                        QFrame {
                            border: 2px solid #FFD700;
                            border-radius: 12px;
                            background: #2D2D2D;
                        }
                    """
                title_style = "font: bold 14px '微软雅黑'; color: #FFFFFF;"  # 修改为白色
                desc_style = "font: 12px '微软雅黑'; color: #B0B0B0;"
                progress_style = """
                        QProgressBar {
                            height: 20px;
                            text-align: center;
                            border-radius: 10px;
                            background: #1E1E1E;
                            color: white;
                        }
                        QProgressBar::chunk {
                            background: qlineargradient(
                                spread:pad, 
                                x1:0, y1:0.5, 
                                x2:1, y2:0.5, 
                                stop:0 #FFD700, 
                                stop:0.3 #FFA500,
                                stop:1 #FF8C00
                            );
                            border-radius: 10px;
                        }
                    """
            else:
                # 未完成成就的黑夜样式 - 修改名称颜色为白色
                frame_style = """
                        QFrame {
                            border: 1px solid #555555;
                            border-radius: 12px;
                            background: #2D2D2D;
                        }
                    """
                title_style = "font: bold 14px '微软雅黑'; color: #FFFFFF;"  # 修改为白色
                desc_style = "font: 12px '微软雅黑'; color: #888888;"
                progress_style = """
                        QProgressBar {
                            height: 20px;
                            text-align: center;
                            border-radius: 10px;
                            background: #1E1E1E;
                            color: white;
                        }
                        QProgressBar::chunk {
                            background: qlineargradient(
                                spread:pad, 
                                x1:0, y1:0.5, 
                                x2:1, y2:0.5, 
                                stop:0 #00BFFF, 
                                stop:0.5 #1E90FF,
                                stop:1 #4169E1
                            );
                            border-radius: 10px;
                        }
                    """
        else:
            # 白昼模式样式
            if data["progress"]() >= data["max"]:
                # 已完成成就的白昼样式
                frame_style = """
                    QFrame {
                        border: 2px solid #FFD700;
                        border-radius: 12px;
                        background: #FFFCF5;
                    }
                """
                title_style = "font: bold 14px '微软雅黑'; color: #2C3E50;"
                desc_style = "font: 12px '微软雅黑'; color: #7F8C8D;"
                progress_style = """
                    QProgressBar {
                        height: 20px;
                        text-align: center;
                        border-radius: 10px;
                        background: #FFF9E6;
                    }
                    QProgressBar::chunk {
                        background: qlineargradient(
                            x1:0, y1:0, x2:1, y2:0,
                            stop:0 #FFD700, stop:1 #FFA500
                        );
                        border-radius: 10px;
                    }
                """
            else:
                # 未完成成就的白昼样式
                frame_style = """
                    QFrame {
                        border: 1px solid #E0E0E0;
                        border-radius: 12px;
                        background: white;
                    }
                """
                title_style = "font: bold 14px '微软雅黑'; color: #2C3E50;"
                desc_style = "font: 12px '微软雅黑'; color: #7F8C8D;"
                progress_style = """
                    QProgressBar {
                        height: 20px;
                        text-align: center;
                        border-radius: 10px;
                        background: #EEE;
                    }
                    QProgressBar::chunk {
                        background: qlineargradient(
                            x1:0, y1:0, x2:1, y2:0,
                            stop:0 #4ECDC4, stop:1 #45B7D1
                        );
                        border-radius: 10px;
                    }
                """

        # 应用样式
        frame.setStyleSheet(frame_style)
        title_label.setStyleSheet(title_style)
        desc_label.setStyleSheet(desc_style)
        progress.setStyleSheet(progress_style)

        # 将文字添加到布局
        text_layout = QVBoxLayout()
        text_layout.addWidget(title_label)
        text_layout.addWidget(desc_label)
        layout.addLayout(text_layout)
        layout.addWidget(progress)

        # ========== 交互特效 ==========
        def enter_event(event):
            if data["progress"]() < data["max"]:
                if self.current_theme == "dark":
                    frame.setStyleSheet("""
                        QFrame {
                            border: 2px solid #0078D4;
                            border-radius: 12px;
                            background: #3A3A3A;
                        }
                    """)
                else:
                    frame.setStyleSheet("""
                        QFrame {
                            border: 2px solid #0078D4;
                            border-radius: 12px;
                            background: #F0F9FF;
                        }
                    """)

        def leave_event(event):
            frame.setStyleSheet(frame_style)

        frame.enterEvent = enter_event
        frame.leaveEvent = leave_event

        return frame

    def update_achievements(self, filter_text=""):
        """动态更新成就布局 - 改为横向排列"""
        # 清空旧内容
        while self.horizontal_layout.count():
            item = self.horizontal_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 添加成就卡片
        for key, data in self.achievements.items():
            # 如果是隐藏成就且未解锁则跳过
            if data.get("hidden", False) and data["progress"]() < 1:
                continue

            # 过滤文本
            if filter_text.lower() not in data["name"].lower():
                continue

            card = self.create_badge_card(key, data)
            self.horizontal_layout.addWidget(card)

        # 添加弹性空间使卡片左对齐
        self.horizontal_layout.addStretch()

    def get_stylesheet(self):
        """Windows 11平面化样式表"""
        return """
            /* ========== 基础样式 ========== */
            QWidget {
                font-family: 'Segoe UI Variable';
                font-size: 14px;
                color: #1A1A1A;
                background: #FFFFFF;
            }

            /* ========== 按钮样式 ========== */
            QPushButton {
                background-color: #F3F3F3;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 8px 16px;
                min-width: 80px;
                color: #1A1A1A;
            }
            QPushButton:hover {
                background-color: #E5E5E5;
                border-color: #D0D0D0;
            }
            QPushButton:pressed {
                background-color: #0078D4;
                color: white;
                border-color: #0078D4;
            }
            QPushButton:checked {
                background-color: #0078D4;
                color: white;
            }

            /* ========== 选项卡优化 ========== */
            QTabBar::tab {
                background: #F8F8F8;
                border: none;
                padding: 12px 24px;
                margin: 2px;
                border-radius: 6px;
            }
            QTabBar::tab:selected {
                background: #0078D4;
                color: white;
            }

            /* ========== 滑动条平面化 ========== */
            QSlider::groove:horizontal {
                height: 4px;
                background: #E0E0E0;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                width: 16px;
                height: 16px;
                margin: -6px 0;
                background: #0078D4;
                border-radius: 8px;
                border: none;
            }

            /* ========== 去除底部阴影 ========== */
            QGroupBox {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                margin-top: 16px;
                padding-top: 24px;
                background: white;
            }
            /* 新增异想体相关样式 */
            QLineEdit:focus {
            border-color: #0078D4;
            }
            QTextBrowser {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 12px;
            }
        """

    def initUI(self):
        """初始化界面（含应用/取消按钮）"""
        self.setWindowTitle("星辉控制面板")
        self.setMinimumSize(600, 500)

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)

        # 选项卡
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_size_settings(), "⚙️ 基础设置")
        self.tabs.addTab(self.create_behavior_settings(), "🧬 行为设置")
        self.tabs.addTab(self.create_appearance_settings(), "🎨 外观设置")
        main_layout.addWidget(self.tabs)

        # 按钮区域
        button_layout = QHBoxLayout()
        btn_cancel = QPushButton("取消")
        btn_apply = QPushButton("应用")
        button_layout.addStretch()  # 将按钮推到右侧
        button_layout.addWidget(btn_cancel)
        button_layout.addWidget(btn_apply)
        main_layout.addLayout(button_layout)

        # 事件绑定
        btn_apply.clicked.connect(self.apply_all_settings)
        btn_cancel.clicked.connect(self.close)

        self.setLayout(main_layout)

    def apply_all_settings(self):
        """应用所有设置并保存"""
        self.apply_size_settings()
        self.save_config()
        self.close()

    def save_config(self):
        """保存基础配置及祈愿池信息"""
        try:
            config = {}
            if os.path.exists("config.json"):
                with open("config.json", "r") as f:
                    config = json.load(f)

            # 合并新旧配置项
            config.update({
                "scale": self.pet.IMG_SCALE,
                "idle_time": self.idle_combo.currentIndex(),
                "current_pool": list(self.pool_data.keys())[self.pool_combo.currentIndex()]
            })

            with open("config.json", "w") as f:
                json.dump(config, f)

            # 同步保存祈愿保底数据
            self.save_pity_data()
            self.save_constellations()
            self.save_achievements()
            self.save_theme_config()

        except Exception as e:
            print(f"综合配置保存失败: {str(e)}")
            self.pet.change_state(self.pet.ERROR)

    def load_config(self):
        """加载综合配置信息"""
        try:
            config = {}
            if os.path.exists("config.json"):
                with open("config.json", "r") as f:
                    config = json.load(f)

            # 加载基础设置
            if "scale" in config:
                self.size_slider.setValue(int(config["scale"] * 100))
                self.apply_size_settings()

            # 加载待机设置
            if "idle_time" in config:
                self.idle_combo.setCurrentIndex(config["idle_time"])

            # 加载祈愿池设置（带异常处理）
            if "current_pool" in config:
                try:
                    pool_index = list(self.pool_data.keys()).index(config["current_pool"])
                    self.pool_combo.setCurrentIndex(pool_index)
                except (ValueError, KeyError) as e:
                    print(f"祈愿池配置加载异常，使用默认值: {str(e)}")
                    self.pool_combo.setCurrentIndex(0)

            # 加载其他子系统配置
            self.load_pity_data()
            self.load_constellations()
            self.load_achievements()
            self.load_theme_config()
            # 应用主题
            self.apply_theme()

        except Exception as e:
            print(f"综合配置加载失败: {str(e)}")
            self.pet.change_state(self.pet.ERROR)

    def create_nav_button(self, text):
        """创建导航按钮"""
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setFixedHeight(40)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                color: #495057;
                border-radius: 8px;
                font-size: 14px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
            QPushButton:checked {
                background-color: #007bff;
                color: white;
            }
        """)
        btn.clicked.connect(lambda: self.switch_page([
                                                         self.btn_size,
                                                         self.btn_behavior,
                                                         self.btn_appearance
                                                     ].index(btn)))
        return btn

    def init_pages(self):
        """初始化所有设置页面"""
        # 尺寸设置
        size_page = QWidget()
        size_layout = QVBoxLayout(size_page)
        size_layout.addWidget(self.create_size_settings())
        self.stack.addWidget(size_page)

        # 行为设置
        behavior_page = QWidget()
        behavior_layout = QVBoxLayout(behavior_page)
        behavior_layout.addWidget(self.create_behavior_settings())
        self.stack.addWidget(behavior_page)

        # 外观设置
        appearance_page = QWidget()
        appearance_layout = QVBoxLayout(appearance_page)
        appearance_layout.addWidget(self.create_appearance_settings())
        self.stack.addWidget(appearance_page)

    def create_size_settings(self):
        """基础设置页（移除自动保存逻辑）"""
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # 尺寸调节组
        size_group = QGroupBox("尺寸设置")
        size_layout = QGridLayout()

        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(5, 20)
        self.size_slider.setValue(int(self.pet.IMG_SCALE * 100))

        # 修复这里：变量名改为 size_value
        self.size_value = QLabel(f"当前尺寸：{int(self.pet.IMG_SCALE * 100)}%")

        # 添加滑块值变化的连接
        self.size_slider.valueChanged.connect(self.update_size_preview)

        size_layout.addWidget(QLabel("缩放比例:"), 0, 0)
        size_layout.addWidget(self.size_slider, 0, 1)
        size_layout.addWidget(self.size_value, 0, 2)  # 这里也改为 size_value
        size_group.setLayout(size_layout)

        # 物理参数组
        physics_group = QGroupBox("物理参数")
        physics_layout = QFormLayout()

        self.gravity_slider = QSlider(Qt.Horizontal)
        self.gravity_slider.setRange(1000, 3000)
        self.gravity_slider.setValue(int(self.pet.PHYSICS['gravity']))  # 强制转整数
        physics_layout.addRow("重力系数:", self.gravity_slider)
        physics_group.setLayout(physics_layout)

        layout.addWidget(size_group)
        layout.addWidget(physics_group)
        layout.addStretch()

        page.setLayout(layout)
        return page

    def create_behavior_settings(self):
        """行为设置页"""
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # 待机时间设置
        idle_group = QGroupBox("待机行为")
        idle_layout = QFormLayout()

        self.idle_combo = QComboBox()
        self.idle_combo.addItems(["3分钟", "5分钟", "10分钟"])
        idle_layout.addRow("休眠时间:", self.idle_combo)

        self.reaction_slider = QSlider(Qt.Horizontal)
        self.reaction_slider.setRange(1, 5)
        idle_layout.addRow("互动灵敏度:", self.reaction_slider)

        idle_group.setLayout(idle_layout)

        layout.addWidget(idle_group)
        layout.addStretch()

        page.setLayout(layout)
        return page

    def apply_theme(self):
        """根据当前主题应用样式表（包含祈愿下拉栏颜色修复）"""
        base_stylesheet = self.get_stylesheet()

        if self.current_theme == "dark":
            theme_stylesheet = """
                /* ====== 黑夜模式覆盖样式 ====== */
                QWidget {
                    background-color: #1E1E1E;
                    color: #F0F0F0;
                }
                QGroupBox {
                    color: #F0F0F0;
                    border-color: #555555;
                }
                QLabel {
                    color: #F0F0F0;
                }
                QTextBrowser {
                    background-color: #2D2D2D;
                    color: #F0F0F0;
                }
                QLineEdit {
                    background-color: #2D2D2D;
                    color: #F0F0F0;
                    border: 1px solid #555555;
                }
                QComboBox {
                    background-color: #2D2D2D;
                    color: #F0F0F0;  /* 下拉框当前值文本颜色 */
                    border: 1px solid #555555;
                }
                QComboBox QAbstractItemView {
                    background-color: #2D2D2D;
                    color: #F0F0F0;  /* 下拉选项文本颜色 */
                    selection-background-color: #0078D4;  /* 选中项背景色 */
                    selection-color: #FFFFFF;  /* 选中项文本颜色 */
                }
                QListWidget {
                    background-color: #2D2D2D;
                    color: #F0F0F0;
                }

                /* ========== 关键修复：卡池下拉框文本颜色 ========== */
                QComboBox#poolCombo {
                    background-color: #2D2D2D;
                    color: #adb5bd;  /* 当前选中项文本设置为岩石灰色 */
                    border: 1px solid #555555;
                }
                QComboBox#poolCombo::item:selected {
                    background-color: #0078D4;
                    color: #adb5bd;  /* 选中项文本保持岩石灰色 */
                }
                QComboBox#poolCombo::drop-down {
                    border: none;
                    background: transparent;
                }
                QComboBox#poolCombo QAbstractItemView {
                    background-color: #2D2D2D;
                    color: #adb5bd;  /* 下拉选项文本设置为岩石灰色 */
                }

                /* ========== 未选中导航卡黑夜模式样式 ========== */
                QTabBar::tab:!selected {
                    background: #2D2D2D;
                    color: #A0A0A0;
                    border: 1px solid #444444;
                }
                QTabBar::tab:selected {
                    background: #0078D4;
                    color: white;
                }

                /* 保持按钮样式不变 */
                QPushButton {
                    background-color: #F3F3F3;
                    color: #1A1A1A;
                }
                QPushButton:hover {
                    background-color: #E5E5E5;
                }
                QPushButton:pressed {
                    background-color: #0078D4;
                    color: white;
                }
            """
        else:
            # 白昼模式样式
            theme_stylesheet = """
                /* 白昼模式下恢复正常样式 */
                QComboBox#poolCombo {
                    color: #1A1A1A;
                    background: white;
                    border: 1px solid #E0E0E0;
                }
                QComboBox#poolCombo QAbstractItemView {
                    color: #1A1A1A;
                    background: white;
                }
            """

        # 应用基础样式+主题样式
        self.setStyleSheet(base_stylesheet + theme_stylesheet)

        # 确保祈愿池下拉框设置对象名（关键修复）
        if hasattr(self, 'pool_combo') and not self.pool_combo.objectName():
            self.pool_combo.setObjectName("poolCombo")

    def create_appearance_settings(self):
        """外观设置页（动态加载音乐文件）"""
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # 动态获取音频文件列表
        self.audio_files = self.get_audio_list()

        # 音乐设置组
        music_group = QGroupBox("背景音乐设置")
        music_layout = QFormLayout()

        # 音乐选择下拉框
        self.music_combo = QComboBox()
        self.music_combo.addItem("禁用")
        self.music_combo.addItems(self.audio_files)

        # 预览按钮
        preview_btn = QPushButton("试听")
        preview_btn.clicked.connect(lambda: self.preview_music(self.music_combo.currentText()))

        # 音量控制
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)

        # 加载当前设置
        try:
            if os.path.exists(ControlPanel.AUDIO_CONFIG):
                with open(ControlPanel.AUDIO_CONFIG, 'r') as f:
                    config = json.load(f)
                    current_music = config.get('bgm', '禁用')
                    if current_music in self.audio_files:
                        self.music_combo.setCurrentText(current_music)
                    self.volume_slider.setValue(config.get('volume', 80))
        except Exception as e:
            print(f"音频配置加载失败: {str(e)}")

        # 布局
        hbox = QHBoxLayout()
        hbox.addWidget(self.music_combo)
        hbox.addWidget(preview_btn)

        music_layout.addRow("当前曲目:", hbox)
        music_layout.addRow("音量调节:", self.volume_slider)
        music_group.setLayout(music_layout)

        # ========== 新增主题设置组 ==========
        theme_group = QGroupBox("主题设置")
        theme_layout = QGridLayout()

        # 主题切换下拉框
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("白昼模式", "light")
        self.theme_combo.addItem("黑夜模式", "dark")

        # 设置当前主题
        current_index = self.theme_combo.findData(self.current_theme)
        if current_index >= 0:
            self.theme_combo.setCurrentIndex(current_index)

        # 主题切换事件
        self.theme_combo.currentIndexChanged.connect(self.change_theme)

        theme_layout.addWidget(QLabel("界面主题:"), 0, 0)
        theme_layout.addWidget(self.theme_combo, 0, 1)

        # 原有动画设置
        self.anim_combo = QComboBox()
        self.anim_combo.addItems(["流畅模式", "节能模式"])
        theme_layout.addWidget(QLabel("动画效果:"), 1, 0)
        theme_layout.addWidget(self.anim_combo, 1, 1)

        theme_group.setLayout(theme_layout)

        # 将所有组件添加到布局
        layout.addWidget(theme_group)
        layout.addWidget(music_group)
        layout.addStretch()

        page.setLayout(layout)
        return page

    def change_theme(self):
        """切换主题并立即应用（带成就刷新）"""
        # 保存当前选中的成就列表项（如果有）
        selected_text = self.search_box.text() if hasattr(self, 'search_box') else ""

        # 更新当前主题
        if hasattr(self, 'theme_combo'):
            self.current_theme = self.theme_combo.currentData()

        # 应用主题样式
        self.apply_theme()

        # 保存主题设置
        self.save_theme_config()

        # 刷新成就显示
        if hasattr(self, 'update_achievements'):
            self.update_achievements(selected_text)

        # 刷新异想体档案（如果存在）
        if hasattr(self, 'abno_list') and self.abno_list.count() > 0:
            # 确保列表有选中项
            if not self.abno_list.currentItem():
                self.abno_list.setCurrentRow(0)
            current_item = self.abno_list.currentItem()
            if current_item:
                self.update_abno_details(current_item)

        # 刷新控制面板其他部分（如果存在）
        if hasattr(self, 'control_panel'):
            self.control_panel.update()

    def save_theme_config(self):
        """保存主题配置到单独文件"""
        try:
            if not os.path.exists(ControlPanel.CONFIG_PATH):
                os.makedirs(ControlPanel.CONFIG_PATH)

            # 确保获取当前主题值
            if hasattr(self, 'theme_combo'):
                self.current_theme = self.theme_combo.currentData()

            with open(ControlPanel.THEME_CONFIG, 'w') as f:
                json.dump({"theme": self.current_theme}, f)
        except Exception as e:
            print(f"主题配置保存失败: {str(e)}")

    def load_theme_config(self):
        """从文件加载主题配置"""
        try:
            if os.path.exists(ControlPanel.THEME_CONFIG):
                with open(ControlPanel.THEME_CONFIG, 'r') as f:
                    config = json.load(f)
                    self.current_theme = config.get("theme", "light")

            # 确保主题下拉框同步
            if hasattr(self, 'theme_combo'):
                index = self.theme_combo.findData(self.current_theme)
                if index >= 0:
                    self.theme_combo.setCurrentIndex(index)
        except Exception as e:
            print(f"主题配置加载失败: {str(e)}")

    def get_audio_list(self):
        """动态获取audio文件夹中的WAV文件列表"""
        audio_list = []
        audio_dir = "audio"

        try:
            # 创建audio文件夹如果不存在
            if not os.path.exists(audio_dir):
                os.makedirs(audio_dir)
                return audio_list

            # 遍历文件夹获取所有wav文件
            for file in os.listdir(audio_dir):
                if file.lower().endswith(".wav"):
                    # 去除扩展名并添加到列表
                    audio_list.append(os.path.splitext(file)[0])

            # 按文件名排序
            audio_list.sort()
        except Exception as e:
            print(f"扫描音频文件夹失败: {str(e)}")
            self.pet.change_state(self.pet.ERROR)

        return audio_list

    # 新增关联方法
    def preview_music(self, name):
        """试听按钮功能"""
        if name != "禁用":
            self.pet.play_music(name)
            QTimer.singleShot(5000, lambda: self.pet.media_player.stop())  # 5秒后自动停止

    def update_volume(self, value):
        """音量调节功能"""
        self.pet.media_player.setVolume(value)

    def switch_page(self, index):
        """切换设置页面"""
        self.stack.setCurrentIndex(index)
        buttons = [self.btn_size, self.btn_behavior, self.btn_appearance]
        for btn in buttons:
            btn.setChecked(btn == buttons[index])

    def update_size_preview(self, value):
        """实时更新尺寸预览"""
        self.size_value.setText(f"当前尺寸：{value}%")

    def apply_all_settings(self):
        """应用所有设置并保存"""
        self.apply_size_settings()

        # 保存音频配置
        try:
            audio_config = {
                "bgm": self.music_combo.currentText(),
                "volume": self.volume_slider.value()
            }
            with open(ControlPanel.AUDIO_CONFIG, 'w') as f:
                json.dump(audio_config, f)

            # 实时应用设置
            self.pet.play_music(audio_config['bgm'])
            self.pet.media_player.setVolume(audio_config['volume'])
        except Exception as e:
            print(f"音频配置保存失败: {str(e)}")

        # === 新增：保存主题配置 ===
        self.save_theme_config()

        # 保存其他配置
        self.save_config()
        self.close()

    def apply_size_settings(self):
        """仅更新尺寸和物理参数（不再自动保存）"""
        new_scale = self.size_slider.value() / 100
        if new_scale != self.pet.IMG_SCALE:
            self.pet.IMG_SCALE = new_scale
            scale_factor = self.pet.IMG_SCALE ** 0.7
            self.pet.PHYSICS['gravity'] = 1800 * scale_factor * 5
            # 更新UI但不自动保存
            self.pet.BASE_SIZE = QSize(
                int(3543 * self.pet.IMG_SCALE),
                int(4488 * self.pet.IMG_SCALE))
            self.pet.setFixedSize(self.pet.BASE_SIZE)
            self.pet.update_image("站立")

    def create_abnormality_settings(self):
        """异想体档案页（包含搜索功能）"""
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)

        # 搜索栏 - 更新placeholder文本
        self.search_box = QLineEdit()  # 改为成员变量以便访问
        self.search_box.setPlaceholderText("输入异想体编号或名称搜索...")
        self.search_box.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E0E0E0;
                border-radius: 15px;
                padding: 8px 15px;
                font-size: 14px;
            }
        """)

        # 连接搜索框的文本变化信号到过滤方法
        self.search_box.textChanged.connect(self.filter_abnormalities)

        # 创建祈愿池下拉框（如果尚未创建）
        if not hasattr(self, 'pool_combo'):
            self.pool_combo = QComboBox()
            # 添加祈愿池选项
            for pool_id, pool_info in self.pool_data.items():
                self.pool_combo.addItem(pool_info["name"], pool_id)

        # 设置下拉框样式
        self.pool_combo.setStyleSheet("""
            QComboBox {
                background: white;
                border: 1px solid #E0E0E0;
                border-radius: 15px;
                padding: 8px 15px;
                font-size: 14px;
                min-width: 180px;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)

        # 祈愿按钮
        wish_btn = QPushButton("✨ 祈愿")
        wish_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FFD700, stop:1 #FFA500);
                border-radius: 15px;
                padding: 8px 20px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #FFC800; }
        """)
        wish_btn.clicked.connect(self.do_wish)

        # 顶部布局（搜索框 + 祈愿池下拉框 + 祈愿按钮）
        header_layout = QHBoxLayout()
        header_layout.addWidget(self.search_box)
        header_layout.addWidget(self.pool_combo)
        header_layout.addWidget(wish_btn)
        layout.addLayout(header_layout)

        # 分割布局
        splitter = QSplitter(Qt.Horizontal)

        # 左侧列表
        self.abno_list = QListWidget()
        self.abno_list.addItems(self.abnormality_data.keys())
        self.abno_list.itemClicked.connect(self.update_abno_details)

        # ==== 关键修复：添加双击事件处理 ====
        self.abno_list.itemDoubleClicked.connect(self.handle_abno_double_click)

        self.abno_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                min-width: 120px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #EEE;
            }
            QListWidget::item:selected {
                background: #0078D420;
            }
        """)

        # 右侧详情
        detail_widget = QWidget()
        detail_layout = QVBoxLayout()

        self.abno_title = QLabel()
        self.abno_title.setStyleSheet("font: bold 18px; color: #1A1A1A;")

        self.abno_image = QLabel()
        self.abno_image.setFixedSize(200, 200)
        self.abno_image.setAlignment(Qt.AlignCenter)

        self.abno_desc = QTextBrowser()
        self.abno_desc.setStyleSheet("""
            QTextBrowser {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 12px;
                background: #FFFFFF;
                font-size: 14px;
                line-height: 1.6;
            }
        """)

        detail_layout.addWidget(self.abno_title)
        detail_layout.addWidget(self.abno_image)
        detail_layout.addWidget(self.abno_desc)
        detail_widget.setLayout(detail_layout)

        splitter.addWidget(self.abno_list)
        splitter.addWidget(detail_widget)
        splitter.setSizes([150, 400])

        layout.addWidget(splitter)
        page.setLayout(layout)

        # 默认显示第一个异想体的详情
        if self.abno_list.count() > 0:
            self.abno_list.setCurrentRow(0)
            self.update_abno_details(self.abno_list.currentItem())

        return page

    # 在 ControlPanel 类中添加以下方法
    def handle_abno_double_click(self, item):
        """处理异想体列表的双击事件"""
        if not item:
            return

        abno_id = item.text()

        # 双击星辉守护者打开问答对话框
        if abno_id == "O-02-88":
            self.show_questions_dialog(abno_id)

        # 双击仓皇大帝打开添加异想体对话框
        elif abno_id == "O-07-99":
            self.show_add_abnormality_dialog()

    def filter_abnormalities(self, text):
        """根据搜索文本过滤异想体列表"""
        text = text.lower().strip()

        # 清空列表并重新添加匹配项
        self.abno_list.clear()

        for abno_id, data in self.abnormality_data.items():
            # 检查编号或名称是否匹配
            if (text in abno_id.lower() or
                    text in data.get('name', '').lower() or
                    text in data.get('risk_level', '').lower()):
                self.abno_list.addItem(abno_id)

        # 默认选中第一个匹配项
        if self.abno_list.count() > 0:
            self.abno_list.setCurrentRow(0)
            self.update_abno_details(self.abno_list.currentItem())

    def load_constellations(self):
        config_path = os.path.join(os.getenv('LOCALAPPDATA'), 'StarPet')
        try:
            if not os.path.exists(config_path):
                os.makedirs(config_path)

            data_file = os.path.join(config_path, 'constellations.json')
            if os.path.exists(data_file):
                with open(data_file, 'r', encoding='utf-8') as f:
                    self.constellation_data = json.load(f)
        except Exception as e:
            print(f"加载命之座数据失败: {str(e)}")

    def save_constellations(self):
        config_path = os.path.join(os.getenv('LOCALAPPDATA'), 'StarPet')
        try:
            data_file = os.path.join(config_path, 'constellations.json')
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(self.constellation_data, f)
        except Exception as e:
            print(f"保存命之座数据失败: {str(e)}")

    def load_pity_data(self):
        config_path = os.path.join(os.getenv('LOCALAPPDATA'), 'StarPet')
        try:
            data_file = os.path.join(config_path, 'wish_pity.json')
            if os.path.exists(data_file):
                with open(data_file, 'r') as f:
                    self.wish_counter = json.load(f)
        except Exception as e:
            print(f"加载保底数据失败: {str(e)}")

    def save_pity_data(self):
        config_path = os.path.join(os.getenv('LOCALAPPDATA'), 'StarPet')
        try:
            data_file = os.path.join(config_path, 'wish_pity.json')
            with open(data_file, 'w') as f:
                json.dump(self.wish_counter, f)
        except Exception as e:
            print(f"保存保底数据失败: {str(e)}")

    # 添加祈愿逻辑
    def do_wish(self):
        """完整的概率处理系统（含保底机制）"""
        current_pool = list(self.pool_data.keys())[
            self.pool_combo.currentIndex() if self.pool_combo.currentIndex() != -1 else 0]
        pool_config = self.pool_data[current_pool]

        # 更新保底计数器
        self.wish_counter['4star_pity'] += 1
        self.wish_counter['5star_pity'] += 1

        # 五星保底机制
        if self.wish_counter['5star_pity'] >= 90:
            rarity = 5
            self.wish_counter['5star_pity'] = 0
        else:
            # 动态概率计算
            base_5star_rate = pool_config["base_5star_rate"]
            increased_rate = max(0, (self.wish_counter['5star_pity'] - 73)) * 0.06
            current_5star_rate = base_5star_rate + increased_rate

            # 四星保底处理
            if self.wish_counter['4star_pity'] >= 10:
                # 四星保底时，四星概率=1-五星概率
                four_star_rate = 1 - current_5star_rate
                self.wish_counter['4star_pity'] = 0
            else:
                four_star_rate = 0.051

            # 确保概率总和不超过1
            current_5star_rate = min(current_5star_rate, 1 - four_star_rate)
            three_star_rate = 1 - four_star_rate - current_5star_rate

            # 执行概率选择
            r = random.random()
            if r < current_5star_rate:
                rarity = 5
                self.wish_counter['5star_pity'] = 0
            elif r < (current_5star_rate + four_star_rate):
                rarity = 4
                self.wish_counter['4star_pity'] = 0
            else:
                rarity = 3

        # 保存保底数据
        self.save_pity_data()

        # ========== 修复的核心部分：确保抽到当前卡池的专属异想体 ==========
        candidates = []
        selected_id = None

        if rarity == 5:
            # 从当前卡池的五星异想体中筛选候选
            candidates = [
                k for k in pool_config["rate_up"]
                if k in self.abnormality_data and
                   self.abnormality_data[k].get('risk_level') == "ALEPH"
            ]

            # 如果没有符合条件的候选，则使用当前卡池ID作为默认
            if not candidates:
                candidates = [current_pool]

            # 从候选池中按权重选择
            weights = [pool_config["5star_weights"].get(k, 0.1) for k in candidates]
            selected_id = random.choices(candidates, weights=weights, k=1)[0]

        elif rarity == 4:
            # 从所有WAW级异想体中筛选候选（优先当前卡池）
            pool_candidates = [
                k for k, v in self.abnormality_data.items()
                if v.get('risk_level') == "WAW" and k in pool_config["rate_up"]
            ]

            # 如果没有当前卡池的WAW级，则使用其他WAW级
            if not pool_candidates:
                pool_candidates = [
                    k for k, v in self.abnormality_data.items()
                    if v.get('risk_level') == "WAW"
                ]

            # 如果还没有候选，则从当前卡池中选择
            if not pool_candidates:
                selected_id = random.choice(pool_config["rate_up"])
            else:
                selected_id = random.choice(pool_candidates)

        else:  # 三星处理
            # 从所有HE/TETH级异想体中筛选候选（优先当前卡池）
            pool_candidates = [
                k for k, v in self.abnormality_data.items()
                if v.get('risk_level') in ("HE", "TETH") and k in pool_config["rate_up"]
            ]

            # 如果没有当前卡池的，则使用其他HE/TETH级
            if not pool_candidates:
                pool_candidates = [
                    k for k, v in self.abnormality_data.items()
                    if v.get('risk_level') in ("HE", "TETH")
                ]

            # 如果还没有候选，则从当前卡池中选择
            if not pool_candidates:
                selected_id = random.choice(pool_config["rate_up"])
            else:
                selected_id = random.choice(pool_candidates)
        # ========== 修复结束 ==========

        # 命座解锁逻辑
        if rarity == 5 and self.abnormality_data[selected_id].get('can_constellation', False):
            current_level = self.constellation_data.get(selected_id, 0)
            if current_level < 6:
                self.constellation_data[selected_id] = current_level + 1
                self.save_constellations()
                self.show_constellation_effect(selected_id)

        # 显示结果
        self.show_wish_result(selected_id, rarity)

        # 首次五星成就解锁
        if rarity == 5 and not self.achievement_data.get("first_5star", False):
            self.achievement_data["first_5star"] = 1
            self.save_achievements()
            self.show_achievement_popup("first_5star")

    def show_constellation_effect(self, abno_id):
        """命座解锁特效"""
        # 获取当前命之座等级
        constellation = self.constellation_data.get(abno_id, 0)  # 获取命之座等级

        # 检查是否是仓皇大帝且达到6命
        if abno_id == "O-07-99" and constellation >= 6:  # 使用 constellation 替换 level
            # 升级为ALEPH级
            self.abnormality_data[abno_id].update({
                "name": self.abnormality_data[abno_id]["aleph_data"]["name"],
                "risk_level": "ALEPH",
                "description": self.abnormality_data[abno_id]["aleph_data"]["description"],
                "quote": self.abnormality_data[abno_id]["aleph_data"]["quote"]
            })
            # 更新图片为ALEPH形态
            self.abnormality_data[abno_id]["img"] = "仓皇大帝.png"
        try:
            # 创建全屏遮罩
            overlay = QWidget()
            overlay.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
            overlay.setAttribute(Qt.WA_TranslucentBackground)
            overlay.setGeometry(QDesktopWidget().screenGeometry())

            # 星轨动画
            effect_label = QLabel(overlay)
            movie = QMovie("images/命座解锁.gif")
            effect_label.setMovie(movie)
            movie.start()

            # 居中显示
            effect_label.adjustSize()
            effect_label.move(
                (overlay.width() - effect_label.width()) // 2,
                (overlay.height() - effect_label.height()) // 2
            )

            # 渐显动画
            overlay.setWindowOpacity(0)
            overlay.show()

            anim = QPropertyAnimation(overlay, b"windowOpacity")
            anim.setDuration(1200)
            anim.setStartValue(0)
            anim.setEndValue(1)
            anim.setEasingCurve(QEasingCurve.OutCubic)

            # 自动关闭
            QTimer.singleShot(2500, lambda: (
                anim.setDirection(QPropertyAnimation.Backward),
                anim.start(),
                QTimer.singleShot(1200, overlay.deleteLater)
            ))
            anim.start()

            # === 新增关键修复 ===
            # 确保列表有选中项
            if not self.abno_list.currentItem():
                if self.abno_list.count() > 0:
                    self.abno_list.setCurrentRow(0)  # 默认选中第一项

            # 更新档案显示（带空值检查）
            current_item = self.abno_list.currentItem()
            if current_item:
                self.update_abno_details(current_item)

        except Exception as e:
            print(f"命座特效异常: {str(e)}")

    def show_achievement_popup(self, achievement_key):
        try:
            data = self.achievements[achievement_key]
            popup = QLabel(f"★ 成就解锁 ★\n{data['name']}\n{data['desc']}")
            popup.setAlignment(Qt.AlignCenter)
            popup.setStyleSheet("""
                background: rgba(255,215,0,0.9);
                border: 2px solid gold;
                border-radius: 15px;
                padding: 20px;
                font: bold 16px '微软雅黑';
                color: #2C3E50;
            """)
            popup.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
            popup.adjustSize()

            # 动画效果
            pos = QApplication.desktop().availableGeometry().center() - popup.rect().center()
            popup.move(pos)
            popup.show()

            QTimer.singleShot(3000, popup.deleteLater)
        except Exception as e:
            print(f"成就提示异常: {str(e)}")

    # 添加结果显示方法
    def show_wish_result(self, abno_id, rarity):
        """透明居中祈愿效果（修复版）"""
        try:
            # 获取程序根目录
            base_dir = os.path.dirname(os.path.abspath(__file__))

            # 创建全屏透明窗口
            overlay = QWidget()
            overlay.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
            overlay.setAttribute(Qt.WA_TranslucentBackground)
            overlay.setGeometry(QDesktopWidget().screenGeometry())

            # 调试输出稀有度
            # print(f"[DEBUG] 当前稀有度: {rarity}星")

            # 构建图片路径（修正路径获取方式）
            star_levels = ["三星", "四星", "五星"]
            target_star = star_levels[rarity - 3]  # rarity=3对应索引0

            img_paths = [
                os.path.join(base_dir, "images", f"{abno_id}_{target_star}.png"),  # 异想体专属
                os.path.join(base_dir, "images", f"{target_star}.png"),  # 通用星级
                os.path.join(base_dir, "images", "三星.png")  # 保底图片
            ]

            # 加载图片流程（添加调试信息）
            pixmap = QPixmap()
            for path in img_paths:
                print(f"[DEBUG] 尝试加载: {path}")
                if os.path.exists(path):
                    print(f"[SUCCESS] 找到图片: {path}")
                    pixmap = QPixmap(path)
                    break

            # 设置图片显示（保持原始比例）
            card = QLabel(overlay)
            card.setAlignment(Qt.AlignCenter)

            if not pixmap.isNull():
                # 动态缩放（最大占屏80%）
                max_size = QDesktopWidget().screenGeometry().size() * 0.8
                scaled_pixmap = pixmap.scaled(
                    max_size,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                card.setPixmap(scaled_pixmap)
            else:
                # 文字回退（添加抗锯齿及卡池信息）
                card.setText(f"{'★' * rarity}\n{abno_id}\n({self.pool_combo.currentText()})")  # 新增卡池显示
                card.setFont(QFont("微软雅黑", 100, QFont.Bold))
                color = "#FFD700" if rarity == 5 else "#9B59B6" if rarity == 4 else "#3498DB"
                card.setStyleSheet(f"color: {color}; background: transparent;")

            # 居中定位
            card.adjustSize()
            card.move(
                (overlay.width() - card.width()) // 2,
                (overlay.height() - card.height()) // 2
            )

            # 动画效果（优化时间曲线）
            overlay.setWindowOpacity(0)
            overlay.show()

            fade_anim = QPropertyAnimation(overlay, b"windowOpacity")
            fade_anim.setDuration(1500)
            fade_anim.setStartValue(0)
            fade_anim.setEndValue(0.98)
            fade_anim.setEasingCurve(QEasingCurve.OutExpo)

            # 自动关闭流程
            QTimer.singleShot(3000, lambda: (
                fade_anim.setDirection(QPropertyAnimation.Backward),
                fade_anim.start(),
                QTimer.singleShot(1500, overlay.deleteLater)
            ))

            fade_anim.start()

        except Exception as e:
            print(f"祈愿异常: {str(e)}")
            import traceback
            traceback.print_exc()

    # 在 ControlPanel 类的 update_abno_details 方法中
    def update_abno_details(self, item):
        """更新异想体详情（高清图片加载版）"""
        # === 空值检查 ===
        if not item:
            return

        # 获取异想体ID和数据
        abno_id = item.text()
        self.current_abno_id = abno_id
        data = self.abnormality_data.get(abno_id, {})

        # === 特殊处理：仓皇大帝6命形态 ===
        if abno_id == "O-07-99":
            constellation = self.constellation_data.get(abno_id, 0)
            if constellation >= 6:  # 6命时使用ALEPH形态数据
                aleph_data = data.get("aleph_data", {})
                data = {
                    **data,  # 保留基础数据
                    "name": aleph_data.get("name", data.get("name", "未知")),
                    "risk_level": "ALEPH",
                    "description": aleph_data.get("description", data.get("description", "")),
                    "quote": aleph_data.get("quote", data.get("quote", "")),
                    "img": aleph_data.get("img", data.get("img", "default.png"))
                }
                if self.abno_desc.mouseDoubleClickEvent:
                    self.abno_desc.mouseDoubleClickEvent = lambda event: self.show_add_abnormality_dialog()
            else:
                # 非6命状态也可以触发
                self.abno_desc.mouseDoubleClickEvent = lambda event: self.show_add_abnormality_dialog()
        else:
            # 其他异想体正常处理
            self.abno_desc.mouseDoubleClickEvent = None

        # === 根据危险等级设置颜色 ===
        risk_level = data.get('risk_level', '未知')
        risk_color = {
            "ALEPH": "#E74C3C",  # 红色
            "WAW": "#9B59B6",  # 紫色
            "HE": "#FFEB3B",  # 黄色
            "TETH": "#3498DB",  # 蓝色
            "ZAYIN": "#2ECC71"  # 绿色
        }.get(risk_level, "#95A5A6")  # 默认灰色

        # === 图片加载（带抗锯齿和缓存）===
        img_name = data.get('img', 'default.png')
        img_path = os.path.join("images", img_name)

        # 检查缓存中是否有图片
        if img_path in self.image_cache:
            pixmap = self.image_cache[img_path]
        else:
            # 尝试加载图片
            if os.path.exists(img_path):
                pixmap = QPixmap(img_path)
                if not pixmap.isNull():
                    # 添加到缓存
                    self.image_cache[img_path] = pixmap
                else:
                    # 加载失败，使用占位符
                    self.abno_image.setText("❌ 图片加载失败")
                    self.abno_image.setStyleSheet("font-size: 12px; color: #E74C3C;")
            else:
                # 文件不存在，使用占位符
                self.abno_image.setText("❌ 图片文件缺失")
                self.abno_image.setStyleSheet("font-size: 12px; color: #E74C3C;")
                pixmap = QPixmap()  # 创建空图片

        # === 高质量图片缩放 ===
        if not pixmap.isNull():
            # 高质量抗锯齿缩放
            scaled_pixmap = pixmap.scaled(
                self.abno_image.width(),
                self.abno_image.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation  # 关键：启用抗锯齿
            )
            self.abno_image.setPixmap(scaled_pixmap)

        # === 根据当前主题设置文本颜色 ===
        if self.current_theme == "dark":
            # 黑夜模式：所有文本为白色，背景深灰色
            text_color = "#FFFFFF"  # 白色
            bg_color = "#2D2D2D"  # 深灰色背景
            border_color = "#555555"  # 边框颜色
            quote_bg = "#3A3A3A"  # 引言背景
        else:
            # 白昼模式：保持原样
            text_color = "#2C3E50"  # 深蓝色
            bg_color = "#FFFFFF"  # 白色背景
            border_color = "#E0E0E0"  # 浅灰色边框
            quote_bg = "#F5F5F5"  # 引言背景

        # === 构建描述文本 ===
        html = f"""
            <div style='color: {risk_color}; font-size: 16px; margin-bottom: 10px;'>
                ▶ 危险等级：{risk_level}
            </div>
            <div style='color: {text_color}; margin-bottom: 15px;'>
                {data.get('description', '暂无数据')}
            </div>
            <div style='border-left: 3px solid #0078D4; padding-left: 10px; 
                        color: {text_color}; font-style: italic;
                        background: {quote_bg}; padding: 8px; border-radius: 4px;'>
                {data.get('quote', '')}
            </div>
        """

        # === 添加命之座信息 ===
        constellation = self.constellation_data.get(abno_id, 0)
        if data.get('can_constellation', False) and constellation > 0:
            cons_html = f"""
                <div style='margin-top:15px; border-top:1px solid {border_color}; padding-top:10px;'>
                    <span style='color:#FFD700;'>✦ 命之座等级：{constellation}</span>
                    <div style='font-size:12px; color:{text_color};'>
                        {self.get_constellation_effect(abno_id, constellation)}
                    </div>
                </div>
            """
            html += cons_html

        # === 设置整体样式 ===
        self.abno_desc.setStyleSheet(f"""
            QTextBrowser {{
                background: {bg_color};
                border: 1px solid {border_color};
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                line-height: 1.6;
                color: {text_color};
            }}
        """)

        # === 设置标题 ===
        self.abno_title.setText(f"{abno_id} - {data.get('name', '未知')}")
        self.abno_title.setStyleSheet(f"font: bold 18px; color: {text_color};")

        # === 设置HTML内容 ===
        self.abno_desc.setHtml(html)

    def show_add_abnormality_dialog(self):
        """显示添加异想体的对话框（完整适配黑夜模式）"""
        dialog = QDialog(self)
        dialog.setWindowTitle("从井中提取异想体")
        dialog.setFixedSize(850, 700)

        # 根据当前主题动态设置样式
        if self.current_theme == "dark":
            dialog_style = """
                QDialog {
                    background: #2D2D2D;
                    border-radius: 8px;
                    font-family: 'Segoe UI Variable';
                }
                QLabel {
                    font-size: 14px;
                    color: #E0E0E0;
                }
                QLineEdit, QTextEdit, QComboBox, QDoubleSpinBox {
                    background: #3A3A3A;
                    color: #FFFFFF;
                    border: 1px solid #555555;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 14px;
                }
                QLineEdit:focus, QTextEdit:focus {
                    border-color: #1E90FF;
                }
                QPushButton {
                    background-color: #1E90FF;
                    color: white;
                    border-radius: 6px;
                    padding: 8px 16px;
                    min-width: 80px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #187BCD;
                }
                QPushButton:pressed {
                    background-color: #1560BD;
                }
                QCheckBox {
                    color: #E0E0E0;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                    border-radius: 4px;
                    border: 1px solid #555555;
                    background: #3A3A3A;
                }
                QCheckBox::indicator:checked {
                    background-color: #1E90FF;
                    border-color: #1E90FF;
                }
                QGroupBox {
                    border: 1px solid #555555;
                    border-radius: 8px;
                    margin-top: 16px;
                    padding-top: 24px;
                    font-weight: bold;
                    color: #E0E0E0;
                }
                QGroupBox::title {
                    color: #E0E0E0;
                    subcontrol-origin: margin;
                    left: 10px;
                }
            """
        else:
            dialog_style = """
                QDialog {
                    background: white;
                    border-radius: 8px;
                    font-family: 'Segoe UI Variable';
                }
                QLabel {
                    font-size: 14px;
                    color: #1A1A1A;
                }
                QLineEdit, QTextEdit, QComboBox, QDoubleSpinBox {
                    border: 1px solid #E0E0E0;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 14px;
                }
                QLineEdit:focus, QTextEdit:focus {
                    border-color: #0078D4;
                }
                QPushButton {
                    background-color: #0078D4;
                    color: white;
                    border-radius: 6px;
                    padding: 8px 16px;
                    min-width: 80px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #106EBE;
                }
                QPushButton:pressed {
                    background-color: #005A9E;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                    border-radius: 4px;
                    border: 1px solid #E0E0E0;
                }
                QCheckBox::indicator:checked {
                    background-color: #0078D4;
                    border-color: #0078D4;
                }
                QGroupBox {
                    border: 1px solid #E0E0E0;
                    border-radius: 8px;
                    margin-top: 16px;
                    padding-top: 24px;
                    font-weight: bold;
                }
            """

        dialog.setStyleSheet(dialog_style)

        # 创建选项卡组件
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
                    QTabWidget::pane {
                        border: none;
                    }
                    QTabBar::tab {
                        padding: 8px 16px;
                        border-radius: 4px;
                        margin-right: 4px;
                    }
                    QTabBar::tab:selected {
                        background: #0078D4;
                        color: white;
                    }
                """)

        # 添加两个选项卡
        tab_widget.addTab(self.create_add_abnormality_tab(dialog), "添加异想体")
        tab_widget.addTab(self.create_manage_abnormalities_tab(dialog), "管理异想体")

        # 主布局
        main_layout = QVBoxLayout(dialog)
        main_layout.addWidget(tab_widget)
        dialog.show()

    def create_add_abnormality_tab(self, dialog):
        """创建添加异想体的表单页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)

        # 表单布局（与原有表单相同）
        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        # 异想体ID
        abno_id_label = QLabel("异想体ID:")
        self.abno_id_edit = QLineEdit()
        self.abno_id_edit.setPlaceholderText("例如: C-01-01")
        form_layout.addRow(abno_id_label, self.abno_id_edit)

        # 名称
        abno_name_label = QLabel("名称:")
        self.abno_name_edit = QLineEdit()
        self.abno_name_edit.setPlaceholderText("异想体名称")
        form_layout.addRow(abno_name_label, self.abno_name_edit)

        # 危险等级
        abno_risk_label = QLabel("危险等级:")
        self.abno_risk_combo = QComboBox()
        self.abno_risk_combo.addItems(["ALEPH", "WAW", "HE", "TETH", "ZAYIN"])
        form_layout.addRow(abno_risk_label, self.abno_risk_combo)

        # 描述
        abno_desc_label = QLabel("描述:")
        self.abno_desc_edit = QTextEdit()
        self.abno_desc_edit.setPlaceholderText("详细描述异想体的特性...")
        self.abno_desc_edit.setFixedHeight(100)
        form_layout.addRow(abno_desc_label, self.abno_desc_edit)

        # 引言
        abno_quote_label = QLabel("引言:")
        self.abno_quote_edit = QLineEdit()
        self.abno_quote_edit.setPlaceholderText("异想体的名言")
        form_layout.addRow(abno_quote_label, self.abno_quote_edit)

        # 图片选择部分
        image_group = QGroupBox("图片设置")
        image_layout = QFormLayout(image_group)

        # 是否可定轨
        self.abno_target_check = QCheckBox("允许在祈愿池中定轨")
        self.abno_target_check.setChecked(True)
        image_layout.addRow(self.abno_target_check)

        # 卡池权重
        abno_weight_label = QLabel("卡池权重:")
        self.abno_weight_spin = QDoubleSpinBox()
        self.abno_weight_spin.setRange(0.1, 10.0)
        self.abno_weight_spin.setValue(1.0)
        self.abno_weight_spin.setSingleStep(0.1)
        image_layout.addRow(abno_weight_label, self.abno_weight_spin)

        # 图片选择
        self.abno_image_path = ""
        self.abno_image_label = QLabel("未选择图片")
        self.abno_image_label.setFixedSize(150, 150)
        self.abno_image_label.setAlignment(Qt.AlignCenter)
        self.abno_image_label.setStyleSheet("""
            QLabel {
                border: 1px dashed #aaa;
                border-radius: 8px;
            }
        """)

        image_btn = QPushButton("选择图片")
        image_btn.clicked.connect(self.select_abnormality_image)

        image_btn_layout = QHBoxLayout()
        image_btn_layout.addStretch()
        image_btn_layout.addWidget(image_btn)

        image_layout.addRow(QLabel("图片预览:"), self.abno_image_label)
        image_layout.addRow(image_btn_layout)

        # 按钮区域
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(lambda: self.save_custom_abnormality(dialog))

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dialog.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)

        # 组合布局
        layout.addLayout(form_layout)
        layout.addWidget(image_group)
        layout.addLayout(btn_layout)

        return tab

    def create_manage_abnormalities_tab(self, dialog):
        """创建管理异想体的表格页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)

        # 搜索框
        search_layout = QHBoxLayout()
        search_edit = QLineEdit()
        search_edit.setPlaceholderText("搜索异想体...")
        search_edit.textChanged.connect(self.filter_abnormalities_table)
        search_layout.addWidget(search_edit)

        # 刷新按钮
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.load_abnormalities_table)
        search_layout.addWidget(refresh_btn)

        layout.addLayout(search_layout)

        # 创建表格
        self.abno_table = QTableWidget()
        self.abno_table.setColumnCount(6)
        self.abno_table.setHorizontalHeaderLabels(["ID", "名称", "危险等级", "可定轨", "权重", "操作"])
        self.abno_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.abno_table.verticalHeader().setVisible(False)
        self.abno_table.setEditTriggers(QTableWidget.NoEditTriggers)

        # 加载表格数据
        self.load_abnormalities_table()

        layout.addWidget(self.abno_table)
        return tab

    def load_abnormalities_table(self):
        """加载自定义异想体数据到表格"""
        # 确保异常管理器已初始化
        if not hasattr(self, 'abnormality_manager'):
            self.abnormality_manager = AbnormalityManager(self)

        # 获取自定义异想体列表
        custom_abnos = self.abnormality_manager.get_custom_abnormalities()

        # 清除旧数据
        self.abno_table.setRowCount(0)

        # 填充表格
        for abno_id, data in custom_abnos.items():
            row = self.abno_table.rowCount()
            self.abno_table.insertRow(row)

            # ID
            id_item = QTableWidgetItem(abno_id)
            self.abno_table.setItem(row, 0, id_item)

            # 名称
            name_item = QTableWidgetItem(data.get('name', '未知'))
            self.abno_table.setItem(row, 1, name_item)

            # 危险等级
            risk_item = QTableWidgetItem(data.get('risk_level', '未知'))
            self.abno_table.setItem(row, 2, risk_item)

            # 可定轨
            target_item = QTableWidgetItem("是" if data.get('can_target', True) else "否")
            self.abno_table.setItem(row, 3, target_item)

            # 权重
            weight_item = QTableWidgetItem(str(data.get('weight', 1.0)))
            self.abno_table.setItem(row, 4, weight_item)

            # 操作按钮 - 添加间距
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setSpacing(8)  # 添加按钮间距

            edit_btn = QPushButton("编辑")
            edit_btn.setFixedSize(60, 30)
            edit_btn.clicked.connect(lambda _, id=abno_id: self.edit_custom_abnormality(id))

            delete_btn = QPushButton("删除")
            delete_btn.setFixedSize(60, 30)
            delete_btn.setStyleSheet("background-color: #FF6B6B; color: white;")
            delete_btn.clicked.connect(lambda _, id=abno_id: self.delete_custom_abnormality(id))

            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            btn_layout.setContentsMargins(0, 0, 0, 0)

            self.abno_table.setCellWidget(row, 5, btn_widget)

    def filter_abnormalities_table(self, text):
        """过滤表格中的异想体"""
        text = text.lower()
        for row in range(self.abno_table.rowCount()):
            should_show = False
            for col in range(self.abno_table.columnCount() - 1):  # 排除操作列
                item = self.abno_table.item(row, col)
                if item and text in item.text().lower():
                    should_show = True
                    break
            self.abno_table.setRowHidden(row, not should_show)

    def edit_custom_abnormality(self, abno_id):
        """编辑自定义异想体"""
        # 确保异常管理器已初始化
        if not hasattr(self, 'abnormality_manager'):
            self.abnormality_manager = AbnormalityManager(self)

        # 获取异想体数据
        data = self.abnormality_manager.get_abnormality(abno_id)
        if not data:
            QMessageBox.warning(self, "编辑失败", "找不到指定的异想体数据！")
            return

        # 填充表单
        self.abno_id_edit.setText(abno_id)
        self.abno_name_edit.setText(data.get('name', ''))
        self.abno_risk_combo.setCurrentText(data.get('risk_level', 'ALEPH'))
        self.abno_desc_edit.setText(data.get('description', ''))
        self.abno_quote_edit.setText(data.get('quote', ''))
        self.abno_target_check.setChecked(data.get('can_target', True))
        self.abno_weight_spin.setValue(data.get('weight', 1.0))

        # 加载图片预览
        img_name = data.get('img', '')
        if img_name:
            img_path = os.path.join("images", img_name)
            if os.path.exists(img_path):
                pixmap = QPixmap(img_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.abno_image_label.setPixmap(scaled_pixmap)
                    self.abno_image_path = img_path
                    return

        # 清除图片预览
        self.abno_image_label.clear()
        self.abno_image_label.setText("未选择图片")
        self.abno_image_path = ""

    def delete_custom_abnormality(self, abno_id):
        """删除自定义异想体"""
        # 确认对话框
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除异想体 '{abno_id}' 吗？此操作不可恢复！",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.No:
            return

        # 确保异常管理器已初始化
        if not hasattr(self, 'abnormality_manager'):
            self.abnormality_manager = AbnormalityManager(self)

        # 删除异想体
        if self.abnormality_manager.delete_custom_abnormality(abno_id):
            # 从主数据中移除
            if abno_id in self.abnormality_data:
                del self.abnormality_data[abno_id]

            # 刷新表格
            self.load_abnormalities_table()
            QMessageBox.information(self, "删除成功", f"已成功删除异想体 '{abno_id}'")
        else:
            QMessageBox.warning(self, "删除失败", "删除异想体失败，请检查日志！")

    def save_custom_abnormality(self, dialog):
        """保存自定义异想体（添加或更新）"""
        abno_id = self.abno_id_edit.text().strip()
        name = self.abno_name_edit.text().strip()

        # 验证必填字段
        if not abno_id or not name:
            QMessageBox.warning(self, "输入错误", "异想体ID和名称不能为空！")
            return

        # 创建异想体数据对象
        abno_data = {
            "name": name,
            "risk_level": self.abno_risk_combo.currentText(),
            "description": self.abno_desc_edit.toPlainText().strip(),
            "quote": self.abno_quote_edit.text().strip(),
            "can_target": self.abno_target_check.isChecked(),
            "weight": self.abno_weight_spin.value(),
            "img": os.path.basename(self.abno_image_path) if self.abno_image_path else ""
        }

        # 确保异常管理器已初始化
        if not hasattr(self, 'abnormality_manager'):
            self.abnormality_manager = AbnormalityManager(self)

        # 添加或更新异想体
        is_update = self.abnormality_manager.is_custom_abnormality(abno_id)

        if is_update:
            action = "更新"
            success = self.abnormality_manager.update_custom_abnormality(abno_id, abno_data)
        else:
            action = "添加"
            success = self.abnormality_manager.add_custom_abnormality(abno_id, abno_data)

        if success:
            # 刷新主数据
            self.abnormality_data[abno_id] = abno_data

            # 将图片复制到images目录（如果是新图片）
            if self.abno_image_path:
                try:
                    target_dir = "images"
                    if not os.path.exists(target_dir):
                        os.makedirs(target_dir)

                    target_path = os.path.join(target_dir, os.path.basename(self.abno_image_path))

                    # 如果是新文件或不同文件才复制
                    if not os.path.exists(target_path) or not self.abno_image_path == target_path:
                        shutil.copyfile(self.abno_image_path, target_path)
                except Exception as e:
                    QMessageBox.warning(self, "图片保存失败", f"无法保存图片: {str(e)}")

            # 更新异想体列表
            self.filter_abnormalities(self.search_box.text())
            QMessageBox.information(self, "保存成功", f"已成功{action}异想体: {name}")
            dialog.accept()
        else:
            QMessageBox.warning(self, "保存失败", f"{action}异想体数据失败，请检查配置！")

    def select_abnormality_image(self):
        """选择异想体图片"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择异想体图片", "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp)"
        )

        if file_path:
            self.abno_image_path = file_path

            # 加载并预览图片
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # 缩放图片以适应预览区域
                scaled_pixmap = pixmap.scaled(
                    150, 150,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.abno_image_label.setPixmap(scaled_pixmap)
                self.abno_image_label.setText("")
            else:
                self.abno_image_label.setText("图片加载失败")
                self.abno_image_label.setPixmap(QPixmap())

    def save_custom_abnormality(self, dialog):
        """保存自定义异想体（修复卡死问题）"""
        abno_id = self.abno_id_edit.text().strip()
        name = self.abno_name_edit.text().strip()

        # 验证必填字段
        if not abno_id or not name:
            QMessageBox.warning(self, "输入错误", "异想体ID和名称不能为空！")
            return

        # 创建异想体数据对象（修复数据格式）
        abno_data = {
            "name": name,
            "risk_level": self.abno_risk_combo.currentText(),
            "description": self.abno_desc_edit.toPlainText().strip(),
            "quote": self.abno_quote_edit.text().strip(),
            "can_target": self.abno_target_check.isChecked(),
            "weight": self.abno_weight_spin.value(),
            "img": os.path.basename(self.abno_image_path) if self.abno_image_path else ""
        }

        # 确保异常管理器已初始化
        if not hasattr(self, 'abnormality_manager'):
            self.abnormality_manager = AbnormalityManager(self)

        # 添加或更新异想体
        is_update = self.abnormality_manager.is_custom_abnormality(abno_id)

        if is_update:
            action = "更新"
            success = self.abnormality_manager.update_custom_abnormality(abno_id, abno_data)
        else:
            action = "添加"
            success = self.abnormality_manager.add_custom_abnormality(abno_id, abno_data)

        if success:
            # 刷新主数据
            self.abnormality_data[abno_id] = abno_data

            # 将图片复制到images目录（修复图片保存逻辑）
            if self.abno_image_path:
                try:
                    target_dir = "images"
                    if not os.path.exists(target_dir):
                        os.makedirs(target_dir)

                    target_path = os.path.join(target_dir, os.path.basename(self.abno_image_path))

                    # 仅当文件不存在时才复制
                    if not os.path.exists(target_path):
                        shutil.copyfile(self.abno_image_path, target_path)
                except Exception as e:
                    QMessageBox.warning(self, "图片保存失败", f"无法保存图片: {str(e)}")
                    print(f"图片保存错误: {str(e)}")

            # 更新异想体列表
            self.filter_abnormalities(self.search_box.text())
            QMessageBox.information(self, "保存成功", f"已成功{action}异想体: {name}")

            # 关键修复：关闭对话框
            dialog.accept()
        else:
            QMessageBox.warning(self, "保存失败", f"{action}异想体数据失败，请检查配置！")

    # 添加命之座效果描述方法
    def get_constellation_effect(self, abno_id, level):
        effects = {
            0: "尚未解锁命之座能力",
            1: "提升物理互动灵敏度20%",
            2: "解锁特殊进食动画",
            3: "星辉邻域容量扩展50%",
            4: "获得金色边框特效",
            5: "解锁隐藏对话选项",
            6: "激活终极星辉形态"
        }
        base_effect = effects.get(min(level, 6), "")

        if abno_id == "O-02-88":  # 星辉守护者特殊效果
            return f"星辉守护者专属：{base_effect}"
        elif abno_id == "O-07-99":  # 仓皇大帝
            if level == 6:
                return "无需相信时间，我将为你指路"  # 专属描述
            return f"仓皇大帝：{base_effect}"
        return base_effect

    def load_achievements(self):
        config_path = os.path.join(os.getenv('LOCALAPPDATA'), 'StarPet')
        # 定义所有可能的成就键（包含ask_star）
        all_keys = ["pioneer", "writer", "first_5star", "first_birthday", "ask_star"]

        # 初始化默认值
        self.achievement_data = {key: 0 for key in all_keys}

        try:
            data_file = os.path.join(config_path, 'achievements.json')
            if os.path.exists(data_file):
                with open(data_file, 'r') as f:
                    loaded_data = json.load(f)
                    # 合并所有键（包括JSON中可能存在的其他键）
                    for key in all_keys:
                        if key in loaded_data:
                            self.achievement_data[key] = loaded_data[key]
                    # 同时保留JSON中可能存在的其他成就
                    for key, value in loaded_data.items():
                        if key not in self.achievement_data:
                            self.achievement_data[key] = value
        except Exception as e:
            print(f"成就加载失败: {str(e)}")

    def save_achievements(self):
        config_path = os.path.join(os.getenv('LOCALAPPDATA'), 'StarPet')
        try:
            data_file = os.path.join(config_path, 'achievements.json')
            with open(data_file, 'w') as f:
                json.dump(self.achievement_data, f)
        except Exception as e:
            print(f"成就保存失败: {str(e)}")

    def show_questions_dialog(self, abno_id):
        """显示问答对话框（优化黑夜模式配色）"""
        # 检查并解锁"问星辉"成就
        if not self.achievement_data.get("ask_star", 0):
            self.achievement_data["ask_star"] = 1
            self.save_achievements()
            self.show_achievement_popup("ask_star")
            # 刷新成就列表以显示新解锁的成就
            self.update_achievements()

        # 创建对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("问星辉")
        dialog.setWindowIcon(self.windowIcon())
        dialog.setFixedSize(500, 400)

        # ========== 根据主题应用整体样式 ==========
        if self.current_theme == "dark":
            # 黑夜模式样式
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #2D2D2D;
                    border-radius: 8px;
                }
                QLabel {
                    color: #FFFFFF;  /* 白色文本 */
                }
                QFrame {
                    background-color: #555555;  /* 分隔线颜色 */
                }
                QScrollArea {
                    background: transparent;
                    border: none;
                }
                QWidget#scrollContent {
                    background: transparent;
                }
            """)

        # 主布局
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)

        # 标题 - 优化黑夜模式下的颜色
        title = QLabel("星辉知识问答")
        if self.current_theme == "dark":
            title.setStyleSheet("font: bold 18px; color: #A7C7E7;")  # 浅蓝色
        else:
            title.setStyleSheet("font: bold 18px; color: #A7C7E7;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 添加分隔线 - 优化黑夜模式颜色
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        if self.current_theme == "dark":
            separator.setStyleSheet("background-color: #555555;")  # 深灰色
        else:
            separator.setStyleSheet("background-color: #E0E0E0;")
        layout.addWidget(separator)

        # 添加滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content.setObjectName("scrollContent")  # 为内容区域设置对象名
        content_layout = QVBoxLayout(content)
        content_layout.setAlignment(Qt.AlignTop)

        # ========== 问答内容 ==========
        qa_pairs = [
            ("星辉的数位板现在用来干什么？", "打游戏的鼠标垫"),
            ("星辉最喜欢的食物是什么？", "代码编译后的二进制蛋糕"),
            ("星辉的编程语言偏好？", "Python，但有时也会用C++做高性能计算"),
            ("星辉如何解决bug？", "冥想三分钟后，bug会自动消失"),
            ("星辉的座右铭是什么？", "代码如诗，bug如雾，但星光终会穿透迷雾"),
            ("星辉如何看待人工智能？", "既是工具也是伙伴，就像数位板与画笔的关系"),
            ("星辉的休息方式？", "在GitHub星海中漫游"),
            ("星辉的学习方法？", "阅读文档如同阅读星空图谱"),
            ("星辉是福瑞吗？", "你猜？"),
            ("如何联系星辉？", "B站:3493123229485258  QQ群:1047728959"),
        ]

        for question, answer in qa_pairs:
            # 问题按钮样式 - 根据主题调整
            q_btn = QPushButton(question)
            if self.current_theme == "dark":
                # 黑夜模式样式
                q_btn_style = """
                    QPushButton {
                        text-align: left;
                        padding: 12px;
                        font-size: 14px;
                        background: #3A3A3A;  /* 深灰色背景 */
                        border: 1px solid #555555;  /* 深灰色边框 */
                        border-radius: 8px;
                        color: #E0E0E0;  /* 浅灰色文本 */
                    }
                    QPushButton:hover {
                        background: #4A4A4A;  /* 悬停时稍亮 */
                    }
                """
            else:
                # 白昼模式样式
                q_btn_style = """
                    QPushButton {
                        text-align: left;
                        padding: 12px;
                        font-size: 14px;
                        background: #F5F5F5;
                        border: 1px solid #E0E0E0;
                        border-radius: 8px;
                        color: #C0D6E4;
                    }
                    QPushButton:hover {
                        background: #EDEDED;
                    }
                """
            q_btn.setStyleSheet(q_btn_style)

            # 答案标签样式 - 根据主题调整
            if self.current_theme == "dark":
                # 黑夜模式样式
                ans_label = QLabel(
                    f"<span style='color:#FFFFFF; font-weight:bold;'>答：</span><span style='color:#FFFFFF;'>{answer}</span>")
                ans_label.setStyleSheet("""
                    background: #3A5A80;  /* 深蓝色背景 */
                    padding: 12px;
                    border-radius: 8px;
                    margin-bottom: 15px;
                """)
            else:
                # 白昼模式样式
                ans_label = QLabel(
                    f"<span style='color:#FFFFFF; font-weight:bold;'>答：</span><span style='color:#FFFFFF;'>{answer}</span>")
                ans_label.setStyleSheet("""
                    background: #C0D6E4;
                    padding: 12px;
                    border-radius: 8px;
                    margin-bottom: 15px;
                """)
            ans_label.setWordWrap(True)
            ans_label.hide()

            # 点击问题显示答案
            q_btn.clicked.connect(lambda _, lbl=ans_label: lbl.setVisible(True))

            content_layout.addWidget(q_btn)
            content_layout.addWidget(ans_label)

        scroll.setWidget(content)
        layout.addWidget(scroll)

        # 底部关闭按钮 - 根据主题调整
        close_btn = QPushButton("关闭")
        if self.current_theme == "dark":
            # 黑夜模式样式
            close_btn_style = """
                QPushButton {
                    background: #3A5A80;  /* 深蓝色 */
                    color: white;
                    border-radius: 8px;
                    padding: 8px 20px;
                }
                QPushButton:hover {
                    background: #4A6A90;  /* 悬停时稍亮 */
                }
            """
        else:
            # 白昼模式样式
            close_btn_style = """
                QPushButton {
                    background: #C0D6E4;
                    color: white;
                    border-radius: 8px;
                    padding: 8px 20px;
                }
                QPushButton:hover {
                    background: #B0C4DE;
                }
            """
        close_btn.setStyleSheet(close_btn_style)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)

        # 显示对话框
        dialog.setAttribute(Qt.WA_DeleteOnClose)
        dialog.show()


class AbnormalityManager:
    """自定义异想体管理器（增强版）"""
    CUSTOM_ABNO_FILE = os.path.join(ControlPanel.CONFIG_PATH, 'custom_abnormalities.json')

    def __init__(self, control_panel):
        self.control_panel = control_panel
        self.custom_abnormalities = {}
        self.load_custom_abnormalities()

    def load_custom_abnormalities(self):
        """加载自定义异想体"""
        try:
            if not os.path.exists(self.CUSTOM_ABNO_FILE):
                # 创建空文件
                with open(self.CUSTOM_ABNO_FILE, 'w') as f:
                    json.dump({}, f)
                return {}

            with open(self.CUSTOM_ABNO_FILE, 'r', encoding='utf-8') as f:
                self.custom_abnormalities = json.load(f)

            # 合并到主异想体数据
            for abno_id, data in self.custom_abnormalities.items():
                self.control_panel.abnormality_data[abno_id] = data

            return self.custom_abnormalities
        except Exception as e:
            print(f"加载自定义异想体失败: {str(e)}")
            return {}

    def get_custom_abnormalities(self):
        """获取所有自定义异想体"""
        return self.custom_abnormalities

    def is_custom_abnormality(self, abno_id):
        """检查是否已存在该ID的自定义异想体"""
        return abno_id in self.custom_abnormalities

    def get_abnormality(self, abno_id):
        """获取指定异想体数据"""
        return self.custom_abnormalities.get(abno_id)

    def add_custom_abnormality(self, abno_id, abno_data):
        """添加新异想体（添加调试日志）"""
        try:
            print(f"尝试添加异想体: {abno_id}")
            if abno_id in self.custom_abnormalities:
                print(f"异想体 {abno_id} 已存在")
                return False

            self.custom_abnormalities[abno_id] = abno_data
            print(f"添加成功: {abno_id}")
            return self.save_custom_abnormalities()
        except Exception as e:
            print(f"添加自定义异想体失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def update_custom_abnormality(self, abno_id, new_data):
        """更新异想体数据"""
        try:
            if abno_id not in self.custom_abnormalities:
                return False  # 不存在，应使用添加方法

            self.custom_abnormalities[abno_id] = new_data
            self.save_custom_abnormalities()
            return True
        except Exception as e:
            print(f"更新自定义异想体失败: {str(e)}")
            return False

    def delete_custom_abnormality(self, abno_id):
        """删除异想体"""
        try:
            if abno_id not in self.custom_abnormalities:
                return False

            # 从内存中删除
            del self.custom_abnormalities[abno_id]

            # 保存到文件
            self.save_custom_abnormalities()
            return True
        except Exception as e:
            print(f"删除自定义异想体失败: {str(e)}")
            return False

    def save_custom_abnormalities(self):
        """保存自定义异想体到文件"""
        try:
            with open(self.CUSTOM_ABNO_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.custom_abnormalities, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存自定义异想体失败: {str(e)}")
            return False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()

        # ========== 窗口入场动画 ==========
        self.opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_anim.setDuration(300)
        self.opacity_anim.setStartValue(0)
        self.opacity_anim.setEndValue(1)
        self.opacity_anim.setEasingCurve(QEasingCurve.OutCubic)
        self.opacity_anim.start()

    def setup_ui(self):
        """Win11风格主界面"""
        ico_path = os.path.join("images", "桌面星辉图标.ico")
        if os.path.exists(ico_path):
            self.setWindowIcon(QIcon(ico_path))
            self.tray.setIcon(QIcon(ico_path))  # 修改托盘图标
        self.setWindowTitle("星辉设置")
        self.setFixedSize(360, 200)  # 调整窗口尺寸

        # ============== 新增Win11样式代码 ==============
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F3F3F3;
                font-family: 'Segoe UI Variable';
                border-radius: 8px;
                border: 1px solid #E0E0E0;
            }
            QPushButton {
                background-color: #0078D4;
                border: 1px solid #0078D4;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                min-width: 120px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #106EBE;
                border-color: #005A9E;
            }
            QPushButton:pressed {
                background-color: #005A9E;
                border-color: #004578;
            }
        """)
        # ============== 删除阴影相关代码 ==============

        # 按钮布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        btn_normal = QPushButton("普通模式")
        btn_background = QPushButton("后台模式")

        layout.addWidget(btn_normal)
        layout.addWidget(btn_background)
        layout.setContentsMargins(40, 40, 40, 40)  # 增加边距

        # 连接信号
        btn_normal.clicked.connect(self.start_normal)
        btn_background.clicked.connect(self.start_background)

        # 系统托盘图标
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        tray_menu = QMenu()
        tray_menu.setStyleSheet("""
            QMenu {
                background: white;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 8px;
                margin: 4px;
            }
            QMenu::item {
                padding: 8px 32px;
                border-radius: 4px;
                color: #1A1A1A;
            }
            QMenu::item:selected {
                background: rgba(0, 120, 212, 0.1);
            }
        """)
        exit_action = tray_menu.addAction("退出")
        exit_action.triggered.connect(QApplication.quit)
        self.tray.setContextMenu(tray_menu)
        self.tray.show()

    def start_normal(self):
        self.pet = VirtualPet()
        self.pet.show()
        self.hide()

    def start_background(self):
        with open("config.json", "w") as f:
            json.dump({"background": True}, f)
        self.start_normal()


def check_background():
    try:
        with open("config.json") as f:
            config = json.load(f)
            # 添加domain_path初始化
            config.setdefault("background", False)
            config.setdefault("domain_path", None)
            return config["background"], config["domain_path"]
    except:
        return False, None


if __name__ == "__main__":
    try:
        # 初始化 Qt 应用
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        app.setQuitOnLastWindowClosed(False)

        print("程序启动...")

        # 根据配置选择模式
        if check_background():
            print("进入后台模式")
            pet = VirtualPet()
            pet.show()
        else:
            print("进入普通模式")
            window = MainWindow()
            window.show()

        print("启动事件循环")
        sys.exit(app.exec_())

    except Exception as e:
        print("发生异常:", e)