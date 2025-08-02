import sys
import os
import json
import subprocess
import uuid
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QMainWindow, QWidget,
    QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QScrollArea,
    QMessageBox, QSpacerItem, QSizePolicy,
    #QLineEdit, QPlainTextEdit
)
from PySide6.QtGui import QIcon, QAction, QPixmap, QClipboard
from PySide6.QtCore import Qt, QSize


CONFIG_PATH = "config.json"
DEFAULT_CONFIG = {
    "window": {"x": 100, "y": 100, "width": 400, "height": 600, "always_on_top": False},
    "paths": {"thumbs_dir": "thumbs", "items_dir": "items"}
}


def load_config():
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)


def save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)


def generate_thumbnail(input_path, output_path):
    try:
        subprocess.run([
            "ffmpeg", "-y", "-i", str(input_path),
            "-vf", "scale=160:-1",
            "-vframes", "1",
            str(output_path)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print("FFmpeg failed:", e)


class ItemWidget(QWidget):
    def __init__(self, content_path, is_image, parent_window):
        super().__init__()
        self.content_path = Path(content_path)
        self.is_image = is_image
        self.parent_window = parent_window

        layout = QHBoxLayout()

        if is_image:
            thumb_path = Path(config["paths"]["thumbs_dir"]) / (self.content_path.stem + "_thumb.jpg")
            pixmap = QPixmap(str(thumb_path)) if thumb_path.exists() else QPixmap(str(self.content_path))
            label = QLabel()
            label.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio))
        else:
            label = QLabel(self.content_path.read_text(encoding='utf-8').strip()[:50] + "...")
            label.setWordWrap(True)

        layout.addWidget(label, stretch=1)

        # btn_copy = QPushButton("Copy")
        btn_copy = QPushButton()
        btn_copy.setIcon(QIcon("icons/copy.png"))
        btn_copy.setToolTip("Copy to clipboard")
        btn_copy.setIconSize(QSize(24, 24))
        btn_copy.clicked.connect(self.copy_to_clipboard)
        layout.addWidget(btn_copy)

        # btn_delete = QPushButton("Delete")
        btn_delete = QPushButton()        
        btn_delete.setIcon(QIcon("icons/delete.png"))
        btn_delete.setToolTip("Delete item")
        btn_delete.setIconSize(QSize(24, 24))
        btn_delete.clicked.connect(self.delete_self)
        layout.addWidget(btn_delete)

        verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(verticalSpacer)

        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(20)

        self.setLayout(layout)

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        if self.is_image:
            pixmap = QPixmap(str(self.content_path))
            clipboard.setPixmap(pixmap)
        else:
            text = self.content_path.read_text(encoding='utf-8').strip()
            clipboard.setText(text)

    def delete_self(self):
        try:
            self.content_path.unlink(missing_ok=True)
            thumb = Path(config["paths"]["thumbs_dir"]) / (self.content_path.stem + "_thumb.jpg")
            thumb.unlink(missing_ok=True)
            self.setParent(None)
        except Exception as e:
            print("Failed to delete:", e)


class MainWindow(QMainWindow):
    def __init__(self, icon):
        super().__init__()
        self.icon = icon
        self.setWindowTitle("Manual Clipboard Manager")
        self.setWindowIcon(icon)

        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setAlignment(Qt.AlignTop)

        # Central layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Input line and Add button
        input_layout = QHBoxLayout()
        # self.input_line = QLineEdit()
        self.input_line = QTextEdit()
        self.input_line.setMinimumHeight(10)
        btn_add = QPushButton("Add")
        btn_add.setMinimumHeight(50)
        btn_add.clicked.connect(self.add_text_item)
        input_layout.addWidget(self.input_line)
        input_layout.addWidget(btn_add)

        btn_paste_img = QPushButton("Paste Image")
        btn_paste_img.clicked.connect(self.paste_image_from_clipboard)
        layout.addLayout(input_layout)
        layout.addWidget(btn_paste_img)

        # Scroll area
        scroll_area = QScrollArea()
        scroll_container = QWidget()
        scroll_container.setLayout(self.scroll_layout)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_container)

        layout.addWidget(scroll_area)
        self.setCentralWidget(central_widget)

        # Load layout from config
        win_cfg = config["window"]
        self.setGeometry(win_cfg["x"], win_cfg["y"], win_cfg["width"], win_cfg["height"])
        if win_cfg.get("always_on_top"):
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)

        self.load_items()

        # Menu bar: Always on top
        view_menu = self.menuBar().addMenu("View")
        self.always_on_top_action = QAction("Always on Top", self, checkable=True)
        self.always_on_top_action.setChecked(win_cfg.get("always_on_top", False))
        self.always_on_top_action.toggled.connect(self.toggle_always_on_top)
        view_menu.addAction(self.always_on_top_action)

    def closeEvent(self, event):
        geo = self.geometry()
        config["window"].update({
            "x": geo.x(), "y": geo.y(),
            "width": geo.width(), "height": geo.height(),
            "always_on_top": self.always_on_top_action.isChecked()
        })
        save_config(config)
        super().closeEvent(event)

    def toggle_always_on_top(self, enabled):
        flags = self.windowFlags()
        self.setWindowFlags(flags | Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint if enabled else flags & ~Qt.WindowStaysOnTopHint)
        self.show()        

    def add_text_item(self):
        # text = self.input_line.text().strip()
        # text = self.input_line.toPlainText().strip()
        text = self.input_line.toMarkdown().strip()
        clipboard = QApplication.clipboard()

        if text:
            file_path = Path(config["paths"]["items_dir"]) / f"{uuid.uuid4().hex}.md"
            file_path.write_text(text, encoding='utf-8')
            self.add_item_widget(file_path, is_image=False)
            self.input_line.clear()
        else:
            # Try to get from clipboard
            clip_text = clipboard.text().strip()
            clip_image = clipboard.image()

            if clip_text:
                file_path = Path(config["paths"]["items_dir"]) / f"{uuid.uuid4().hex}.md"
                file_path.write_text(clip_text, encoding='utf-8')
                self.add_item_widget(file_path, is_image=False)
            elif not clip_image.isNull():
                file_path = Path(config["paths"]["items_dir"]) / f"{uuid.uuid4().hex}.png"
                clip_image.save(str(file_path))
                thumb_path = Path(config["paths"]["thumbs_dir"]) / (file_path.stem + "_thumb.jpg")
                generate_thumbnail(file_path, thumb_path)
                self.add_item_widget(file_path, is_image=True)
            else:
                QMessageBox.information(self, "Clipboard Empty", "No text or image in clipboard.")


    def paste_image_from_clipboard(self):
        clipboard = QApplication.clipboard()
        image = clipboard.image()
        if image.isNull():
            QMessageBox.warning(self, "No Image", "No image data in clipboard.")
            return
        file_path = Path(config["paths"]["items_dir"]) / f"{uuid.uuid4().hex}.png"
        image.save(str(file_path))
        thumb_path = Path(config["paths"]["thumbs_dir"]) / (file_path.stem + "_thumb.jpg")
        generate_thumbnail(file_path, thumb_path)
        self.add_item_widget(file_path, is_image=True)

    def add_item_widget(self, path, is_image):
        widget = ItemWidget(path, is_image, self)
        self.scroll_layout.addWidget(widget)

    def load_items(self):
        items_dir = Path(config["paths"]["items_dir"])
        for file in sorted(items_dir.glob("*")):
            is_image = file.suffix.lower() in [".png", ".jpg", ".jpeg", ".bmp"]
            self.add_item_widget(file, is_image=is_image)


class TrayApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setQuitOnLastWindowClosed(False)

        icon = QIcon("icon2.ico")
        self.setWindowIcon(icon)
        self.window = MainWindow(icon)

        # Tray icon
        self.tray_icon = QSystemTrayIcon(icon)
        self.tray_icon.setToolTip("Clipboard Manager")
        self.tray_icon.activated.connect(self.on_tray_activated)

        menu = QMenu()
        menu.addAction("Toggle Window", self.window.toggle)
        menu.addSeparator()
        menu.addAction("Exit", self.quit)
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

        QApplication.instance().tray_icon = self.tray_icon

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.window.toggle()

    def quit(self):
        save_config(config)
        super().quit()


# Ensure folders exist
config = load_config()
Path(config["paths"]["items_dir"]).mkdir(parents=True, exist_ok=True)
Path(config["paths"]["thumbs_dir"]).mkdir(parents=True, exist_ok=True)

# Add toggle method to window
def toggle(self):
    if self.isVisible():
        self.hide()
    else:
        self.show()
        self.activateWindow()
MainWindow.toggle = toggle

if __name__ == "__main__":
    app = TrayApp(sys.argv)
    sys.exit(app.exec())
