# =============================================================================
# EVN TOOL AIO - PyQt6 Professional Edition v3.2
# by CuongNM.HNM - 2026
# Cài đặt: pip install PyQt6 pandas pdfplumber selenium webdriver-manager requests openpyxl Pillow
# =============================================================================

import sys
import os
import time
import threading
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget, QScrollArea,
    QLineEdit, QComboBox, QCheckBox, QRadioButton, QButtonGroup,
    QTextEdit, QFileDialog, QGraphicsDropShadowEffect, QSizePolicy, QSpacerItem,
    QTabWidget
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap, QColor, QTextCursor, QTextCharFormat

import core  # Import module logic chính

# =============================================================================
# PATHS
# =============================================================================
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ASSETS_DIR = os.path.join(BASE_DIR, "assets")

def get_asset(filename):
    return os.path.join(ASSETS_DIR, filename)

# =============================================================================
# CONFIGURATION SAVING
# =============================================================================
if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = BASE_DIR

CONFIG_FILE = os.path.join(APP_DIR, "config.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {}

def save_config(data):
    try:
        current = load_config()
        current.update(data)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(current, f, ensure_ascii=False, indent=4)
    except: pass

# =============================================================================
# THEME SYSTEM v3.1 - DARK / LIGHT
# Màu nhấn chủ đạo: TÍM (Purple) xuyên suốt cả hai mode
# =============================================================================
THEMES = {
    "dark": {
        # --- Nền chính ---
        "bg_main":          "#0F1419",
        "bg_card":          "#1A1D23",
        "bg_card_hover":    "#21252D",
        # --- Sidebar: nền tối hơn content ---
        "sidebar_bg":       "#0B0D12",
        "sidebar_hover":    "#1A1D23",
        "sidebar_accent":   "#7C3AED",   # Màu tím cho active nav border
        # --- Text ---
        "text_title":       "#F1F5F9",
        "text_body":        "#C4C9D4",
        "text_muted":       "#6B7280",
        "text_highlight":   "#A78BFA",   # Tím nhạt cho text highlight
        # --- Buttons: TÍM là primary ---
        "btn_primary":      "#7C3AED",
        "btn_primary_hv":   "#6D28D9",
        "btn_danger":       "#EF4444",
        "btn_danger_hv":    "#DC2626",
        "btn_success":      "#10B981",
        "btn_success_hv":   "#059669",
        "btn_warning":      "#F59E0B",
        "btn_warning_hv":   "#D97706",
        "btn_cta":          "#7C3AED",
        "btn_cta_hv":       "#6D28D9",
        # --- Input & Border: Xám tối, chỉ sáng khi focus ---
        "border":           "#3e3e42",   # Per spec: xám tối thay cyan
        "border_focus":     "#7C3AED",   # Tím sáng khi focus
        "input_bg":         "#13161C",
        # --- Console: Monokai theme ---
        "log_bg":           "#1e1e1e",   # Nền tối đặc
        "log_ok":           "#A6E22E",   # Neon xanh lá (Monokai)
        "log_err":          "#F92672",   # Hồng đỏ (Monokai)
        "log_warn":         "#E6DB74",   # Vàng nhạt (Monokai)
        "log_info":         "#66D9E8",   # Cyan nhạt (Monokai)
        "log_default":      "#A6E22E",   # Neon dịu (per spec)
        "scrollbar":        "#3e3e42",
    },
    "light": {
        # --- Nền chính ---
        "bg_main":          "#F4F6FA",
        "bg_card":          "#FFFFFF",
        "bg_card_hover":    "#EEF2FF",   # Tím rất nhạt khi hover card
        # --- Sidebar: Xám tím nhạt với vạch tím trái ---
        "sidebar_bg":       "#EDE9F6",   # Tím nhạt per spec
        "sidebar_hover":    "#DDD6FE",
        "sidebar_accent":   "#7C3AED",   # Vạch tím trái active nav
        # --- Text ---
        "text_title":       "#0F172A",
        "text_body":        "#1E293B",
        "text_muted":       "#64748B",
        "text_highlight":   "#6D28D9",   # Tím đậm cho highlight
        # --- Buttons: TÍM là primary ---
        "btn_primary":      "#7C3AED",
        "btn_primary_hv":   "#6D28D9",
        "btn_danger":       "#EF4444",
        "btn_danger_hv":    "#DC2626",
        "btn_success":      "#10B981",
        "btn_success_hv":   "#059669",
        "btn_warning":      "#F59E0B",
        "btn_warning_hv":   "#D97706",
        "btn_cta":          "#7C3AED",
        "btn_cta_hv":       "#6D28D9",
        # --- Input & Border ---
        "border":           "#D1D5DB",
        "border_focus":     "#7C3AED",   # Tím sáng khi focus (per spec)
        "input_bg":         "#F9FAFB",
        # --- Console: Nền tối đặc per spec ---
        "log_bg":           "#1e1e1e",   # Per spec: dùng màu nền xám cực đậm
        "log_ok":           "#4ADE80",
        "log_err":          "#F87171",
        "log_warn":         "#FBBF24",
        "log_info":         "#93C5FD",
        "log_default":      "#D1D5DB",
        "scrollbar":        "#D1D5DB",
    }
}

# Mặc định lúc mở tool là light mode
current_mode = "light"
T = THEMES[current_mode]

def get_theme():
    return THEMES[current_mode]

# =============================================================================
# FONTS - Consolas cho Console, Segoe UI cho UI
# =============================================================================
def F(style="body"):
    fonts = {
        "h1":        QFont("Segoe UI", 13, QFont.Weight.Bold),
        "h2":        QFont("Segoe UI", 11, QFont.Weight.Bold),
        "h3":        QFont("Segoe UI", 10, QFont.Weight.Bold),
        "body":      QFont("Segoe UI", 9),
        "body_bold": QFont("Segoe UI", 9, QFont.Weight.Bold),
        "small":     QFont("Segoe UI", 9),
        "tiny":      QFont("Segoe UI", 8),
        "code":      QFont("Consolas", 9),   # Font chuyên dụng cho console per spec
    }
    return fonts.get(style, fonts["body"])

# =============================================================================
# THREAD-SAFE TEXT SIGNAL
# =============================================================================
class TextSignal(QObject):
    text_written = pyqtSignal(str)

class TextRedirector:
    """Chuyển hướng print() về signal để hiển thị màu sắc trong log"""
    def __init__(self, signal):
        self.signal = signal

    def write(self, s):
        if s.strip():
            now = time.strftime("%H:%M:%S")
            self.signal.text_written.emit(f"[{now}] {s.strip()}")

    def flush(self):
        pass

# =============================================================================
# TOAST NOTIFICATION
# =============================================================================
class Toast(QFrame):
    def __init__(self, parent, title, message, toast_type="info"):
        super().__init__(parent)
        T = get_theme()
        self.setFixedSize(300, 75)

        pw = parent.window()
        self.move(pw.width() - 320, pw.height() - 105)

        colors = {
            "info":    T["btn_primary"],
            "success": T["btn_success"],
            "error":   T["btn_danger"],
            "warning": T["btn_warning"],
        }
        accent = colors.get(toast_type, T["btn_primary"])

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {T['bg_card']};
                border-radius: 10px;
                border: 1px solid {T['border']};
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 12, 0)
        layout.setSpacing(0)

        strip = QFrame()
        strip.setFixedWidth(5)
        strip.setStyleSheet(f"background-color: {accent}; border-radius: 0;")
        layout.addWidget(strip)

        content = QVBoxLayout()
        content.setContentsMargins(12, 8, 0, 8)
        content.setSpacing(2)

        t_lbl = QLabel(title)
        t_lbl.setFont(F("body_bold"))
        t_lbl.setStyleSheet(f"color: {T['text_title']}; background: transparent; border: none;")
        content.addWidget(t_lbl)

        m_lbl = QLabel(message)
        m_lbl.setFont(F("small"))
        m_lbl.setStyleSheet(f"color: {T['text_body']}; background: transparent; border: none;")
        m_lbl.setWordWrap(True)
        content.addWidget(m_lbl)

        layout.addLayout(content)
        self.show()
        self.raise_()
        QTimer.singleShot(3200, self.close)

# =============================================================================
# SVG ICONS - Bộ icon đồng nhất thay thế emoji (per spec)
# =============================================================================
ICON_FOLDER = """<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>"""
ICON_FILE   = """<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>"""

def make_svg_icon(svg_str, color="#7C3AED", size=14):
    """Tạo QPixmap từ SVG string với màu tùy chỉnh"""
    try:
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtCore import QByteArray
        colored = svg_str.replace('stroke="currentColor"', f'stroke="{color}"')
        renderer = QSvgRenderer(QByteArray(colored.encode()))
        pm = QPixmap(size, size)
        pm.fill(Qt.GlobalColor.transparent)
        from PyQt6.QtGui import QPainter
        painter = QPainter(pm)
        renderer.render(painter)
        painter.end()
        return QIcon(pm)
    except Exception:
        return QIcon()

# =============================================================================
# REUSABLE WIDGETS
# =============================================================================

class Card(QFrame):
    """Card container bo góc với shadow nhẹ"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.refresh_theme()

    def refresh_theme(self):
        T = get_theme()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {T['bg_card']};
                border-radius: 12px;
                border: 1px solid {T['border']};
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(16)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)


class InputGroup(QFrame):
    """
    Group box chứa các input field - có viền mờ + shadow nhẹ
    Tách biệt phần nhập liệu với System Console (per spec)
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.refresh_theme()
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(12, 12, 12, 12)
        self._layout.setSpacing(12)   # Khoảng thở 12px per spec

    def refresh_theme(self):
        T = get_theme()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {T['bg_card']};
                border-radius: 10px;
                border: 1px solid {T['border']};
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

    def add(self, widget):
        self._layout.addWidget(widget)

    def add_layout(self, layout):
        self._layout.addLayout(layout)


class Btn(QPushButton):
    """Button hiện đại - màu TÍM là primary"""
    def __init__(self, text, btn_type="primary", icon_path=None, parent=None):
        super().__init__(text, parent)
        self.btn_type = btn_type
        self.setFont(F("body_bold"))
        self.setFixedHeight(32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        if icon_path and os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
        self.refresh_theme()

    def refresh_theme(self):
        T = get_theme()
        colors = {
            "primary": (T["btn_primary"],   T["btn_primary_hv"]),
            "success": (T["btn_success"],   T["btn_success_hv"]),
            "danger":  (T["btn_danger"],    T["btn_danger_hv"]),
            "warning": (T["btn_warning"],   T["btn_warning_hv"]),
            "cta":     (T["btn_cta"],       T["btn_cta_hv"]),
            "ghost":   (T["bg_card_hover"], T["border"]),
        }
        bg, hv = colors.get(self.btn_type, colors["primary"])
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {"#FFFFFF" if self.btn_type != "ghost" else T['text_body']};
                border: none;
                border-radius: 8px;
                padding: 0 16px;
            }}
            QPushButton:hover {{
                background-color: {hv};
            }}
            QPushButton:disabled {{ background-color: {T['text_muted']}; color: #888; }}
        """)


class BrowseBtn(QPushButton):
    """
    Nút browse dùng icon Folder/File thay vì text '...' (per spec)
    Dùng SVG icon đồng nhất từ Lucide icon set
    """
    def __init__(self, browse_type="folder", parent=None):
        super().__init__(parent)
        self.setFixedSize(30, 28)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Chọn thư mục" if browse_type == "folder" else "Chọn file")

        if browse_type == "folder":
            self.setText("📂")
        else:
            self.setText("📄")
        self.setFont(QFont("Segoe UI", 11))
        self.refresh_theme()

    def refresh_theme(self):
        T = get_theme()
        # Dark mode: icon mờ ~60% độ sáng cho đến khi hover (per spec)
        is_dark = current_mode == "dark"
        icon_color = T['text_muted'] if is_dark else T['btn_primary']
        bg_normal  = T['bg_card_hover'] if not is_dark else "#1C1F27"
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_normal};
                color: {icon_color};
                border: 1px solid {T['border']};
                border-radius: 6px;
                padding: 0;
                opacity: 0.6;
            }}
            QPushButton:hover {{
                background-color: {T['btn_primary']};
                color: #FFFFFF;
                border-color: {T['btn_primary']};
            }}
        """)


class Entry(QWidget):
    """Input field + browse button với icon folder/file"""
    def __init__(self, label, default="", browse_type=None, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.lbl = QLabel(label)
        self.lbl.setFont(F("tiny"))
        layout.addWidget(self.lbl)

        row = QHBoxLayout()
        row.setSpacing(6)
        self.entry = QLineEdit(default)
        self.entry.setFont(F("small"))
        self.entry.setFixedHeight(28)
        row.addWidget(self.entry)

        if browse_type:
            self.browse_type = browse_type
            self.btn_b = BrowseBtn(browse_type)
            self.btn_b.clicked.connect(self._browse)
            row.addWidget(self.btn_b)

        layout.addLayout(row)
        self.refresh_theme()

    def refresh_theme(self):
        T = get_theme()
        self.lbl.setStyleSheet(f"color: {T['text_muted']};")
        self.entry.setStyleSheet(f"""
            QLineEdit {{
                background-color: {T['input_bg']};
                color: {T['text_body']};
                border: 1px solid {T['border']};
                border-radius: 6px;
                padding: 0 8px;
            }}
            QLineEdit:focus {{
                border-color: {T['border_focus']};
            }}
        """)
        if hasattr(self, 'btn_b'):
            self.btn_b.refresh_theme()

    def _browse(self):
        if self.browse_type == "folder":
            p = QFileDialog.getExistingDirectory(self, "Chọn thư mục")
        elif self.browse_type == "file":
            p, _ = QFileDialog.getOpenFileName(self, "Chọn file")
        else:
            p, _ = QFileDialog.getSaveFileName(self, "Lưu file", filter="Excel (*.xlsx)")
        if p:
            self.entry.setText(p)

    def get(self): return self.entry.text()
    def set(self, v): self.entry.setText(v)


class Combo(QWidget):
    """Dropdown hiện đại với label"""
    def __init__(self, label, values, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.lbl = QLabel(label)
        self.lbl.setFont(F("tiny"))
        layout.addWidget(self.lbl)

        self.combo = QComboBox()
        self.combo.addItems(values)
        self.combo.setFont(F("small"))
        self.combo.setFixedHeight(28)
        self.combo.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.combo)
        self.refresh_theme()

    def refresh_theme(self):
        T = get_theme()
        self.lbl.setStyleSheet(f"color: {T['text_muted']};")
        self.combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {T['input_bg']};
                color: {T['text_body']};
                border: 1px solid {T['border']};
                border-radius: 6px;
                padding: 0 10px;
            }}
            QComboBox:hover {{ border-color: {T['btn_primary']}; }}
            QComboBox::drop-down {{ border: none; width: 22px; }}
            QComboBox QAbstractItemView {{
                background-color: {T['bg_card']};
                color: {T['text_body']};
                selection-background-color: {T['btn_primary']};
                selection-color: white;
                border: 1px solid {T['border']};
                border-radius: 6px;
            }}
        """)

    def get(self): return self.combo.currentText()
    def set(self, v):
        i = self.combo.findText(v)
        if i >= 0: self.combo.setCurrentIndex(i)


# =============================================================================
# LOG WIDGET - Hiển thị log màu sắc kiểu Monokai (per spec)
# =============================================================================
class ColorLog(QTextEdit):
    """TextEdit hiển thị log với màu theo loại thông báo - style Monokai"""

    OK_KEYS   = ["✅", "🏁", "✨", "thành công", "success", "hoàn tất", "ok"]
    ERR_KEYS  = ["🚫", "❌", "lỗi", "error", "failed", "thất bại"]
    WARN_KEYS = ["⚠️", "⚡", "cảnh báo", "warn"]
    INFO_KEYS = ["🚀", "📊", "👤", "🔍", "📥", "📄", "💾", "💡", "🔤", "🔄", "🖨️"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFont(F("code"))
        self.refresh_theme()

    def refresh_theme(self):
        T = get_theme()
        # Consolas / Cascadia Code = font monospace chuyên dụng, ký tự thẳng hàng kiểu terminal (per spec)
        self.setFont(F("code"))
        self.setStyleSheet(f"""
            QTextEdit {{
                background-color: {T['log_bg']};
                color: {T['log_default']};
                border: none;
                border-radius: 8px;
                padding: 10px 12px;
                font-family: 'Consolas', 'Cascadia Code', 'JetBrains Mono', monospace;
                font-size: 9pt;
                line-height: 1.6;
            }}
            QScrollBar:vertical {{
                background-color: transparent;
                width: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: #3e3e42;
                border-radius: 3px;
                min-height: 20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)

    def _detect_color(self, text_lower):
        """Phát hiện màu dựa trên nội dung log"""
        T = get_theme()
        for k in self.ERR_KEYS:
            if k in text_lower:
                return T["log_err"]
        for k in self.OK_KEYS:
            if k in text_lower:
                return T["log_ok"]
        for k in self.WARN_KEYS:
            if k in text_lower:
                return T["log_warn"]
        for k in self.INFO_KEYS:
            if k in text_lower:
                return T["log_info"]
        return get_theme()["log_default"]

    def append_colored(self, text):
        """Thêm dòng log với màu tự động"""
        color = self._detect_color(text.lower())
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))

        cursor.insertText(text + "\n", fmt)
        self.setTextCursor(cursor)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def clear_log(self):
        self.clear()


# =============================================================================
# PAGE BASE
# =============================================================================
class Page(QScrollArea):
    def __init__(self, title, subtitle, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setWidgetResizable(True)

        container = QWidget()
        container.setStyleSheet("background-color: transparent;")
        self.setWidget(container)

        self.main_layout = QVBoxLayout(container)
        self.main_layout.setContentsMargins(16, 14, 16, 12)
        self.main_layout.setSpacing(14)   # Tăng khoảng thở per spec

        # Header nhỏ gọn
        hdr = QWidget()
        hdr_layout = QVBoxLayout(hdr)
        hdr_layout.setContentsMargins(0, 0, 0, 0)
        hdr_layout.setSpacing(2)

        self.t_lbl = QLabel(title)
        self.t_lbl.setFont(F("h1"))
        hdr_layout.addWidget(self.t_lbl)

        self.s_lbl = QLabel(subtitle)
        self.s_lbl.setFont(F("small"))
        if subtitle == "":
            self.s_lbl.hide()
        hdr_layout.addWidget(self.s_lbl)

        self.main_layout.addWidget(hdr)

        self.content = QVBoxLayout()
        self.content.setSpacing(14)
        self.main_layout.addLayout(self.content, 1)
        self.refresh_theme()

    def refresh_theme(self):
        T = get_theme()
        self.t_lbl.setStyleSheet(f"color: {T['text_title']};")
        self.s_lbl.setStyleSheet(f"color: {T['text_muted']};")
        self.setStyleSheet(f"""
            QScrollArea {{ background-color: transparent; border: none; }}
            QScrollBar:vertical {{
                background-color: transparent;
                width: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {T['scrollbar']};
                border-radius: 3px;
                min-height: 20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)

    def toast(self, title, msg, toast_type="info"):
        pass # Tắt toast notification theo yêu cầu của User vì vướng víu


# =============================================================================
# DOWNLOAD PAGE
# =============================================================================
class DownloadPage(Page):
    def __init__(self, parent=None):
        super().__init__("⬇  Tải Hóa Đơn Tự Động", "", parent)

        self.text_signal = TextSignal()
        self.text_signal.text_written.connect(self._append_log)

        T = get_theme()

        # ── InputGroup: Phân nhóm ô nhập liệu (per spec) ──
        input_box = InputGroup()

        config = load_config()
        self.e_excel = Entry("📄 File Excel tài khoản (Cột A: User | Cột B: Pass)",
                             config.get("excel_path", r"D:\TEST_1\TK-MK-EVN.xlsx"), "file")
        input_box.add(self.e_excel)

        self.e_folder = Entry("📁 Thư mục lưu hóa đơn tải về",
                              config.get("folder_path", r"D:\TEST_1"), "folder")
        input_box.add(self.e_folder)

        # Grid: Tháng / Năm / Trình duyệt / Model AI
        grid = QHBoxLayout()
        grid.setSpacing(12)

        self.c_month   = Combo("📅 Tháng", [str(i) for i in range(1, 13)])
        self.c_month.set("12")
        grid.addWidget(self.c_month)

        self.c_year    = Combo("📅 Năm", ["2024", "2025", "2026"])
        self.c_year.set("2026")
        grid.addWidget(self.c_year)

        self.c_browser = Combo("🌐 Trình duyệt", ["Edge", "Chrome"])
        grid.addWidget(self.c_browser)

        self.c_model   = Combo("🤖 Model AI", ["Premium", "Standard", "Lite"])
        self.c_model.set(config.get("model_type", "Premium"))
        grid.addWidget(self.c_model)

        input_box.add_layout(grid)

        # Xóa checkbox chạy ẩn theo yêu cầu, hệ thống sẽ mặc định chạy ẩn và lấy thêm ko gian
        self.content.addWidget(input_box)

        # Start button
        self.btn_start = Btn("🚀  BẮT ĐẦU TẢI DỮ LIỆU", "cta")
        self.btn_start.setFixedHeight(36)
        self.btn_start.clicked.connect(self.start)
        self.content.addWidget(self.btn_start)

        # ── Console area - tách biệt rõ ràng ──
        log_card = Card()
        log_cl = QVBoxLayout(log_card)
        log_cl.setContentsMargins(10, 8, 10, 8)
        log_cl.setSpacing(6)

        log_hdr_row = QHBoxLayout()
        self.log_hdr_lbl = QLabel("SYSTEM CONSOLE")
        self.log_hdr_lbl.setFont(F("tiny"))
        log_hdr_row.addWidget(self.log_hdr_lbl)
        log_hdr_row.addStretch()

        btn_clear = Btn("Xóa log", "ghost")
        btn_clear.setFixedSize(72, 24)
        btn_clear.setFont(F("tiny"))
        btn_clear.clicked.connect(lambda: self.log.clear_log())
        log_hdr_row.addWidget(btn_clear)

        log_cl.addLayout(log_hdr_row)

        self.log = ColorLog()
        self.log.setMinimumHeight(150)
        log_cl.addWidget(self.log)

        self.content.addWidget(log_card, 1)

        self.refresh_theme()

        # Welcome message
        self.log.append_colored("✅ Hệ thống sẵn sàng! Chọn file Excel và bấm BẮT ĐẦU để tải hóa đơn.")

    def refresh_theme(self):
        super().refresh_theme()
        T = get_theme()
        if hasattr(self, 'log_hdr_lbl'):
            self.log_hdr_lbl.setStyleSheet(f"""
                QLabel {{
                    background-color: {T['bg_card_hover']};
                    color: {T['text_muted']};
                    border: none;
                    border-radius: 6px;
                    padding: 4px 12px;
                    font-weight: bold;
                    letter-spacing: 1px;
                }}
            """)
    def _append_log(self, text):
        self.log.append_colored(text)

    def start(self):
        save_config({
            "excel_path": self.e_excel.get(),
            "folder_path": self.e_folder.get(),
            "model_type": self.c_model.get()
        })
        sys.stdout = TextRedirector(self.text_signal)
        self.toast("Khởi động", "Đang khởi động tiến trình tải...", "info")
        self.btn_start.setEnabled(False)
        self.btn_start.setText("⏳  ĐANG CHẠY...")
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            core.run_process_gui(
                self.e_excel.get(), self.e_folder.get(),
                self.c_month.get(), self.c_year.get(),
                self.c_browser.get(), True
            )
            QTimer.singleShot(0, lambda: self.toast("Hoàn tất", "Đã tải xong toàn bộ hóa đơn!", "success"))
        except Exception as e:
            QTimer.singleShot(0, lambda: self.toast("Lỗi hệ thống", str(e), "error"))
            print(f"🚫 Lỗi hệ thống: {e}")
        finally:
            QTimer.singleShot(0, self._reset_btn)

    def _reset_btn(self):
        self.btn_start.setEnabled(True)
        self.btn_start.setText("🚀  BẮT ĐẦU TẢI DỮ LIỆU")
        self.btn_start.style().unpolish(self.btn_start)
        self.btn_start.style().polish(self.btn_start)
        self.btn_start.update()


# =============================================================================
# TOOLS PAGE
# =============================================================================
class ToolsPage(Page):
    def __init__(self, parent=None):
        super().__init__("🔧  Công Cụ Xử Lý", "Giải nén ZIP · Ánh xạ tên · In PDF hàng loạt", parent)

        self.text_signal = TextSignal()
        self.text_signal.text_written.connect(self._append_log)
        T = get_theme()

        # Gộp thành Tab để tiết kiệm không gian, nhường chỗ cho log Console
        self.tab_menu = QFrame()
        self.tab_menu.setFixedHeight(44)
        tm_layout = QHBoxLayout(self.tab_menu)
        tm_layout.setContentsMargins(4, 4, 4, 4)
        tm_layout.setSpacing(4)
        
        self.btn_tab1 = QPushButton("📦 Giải Nén")
        self.btn_tab2 = QPushButton("🔀 Ánh Xạ")
        self.btn_tab3 = QPushButton("🖨️ In Ấn")
        
        for i, btn in enumerate((self.btn_tab1, self.btn_tab2, self.btn_tab3)):
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setCheckable(True)
            if i == 0: btn.clicked.connect(lambda: self.switch_tab(0))
            elif i == 1: btn.clicked.connect(lambda: self.switch_tab(1))
            elif i == 2: btn.clicked.connect(lambda: self.switch_tab(2))
            tm_layout.addWidget(btn)
        
        self.btn_tab1.setChecked(True)
        self.content.addWidget(self.tab_menu)

        self.tabs = QStackedWidget()

        # === GIẢI NÉN ===
        c1 = QWidget()
        l1 = QVBoxLayout(c1)
        l1.setContentsMargins(4, 2, 4, 0)
        l1.setSpacing(12)
        l1.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.e_zip = Entry("Thư mục chứa file .ZIP vừa tải về", r"D:\TEST_1", "folder")
        l1.addWidget(self.e_zip)
        b1 = Btn("▶  Chạy giải nén", "warning")
        b1.clicked.connect(self.start_unzip)
        l1.addWidget(b1)
        self.tabs.addWidget(c1)

        # === ÁNH XẠ ===
        c2 = QWidget()
        l2 = QVBoxLayout(c2)
        l2.setContentsMargins(4, 2, 4, 0)
        l2.setSpacing(12)
        l2.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.e_pmap = Entry("Thư mục PDF cần đổi tên", r"D:\TEST_1\HoaDon_Tong", "folder")
        l2.addWidget(self.e_pmap)
        self.e_map = Entry("File Excel Mapping (Cột A: Mã KH | Cột B: Mã CSHT)", r"D:\TEST_1\Mapping.xlsx", "file")
        l2.addWidget(self.e_map)
        
        map_date_layout = QHBoxLayout()
        map_date_layout.setSpacing(12)
        self.map_month = Combo("📅 Ký hiệu Tháng", [str(i) for i in range(1, 13)])
        self.map_month.set("12")
        self.map_year = Combo("📅 Ký hiệu Năm", ["2024", "2025", "2026"])
        self.map_year.set("2026")
        map_date_layout.addWidget(self.map_month)
        map_date_layout.addWidget(self.map_year)
        l2.addLayout(map_date_layout)
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        bm1 = Btn("Mã KH → CSHT", "success")
        bm1.clicked.connect(lambda: self.start_map(1))
        btn_row.addWidget(bm1)
        bm2 = Btn("Mã CSHT → KH", "primary")
        bm2.clicked.connect(lambda: self.start_map(2))
        btn_row.addWidget(bm2)
        l2.addLayout(btn_row)
        self.tabs.addWidget(c2)

        # === IN ẤN ===
        c3 = QWidget()
        l3 = QVBoxLayout(c3)
        l3.setContentsMargins(4, 2, 4, 0)
        l3.setSpacing(12)
        l3.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.e_print = Entry("Thư mục chứa file PDF cần in", r"D:\TEST_1\HoaDon_Tong", "folder")
        l3.addWidget(self.e_print)
        b3 = Btn("🖨️  Gửi lệnh in", "danger")
        b3.clicked.connect(self.start_print)
        l3.addWidget(b3)
        self.tabs.addWidget(c3)

        self.content.addWidget(self.tabs)

        # LOG
        log_card = Card()
        log_cl = QVBoxLayout(log_card)
        log_cl.setContentsMargins(12, 8, 12, 8)
        log_cl.setSpacing(6)

        log_hdr_row = QHBoxLayout()
        self.log_hdr = QLabel("SYSTEM CONSOLE")
        self.log_hdr.setFont(F("tiny"))
        log_hdr_row.addWidget(self.log_hdr)
        log_hdr_row.addStretch()

        btn_clear = Btn("Xóa log", "ghost")
        btn_clear.setFixedSize(72, 24)
        btn_clear.setFont(F("tiny"))
        btn_clear.clicked.connect(lambda: self.log.clear_log())
        log_hdr_row.addWidget(btn_clear)
        log_cl.addLayout(log_hdr_row)

        self.log = ColorLog()
        self.log.setMinimumHeight(150)
        log_cl.addWidget(self.log)
        self.content.addWidget(log_card, 1) # stretch parameter = 1: log tự động giãn đầy khoảng trống
        
        self.refresh_theme()
        
        # Báo log khởi tạo (per user request)
        self.log.append_colored("✅ Hệ thống sẵn sàng! Chọn công cụ trên Tab và bấm nút dưới cùng để bắt đầu.")
        self.switch_tab(0, True)

    def switch_tab(self, index, is_init=False):
        if not is_init:
            self.log.clear_log()
            t_name = "Giải Nén" if index == 0 else "Ánh Xạ" if index == 1 else "In Ấn"
            self.log.append_colored(f"✅ Đã chuyển sang chế độ thao tác: {t_name}. Sẵn sàng!")

        self.btn_tab1.setChecked(index == 0)
        self.btn_tab2.setChecked(index == 1)
        self.btn_tab3.setChecked(index == 2)
        self.tabs.setCurrentIndex(index)
        
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if i == index:
                w.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            else:
                w.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        
        # Bắt buộc tính toán lại và fix cứng height cho QStackedWidget nhảy lên xuống
        QApplication.processEvents() # ép ui update sơ bộ nếu cần
        current_w = self.tabs.widget(index)
        if current_w:
            content_h = current_w.sizeHint().height()
            self.tabs.setFixedHeight(content_h + 2)

    def refresh_theme(self):
        super().refresh_theme()
        T = get_theme()
        if hasattr(self, 'log_hdr'):
            self.log_hdr.setStyleSheet(f"""
                QLabel {{
                    background-color: {T['bg_card_hover']};
                    color: {T['text_muted']};
                    border: none;
                    border-radius: 6px;
                    padding: 4px 12px;
                    font-weight: bold;
                    letter-spacing: 1px;
                }}
            """)
            
            is_dark = current_mode == "dark"
            tab_bg = "#21242D" if is_dark else "#E2E8F0"
            tab_item_bg = "#303540" if is_dark else "#FFFFFF"
            
            # Cập nhật style cho khung menu custom (Segmented Control style full-width)
            self.tab_menu.setStyleSheet(f"""
                QFrame {{
                    background-color: {tab_bg};
                    border-radius: 8px;
                    border: 1px solid {T['border']};
                }}
                QPushButton {{
                    background-color: transparent;
                    color: {T['text_muted']};
                    border-radius: 6px;
                    font-size: 13px; font-weight: bold;
                    border: none;
                }}
                QPushButton:checked {{
                    background-color: {tab_item_bg};
                    color: {T['btn_primary']};
                    border: 1px solid {T['border']};
                }}
                QPushButton:hover:!checked {{
                    color: {T['text_body']};
                }}
            """)
            self.tabs.setStyleSheet("QStackedWidget { background: transparent; }")

    def _append_log(self, t): self.log.append_colored(t)

    def start_unzip(self):
        sys.stdout = TextRedirector(self.text_signal)
        self.toast("Giải nén", "Đang xử lý...", "warning")
        threading.Thread(target=lambda: core.organize_downloaded_files(self.e_zip.get()), daemon=True).start()

    def start_map(self, mode):
        sys.stdout = TextRedirector(self.text_signal)
        self.toast("Ánh xạ", "Đang thực hiện...", "info")
        threading.Thread(target=lambda: core.rename_with_excel_mapping(
            self.e_pmap.get(), self.e_map.get(), self.map_month.get(), self.map_year.get(), mode), daemon=True).start()

    def start_print(self):
        sys.stdout = TextRedirector(self.text_signal)
        self.toast("In ấn", "Đang gửi lệnh in...", "warning")
        threading.Thread(target=lambda: core.print_all_pdfs(self.e_print.get()), daemon=True).start()


# =============================================================================
# EXTRACT PAGE
# =============================================================================
class ExtractPage(Page):
    def __init__(self, parent=None):
        super().__init__("📊  Trích Xuất Dữ Liệu", "Đọc PDF và xuất ra file Excel tổng hợp", parent)

        self.text_signal = TextSignal()
        self.text_signal.text_written.connect(self._append_log)
        T = get_theme()

        card = InputGroup()

        # Radio
        radio_row = QHBoxLayout()
        radio_row.setSpacing(20)
        self.radio_group = QButtonGroup(self)

        self.r_tong = QRadioButton("📄 Hóa Đơn Tổng")
        self.r_tong.setFont(F("small"))
        self.r_tong.setChecked(True)
        self.radio_group.addButton(self.r_tong)
        radio_row.addWidget(self.r_tong)

        self.r_ct = QRadioButton("📋 Hóa Đơn Chi Tiết")
        self.r_ct.setFont(F("small"))
        self.radio_group.addButton(self.r_ct)
        radio_row.addWidget(self.r_ct)
        radio_row.addStretch()
        card.add_layout(radio_row)

        config = load_config()
        self.e_pdf = Entry("📁 Thư mục chứa file hóa đơn PDF",
                           config.get("pdf_path", r"D:\TEST_1\HoaDon_Tong"), "folder")
        card.add(self.e_pdf)

        self.e_save = Entry("💾 Thư mục lưu file Excel kết quả",
                            config.get("save_pdf_path", r"D:\TEST_1"), "folder")
        card.add(self.e_save)

        self.btn_ext = Btn("🚀  BẮT ĐẦU TRÍCH XUẤT", "success")
        self.btn_ext.setFixedHeight(38)
        self.btn_ext.clicked.connect(self.start)
        card.add(self.btn_ext)

        self.content.addWidget(card)

        # LOG
        log_card = Card()
        log_cl = QVBoxLayout(log_card)
        log_cl.setContentsMargins(12, 8, 12, 8)
        log_cl.setSpacing(6)

        log_hdr_row = QHBoxLayout()
        self.log_hdr = QLabel("SYSTEM CONSOLE")
        self.log_hdr.setFont(F("tiny"))
        log_hdr_row.addWidget(self.log_hdr)
        log_hdr_row.addStretch()

        btn_clear = Btn("Xóa log", "ghost")
        btn_clear.setFixedSize(72, 24)
        btn_clear.setFont(F("tiny"))
        btn_clear.clicked.connect(lambda: self.log.clear_log())
        log_hdr_row.addWidget(btn_clear)
        log_cl.addLayout(log_hdr_row)

        self.log = ColorLog()
        self.log.setMinimumHeight(150)
        log_cl.addWidget(self.log)
        self.content.addWidget(log_card, 1)

        self.refresh_theme()

    def refresh_theme(self):
        super().refresh_theme()
        T = get_theme()
        radio_style = f"""
            QRadioButton {{ color: {T['text_body']}; spacing: 6px; font-size: 11px; }}
            QRadioButton::indicator {{
                width: 16px; height: 16px; border-radius: 8px;
                border: 2px solid {T['border']}; background-color: {T['input_bg']};
            }}
            QRadioButton::indicator:checked {{
                background-color: {T['btn_primary']}; border-color: {T['btn_primary']};
            }}
        """
        if hasattr(self, 'r_tong'):
            self.r_tong.setStyleSheet(radio_style)
            self.r_ct.setStyleSheet(radio_style)
            self.log_hdr.setStyleSheet(f"""
                QLabel {{
                    background-color: {T['bg_card_hover']};
                    color: {T['text_muted']};
                    border: none;
                    border-radius: 6px;
                    padding: 4px 12px;
                    font-weight: bold;
                    letter-spacing: 1px;
                }}
            """)

    def _append_log(self, t): self.log.append_colored(t)

    def start(self):
        save_config({
            "pdf_path": self.e_pdf.get(),
            "save_pdf_path": self.e_save.get()
        })
        sys.stdout = TextRedirector(self.text_signal)
        self.toast("Trích xuất", "Đang quét dữ liệu PDF...", "success")
        self.btn_ext.setEnabled(False)
        self.btn_ext.setText("⏳  ĐANG QUÉT...")
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        import datetime
        try:
            today = datetime.datetime.now().strftime("%d-%m-%Y")
            save_path = os.path.join(self.e_save.get(), f"KetQua-{today}.xlsx")
            if self.r_tong.isChecked():
                core.extract_total_invoices(self.e_pdf.get(), save_path)
            else:
                core.extract_detailed_invoices(self.e_pdf.get(), save_path)
            QTimer.singleShot(0, lambda: self.toast("Xong!", f"Đã lưu: KetQua-{today}.xlsx", "success"))
        except Exception as e:
            QTimer.singleShot(0, lambda: self.toast("Lỗi", str(e), "error"))
        finally:
            QTimer.singleShot(0, self._reset_btn)

    def _reset_btn(self):
        self.btn_ext.setEnabled(True)
        self.btn_ext.setText("🚀  BẮT ĐẦU TRÍCH XUẤT")
        self.btn_ext.style().unpolish(self.btn_ext)
        self.btn_ext.style().polish(self.btn_ext)
        self.btn_ext.update()


# =============================================================================
# SIDEBAR NAV BUTTON - Màu tím là active, vạch tím trái (per spec)
# =============================================================================
class NavBtn(QPushButton):
    def __init__(self, icon_char, text, parent=None):
        super().__init__(f" {icon_char}  {text}", parent)
        self._active = False
        self.setFont(F("small"))
        self.setFixedHeight(36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._restyle()

    def set_active(self, v):
        self._active = v
        self._restyle()

    def refresh_theme(self):
        self._restyle()

    def _restyle(self):
        T = get_theme()
        if self._active:
            # Active: nền TÍM nhạt rõ ràng (dùng rgba thay hex+22 để đồng nhất trên mọi hệ thống)
            # Màu nền rgba(124,58,237,0.15) = tím 15% opacity, text màu tím nổi bật
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba(124, 58, 237, 0.15);
                    color: {T['text_highlight']};
                    border: none;
                    border-left: 3px solid {T['sidebar_accent']};
                    border-radius: 8px;
                    text-align: left;
                    padding-left: 10px;
                    font-weight: bold;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {T['text_muted']};
                    border: none;
                    border-radius: 8px;
                    text-align: left;
                    padding-left: 13px;
                }}
                QPushButton:hover {{
                    background-color: {T['sidebar_hover']};
                    color: {T['text_body']};
                }}
            """)


# =============================================================================
# MAIN WINDOW
# =============================================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Sửa lỗi mất icon trên taskbar Windows
        try:
            import ctypes
            myappid = 'cuongnm.hnm.evn_tool_aio.3.2'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

        self.is_dark = False
        self.setWindowTitle("EVN Tool AIO  •  v3.2")

        icon_path = os.path.join(BASE_DIR, "icon128.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.setMinimumSize(540, 500)
        self.resize(600, 580)
        self._build_ui()

    def _build_ui(self):
        T = get_theme()
        self.setStyleSheet(f"background-color: {T['bg_main']};")

        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ========================= SIDEBAR =========================
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setFixedWidth(172)
        # Light mode: tím nhạt | Dark mode: tối đặc (per spec)
        self.sidebar_frame.setStyleSheet(f"background-color: {T['sidebar_bg']};")

        sidebar_layout = QVBoxLayout(self.sidebar_frame)
        sidebar_layout.setContentsMargins(10, 16, 10, 12)
        sidebar_layout.setSpacing(0)

        # Logo / Branding
        self.logo_lbl = QLabel("⚡ EVN TOOL")
        self.logo_lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(self.logo_lbl)

        self.ver_lbl = QLabel("ALL IN ONE  v3.2")
        self.ver_lbl.setFont(F("tiny"))
        self.ver_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(self.ver_lbl)

        sidebar_layout.addSpacing(20)

        # Divider
        self.sep = QFrame()
        self.sep.setFrameShape(QFrame.Shape.HLine)
        sidebar_layout.addWidget(self.sep)
        sidebar_layout.addSpacing(10)

        # Nav buttons
        self.nav_btns = {}
        pages_info = [
            ("download", "⬇", "Tải Hóa Đơn"),
            ("tools",    "🔧", "Công Cụ"),
            ("extract",  "📊", "Trích Xuất"),
        ]
        for key, icon, text in pages_info:
            btn = NavBtn(icon, text)
            btn.clicked.connect(lambda _, k=key: self.select_page(k))
            sidebar_layout.addWidget(btn)
            self.nav_btns[key] = btn

        sidebar_layout.addSpacing(15)

        # CHANGELOG BOX - bo góc lớn hơn per spec
        self.changelog = QFrame()
        cl_layout = QVBoxLayout(self.changelog)
        cl_layout.setContentsMargins(10, 10, 10, 10)
        cl_layout.setSpacing(5)

        self.c_title = QLabel("● Update v3.2")
        self.c_title.setFont(F("small"))
        cl_layout.addWidget(self.c_title)

        self.c_text = QLabel(
            "• Ép chạy Headless nền 100%\n"
            "• Nâng cấp bẫy lỗi Traceback\n"
            "• Giao diện Tab Công cụ 3 cột\n"
            "• Tool Mappings (Tháng/Năm)"
        )
        self.c_text.setWordWrap(True)
        self.c_text.setFont(F("tiny"))
        cl_layout.addWidget(self.c_text)
        
        cl_layout.addSpacing(5)
        
        self.c_title_31 = QLabel("● Update v3.1")
        self.c_title_31.setFont(F("small"))
        cl_layout.addWidget(self.c_title_31)

        self.c_text_31 = QLabel(
            "• Tối ưu chống chặn Bot EVN\n"
            "• Dark / Light mode\n"
            "• Tự động chống trùng tên file"
        )
        self.c_text_31.setWordWrap(True)
        self.c_text_31.setFont(F("tiny"))
        cl_layout.addWidget(self.c_text_31)

        sidebar_layout.addWidget(self.changelog)

        sidebar_layout.addStretch()

        # Dark/Light toggle button - icon đơn sắc per spec
        theme_icon = "◐ Light" if self.is_dark else "◑ Dark"
        self.btn_theme = QPushButton(f"{theme_icon} Mode")
        self.btn_theme.setFont(F("tiny"))
        self.btn_theme.setFixedHeight(30)
        self.btn_theme.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_theme.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {T['text_muted']};
                border: 1px solid {T['border']};
                border-radius: 6px;
            }}
            QPushButton:hover {{
                color: {T['text_body']};
                border-color: {T['btn_primary']};
                background-color: {T['btn_primary']}15;
            }}
        """)
        self.btn_theme.clicked.connect(self.toggle_theme)
        sidebar_layout.addWidget(self.btn_theme)

        sidebar_layout.addSpacing(6)

        # Footer
        self.footer_top = QLabel("2026 © Developed by")
        self.footer_top.setFont(F("tiny"))
        self.footer_top.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(self.footer_top)

        self.footer_brand = QLabel("CUONGNM.HNM")
        self.footer_brand.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.footer_brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(self.footer_brand)

        root.addWidget(self.sidebar_frame)

        # ========================= CONTENT =========================
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: transparent;")

        self.pages = {
            "download": DownloadPage(self),
            "tools":    ToolsPage(self),
            "extract":  ExtractPage(self),
        }
        for page in self.pages.values():
            self.stack.addWidget(page)

        root.addWidget(self.stack)

        self.select_page("download")
        self.refresh_theme()

    def refresh_theme(self):
        T = get_theme()
        self.setStyleSheet(f"background-color: {T['bg_main']};")
        self.sidebar_frame.setStyleSheet(f"background-color: {T['sidebar_bg']};")
        self.logo_lbl.setStyleSheet(f"color: {T['text_highlight']};")
        self.ver_lbl.setStyleSheet(f"color: {T['text_muted']}; letter-spacing: 1px;")
        self.sep.setStyleSheet(f"color: {T['border']};")

        self.c_title.setStyleSheet(f"color: {T['btn_primary']}; font-weight: bold; border: none; background: transparent;")
        if hasattr(self, 'c_title_31'):
            self.c_title_31.setStyleSheet(f"color: {T['btn_primary']}; font-weight: bold; border: none; background: transparent;")
            
        label_color = T['text_body'] if current_mode == "light" else T['text_muted']
        self.c_text.setStyleSheet(f"color: {label_color}; border: none; background: transparent; line-height: 1.6;")
        if hasattr(self, 'c_text_31'):
            self.c_text_31.setStyleSheet(f"color: {label_color}; border: none; background: transparent; line-height: 1.6;")
        self.changelog.setStyleSheet(f"QFrame {{ background-color: {T['bg_card']}; border: 1px solid {T['border']}; border-radius: 10px; }}")

        self.footer_top.setStyleSheet(f"color: {T['text_muted']}; background: transparent;")
        self.footer_brand.setStyleSheet(f"color: {T['btn_primary']}; background: transparent; letter-spacing: 1px;")

        theme_icon = "◐ Light" if self.is_dark else "◑ Dark"
        self.btn_theme.setText(f"{theme_icon} Mode")
        self.btn_theme.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {T['text_muted']};
                border: 1px solid {T['border']};
                border-radius: 6px;
            }}
            QPushButton:hover {{
                color: {T['text_body']}; border-color: {T['btn_primary']}; background-color: {T['btn_primary']}15;
            }}
        """)

        def _update(w):
            if hasattr(w, "refresh_theme") and w != self:
                w.refresh_theme()
            for c in w.children():
                if isinstance(c, QWidget):
                    _update(c)
        _update(self.centralWidget())

    def select_page(self, key):
        for k, btn in self.nav_btns.items():
            btn.set_active(k == key)
        if key in self.pages:
            self.stack.setCurrentWidget(self.pages[key])

    def toggle_theme(self):
        global current_mode
        self.is_dark = not self.is_dark
        current_mode = "dark" if self.is_dark else "light"

        # Update styling thay vì xóa toàn bộ giao diện
        self.refresh_theme()


# =============================================================================
# ENTRY POINT
# =============================================================================
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Font mặc định toàn app
    app_font = QFont("Segoe UI", 9)
    app.setFont(app_font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
