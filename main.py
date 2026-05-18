import sys
import os
import json
import shutil
import requests
import re

from urllib.parse import urljoin

from functools import partial

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QFileDialog,
    QScrollArea,
    QFrame,
    QMessageBox,
    QGraphicsDropShadowEffect,
    QTextBrowser,
    QToolButton
)

from PySide6.QtCore import Qt, QUrl

from PySide6.QtGui import (
    QPixmap,
    QCursor,
    QIcon,
    QPainter,
    QPainterPath
)

from bs4 import BeautifulSoup


DATA_FILE = "data.json"
PHOTO_FOLDER = "PhotoG"


def load_data():
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


class SiteCard(QFrame):
    def __init__(
        self,
        name,
        image_path,
        click_callback,
        move_up_callback
    ):
        super().__init__()

        self.click_callback = click_callback
        self.move_up_callback = move_up_callback

        self.setFixedSize(300, 95)

        self.setObjectName("card")

        self.setCursor(
            QCursor(Qt.PointingHandCursor)
        )

        self.shadow = QGraphicsDropShadowEffect()

        self.shadow.setBlurRadius(20)
        self.shadow.setOffset(0, 0)

        self.setGraphicsEffect(
            self.shadow
        )

        self.setStyleSheet("""
            QFrame {
                border-radius: 18px;
                border: 2px solid #2b2b2b;
                background-color: #1a1a1a;
            }
        """)

        self.layout = QVBoxLayout(self)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setContentsMargins(0, 0, 0, 0)

        self.layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.background = QLabel()

        self.background.setFixedSize(
            300,
            95
        )

        self.background.setAlignment(
            Qt.AlignCenter
        )

        if image_path and os.path.exists(image_path):

            pixmap = QPixmap(image_path)

            scaled = pixmap.scaled(
                self.background.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )

            rounded = QPixmap(
                self.background.size()
            )

            rounded.fill(Qt.transparent)

            painter = QPainter(rounded)
            painter.setRenderHint(
                QPainter.Antialiasing
            )

            path = QPainterPath()
            path.addRoundedRect(
                0,
                0,
                self.background.width(),
                self.background.height(),
                18,
                18
            )

            painter.setClipPath(path)

            painter.drawPixmap(
                0,
                0,
                scaled
            )

            painter.end()

            self.background.setPixmap(
                rounded
            )

        self.background.setAttribute(
            Qt.WA_StyledBackground,
            True
        )

        self.overlay = QLabel(
            self.background
        )

        self.overlay.setGeometry(
            0,
            0,
            300,
            95
        )

        self.overlay.setStyleSheet("""
            background-color: rgba(0, 0, 0, 140);
            border-radius: 18px;
        """)

        self.title = QLabel(
            name,
            self.background
        )

        self.title.setStyleSheet("""
            color: white;
            font-size: 17px;
            font-weight: bold;
            background: transparent;
        """)

        self.title.move(20, 35)

        # Кнопка вверх
        self.up_button = QToolButton(
            self.background
        )

        self.up_button.setText("↑")

        self.up_button.setGeometry(
            265,
            0,
            35,
            95
        )

        self.up_button.clicked.connect(
            self.move_up_callback
        )

        self.up_button.hide()

        self.up_button.setStyleSheet("""
            QToolButton {
                background-color: rgba(50,50,50,180);
                border: none;
                color: white;
                font-size: 22px;
                border-top-right-radius: 18px;
                border-bottom-right-radius: 18px;
            }

            QToolButton:hover {
                background-color: rgba(74,140,255,180);
            }
        """)

        self.setStyleSheet("""
            QFrame {
                border-radius: 18px;
                border: 2px solid #2b2b2b;
                background-color: #1a1a1a;
            }
            
            QLabel#background {
                border-radius: 18px;
            }
        """)

        self.layout.addWidget(
            self.background
        )

    def set_selected(self, value):
        if value:
            self.setStyleSheet("""
                QFrame {
                    border-radius: 18px;
                    border: 2px solid #4a8cff;
                    background-color: #25344d;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    border-radius: 18px;
                    border: 2px solid #2b2b2b;
                    background-color: #1a1a1a;
                }
            """)

    def enterEvent(self, event):
        self.shadow.setBlurRadius(40)
        self.up_button.show()

    def leaveEvent(self, event):
        self.shadow.setBlurRadius(20)
        self.up_button.hide()

    def mousePressEvent(self, event):

        # Якщо клікнули по кнопці ↑
        if self.up_button.geometry().contains(
            event.pos()
        ):
            return

        self.click_callback()

class ClickableImage(QLabel):
    def __init__(self, click_callback):
        super().__init__()

        self.click_callback = click_callback

    def mousePressEvent(self, event):
        self.click_callback()

class HtmlViewer(QScrollArea):
    def __init__(self):
        super().__init__()

        self.setWidgetResizable(True)

        self.browser = QTextBrowser()

        self.browser.setOpenExternalLinks(True)

        self.browser.setStyleSheet("""
            QTextBrowser {
                background-color: #111111;
                color: white;
                border-radius: 18px;
                padding: 20px;
                border: none;
                font-size: 15px;
            }
        """)

        self.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #111111;
            }
        """)

        self.setWidget(
            self.browser
        )

    def load_url(self, url, site_name):

        safe_name = re.sub(r'[\\/*?:"<>|]', "_", site_name)

        image_folder = os.path.join(
            PHOTO_FOLDER,
            safe_name
        )

        os.makedirs(
            image_folder,
            exist_ok=True
        )

        cache_file = os.path.join(
            image_folder,
            "cached_page.html"
        )

        if os.path.exists(cache_file):

            with open(cache_file, "r", encoding="utf-8") as f:
                cached_html = f.read()

            self.browser.setHtml(cached_html)

            return

        try:
            headers = {
                "User-Agent": "Mozilla/5.0"
            }

            response = requests.get(
                url,
                headers=headers,
                timeout=15
            )

            html = response.text

            soup = BeautifulSoup(
                html,
                "html.parser"
            )

            for tag in soup([
                "script",
                "noscript"
            ]):
                tag.decompose()

            # Папка для фото
            safe_name = re.sub(r'[\\/*?:"<>|]', "_", site_name)

            image_folder = os.path.join(
                PHOTO_FOLDER,
                safe_name
            )

            os.makedirs(
                image_folder,
                exist_ok=True
            )

            # Завантаження картинок
            for index, img in enumerate(soup.find_all("img")):

                src = img.get("src")

                if not src:
                    continue

                try:
                    absolute_url = urljoin(url, src)

                    img_response = requests.get(
                        absolute_url,
                        headers=headers,
                        timeout=10
                    )

                    if img_response.status_code != 200:
                        continue

                    ext = ".jpg"

                    if ".png" in absolute_url:
                        ext = ".png"

                    elif ".webp" in absolute_url:
                        ext = ".webp"

                    elif ".jpeg" in absolute_url:
                        ext = ".jpeg"

                    file_name = f"img_{index}{ext}"

                    local_path = os.path.join(
                        image_folder,
                        file_name
                    )

                    with open(local_path, "wb") as f:
                        f.write(img_response.content)

                    img["src"] = local_path.replace("\\", "/")

                except:
                    pass

            base_style = """
            <style>

                html, body {
                    background-color: #111111;
                    color: white;
                    font-family: Segoe UI;
                    padding: 25px;
                    line-height: 1.6;
                }

                p, span, div, li, td, th {
                    color: white;
                }

                img {
                    max-width: 100%;
                    border-radius: 12px;
                    margin-top: 10px;
                    margin-bottom: 10px;
                }

                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                    margin-bottom: 20px;
                    background-color: #1b1b1b;
                }

                th, td {
                    border: 1px solid #444;
                    padding: 10px;
                    background-color: #1b1b1b;
                }

                h1, h2, h3 {
                    color: #4a8cff;
                }

                a {
                    color: #4a8cff;
                    text-decoration: none;
                }

                pre {
                    background: #222;
                    padding: 15px;
                    border-radius: 10px;
                    overflow-x: auto;
                }

                code {
                    color: #7dd3fc;
                }

            </style>
            """

            final_html = f"""
            {base_style}
            {str(soup)}
            """

            with open(cache_file, "w", encoding="utf-8") as f:
                f.write(final_html)

            self.browser.setHtml(final_html)

        except Exception as e:
            self.browser.setHtml(f"""
                <h1 style='color:red;'>
                    Помилка завантаження
                </h1>

                <p>{str(e)}</p>
            """)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(
            QIcon("icon.ico")
        )

        self.setWindowTitle(
            "Gaming Guide Launcher"
        )

        self.setMinimumSize(
            1400,
            800
        )

        self.data = load_data()

        self.current_index = None
        self.edit_mode = False

        self.cards = []

        self.central = QWidget()

        self.setCentralWidget(
            self.central
        )

        self.setStyleSheet("""
            QMainWindow {
                background-color: #111111;
            }

            QLabel {
                color: white;
            }

            QLineEdit {
                background: #1b1b1b;
                border: 2px solid #2f2f2f;
                border-radius: 16px;
                padding: 12px;
                color: white;
                font-size: 14px;
            }

            QLineEdit:focus {
                border: 2px solid #4a8cff;
            }

            QPushButton {
                background-color: #1f1f1f;
                border: 2px solid #2d2d2d;
                border-radius: 16px;
                color: white;
                font-size: 14px;
                padding: 12px;
            }

            QPushButton:hover {
                border: 2px solid #4a8cff;
                background-color: #2a2a2a;
            }
        """)

        self.main_layout = QHBoxLayout(
            self.central
        )

        self.create_left_panel()
        self.create_right_panel()

        self.refresh_cards()

        self.showMaximized()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F11:

            if self.isMaximized():
                self.showNormal()
            else:
                self.showMaximized()

        super().keyPressEvent(event)

    def resizeEvent(self, event):
        if hasattr(self, "settings_button"):

            self.settings_button.move(
                self.width() - 100,
                self.height() - 110
            )

        super().resizeEvent(event)

    def create_left_panel(self):
        self.left_widget = QWidget()

        self.left_widget.setFixedWidth(
            350
        )

        layout = QVBoxLayout(
            self.left_widget
        )

        self.image_label = ClickableImage(
            self.change_image
        )

        self.image_label.setFixedSize(
            310,
            190
        )

        self.image_label.setAlignment(
            Qt.AlignCenter
        )

        self.set_placeholder()

        layout.addWidget(
            self.image_label,
            alignment=Qt.AlignCenter
        )

        self.scroll_area = QScrollArea()

        self.scroll_area.setWidgetResizable(
            True
        )

        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)

        self.scroll_content = QWidget()

        self.scroll_content.setStyleSheet("""
            QWidget {
                background-color: #111111;
            }
        """)

        self.cards_layout = QVBoxLayout(
            self.scroll_content
        )

        self.cards_layout.setSpacing(14)

        self.cards_layout.setContentsMargins(
            10,
            10,
            10,
            10
        )

        self.cards_layout.addStretch()

        self.scroll_area.setWidget(
            self.scroll_content
        )

        layout.addWidget(
            self.scroll_area
        )

        button_layout = QHBoxLayout()

        self.add_button = QPushButton(
            "Додати"
        )

        self.add_button.clicked.connect(
            self.create_site
        )

        self.delete_button = QPushButton(
            "Видалити"
        )

        self.delete_button.clicked.connect(
            self.delete_site
        )

        button_layout.addWidget(
            self.add_button
        )

        button_layout.addWidget(
            self.delete_button
        )

        layout.addLayout(
            button_layout
        )

        self.main_layout.addWidget(
            self.left_widget
        )

    def create_right_panel(self):
        self.right_widget = QWidget()

        layout = QVBoxLayout(
            self.right_widget
        )

        self.editor_widget = QWidget()

        editor_layout = QVBoxLayout(
            self.editor_widget
        )

        title = QLabel(
            "Редагування вкладки"
        )

        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
        """)

        editor_layout.addWidget(
            title
        )

        self.url_input = QLineEdit()

        self.url_input.setPlaceholderText(
            "Введіть URL..."
        )

        self.name_input = QLineEdit()

        self.name_input.setPlaceholderText(
            "Назва вкладки..."
        )

        editor_layout.addWidget(
            QLabel("URL:")
        )

        editor_layout.addWidget(
            self.url_input
        )

        editor_layout.addWidget(
            QLabel("Назва:")
        )

        editor_layout.addWidget(
            self.name_input
        )

        self.save_button = QPushButton(
            "Створити"
        )

        self.save_button.clicked.connect(
            self.save_or_update_site
        )

        editor_layout.addWidget(
            self.save_button
        )

        layout.addWidget(
            self.editor_widget
        )

        self.viewer = HtmlViewer()

        layout.addWidget(
            self.viewer,
            stretch=1
        )

        self.main_layout.addWidget(
            self.right_widget,
            stretch=1
        )

        self.settings_button = QPushButton(
            "⚙"
        )

        self.settings_button.setParent(
            self.central
        )

        self.settings_button.setFixedSize(
            65,
            65
        )

        self.settings_button.clicked.connect(
            self.enable_edit_mode
        )

        self.settings_button.setStyleSheet("""
            QPushButton {
                background-color: #202020;
                border-radius: 32px;
                font-size: 26px;
                border: 2px solid #333333;
            }

            QPushButton:hover {
                border: 2px solid #4a8cff;
                background-color: #2b2b2b;
            }
        """)

        self.editor_widget.hide()

    def set_placeholder(self):

        self.image_label.setPixmap(
            QPixmap()
        )

        self.image_label.setText("+")

        self.image_label.setStyleSheet("""
            background-color: #2b2b2b;
            border-radius: 20px;
            border: 3px dashed #555555;
            color: #888888;
            font-size: 48px;
            font-weight: bold;
        """)

    def create_site(self):
        self.current_index = None

        self.edit_mode = False

        self.url_input.clear()

        self.name_input.clear()

        self.save_button.setText(
            "Створити"
        )

        self.viewer.browser.setHtml("")

        self.set_placeholder()

        self.editor_widget.show()

    def save_or_update_site(self):
        url = self.url_input.text().strip()
        name = self.name_input.text().strip()

        if not url or not name:
            QMessageBox.warning(
                self,
                "Помилка",
                "Заповніть всі поля"
            )
            return

        if not url.startswith(
                ("http://", "https://")):

            url = "https://" + url

        if self.edit_mode and self.current_index is not None:

            # Беремо стару назву ДО зміни
            old_name = self.data[self.current_index]["name"]

            # Якщо назва змінилась — видалити стару папку
            if old_name != name:

                safe_name = re.sub(
                    r'[\\/*?:"<>|]',
                    "_",
                    old_name
                )

                folder_path = os.path.join(
                    PHOTO_FOLDER,
                    safe_name
                )

                if os.path.exists(folder_path):
                    shutil.rmtree(folder_path)

            self.data[self.current_index]["url"] = url
            self.data[self.current_index]["name"] = name

        else:
            self.data.append({
                "name": name,
                "url": url,
                "image": ""
            })

        save_data(self.data)

        self.refresh_cards()

        self.select_site(
            len(self.data) - 1
            if not self.edit_mode
            else self.current_index
        )

        self.edit_mode = False

        self.save_button.setText(
            "Створити"
        )

        self.editor_widget.hide()

    def refresh_cards(self):

        self.cards = []

        # Повністю очищаємо layout
        while self.cards_layout.count():

            item = self.cards_layout.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

        # Створюємо карточки заново
        for index, item in enumerate(self.data):

            card = SiteCard(
                item["name"],
                item.get("image", ""),
                click_callback=partial(self.select_site, index),
                move_up_callback=partial(self.move_card_up, index)
            )

            self.cards.append(card)

            self.cards_layout.addWidget(card)

        # Stretch завжди внизу
        self.cards_layout.addStretch()

    def select_site(self, index):
        self.current_index = index

        for i, card in enumerate(self.cards):
            card.set_selected(i == index)

        item = self.data[index]

        self.url_input.setText(
            item["url"]
        )

        self.name_input.setText(
            item["name"]
        )

        self.viewer.load_url(
            item["url"],
            item["name"]
        )

        image_path = item.get(
            "image",
            ""
        )

        if image_path and os.path.exists(image_path):

            pixmap = QPixmap(
                image_path
            )

            scaled = pixmap.scaled(
                310,
                190,
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )

            self.image_label.setPixmap(
                scaled
            )

            self.image_label.setStyleSheet("""
                border-radius: 20px;
                border: 2px solid #333333;
                background-color: #111111;
            """)

        else:
            self.set_placeholder()

        self.editor_widget.hide()

    def enable_edit_mode(self):
        if self.current_index is None:
            return

        self.edit_mode = True

        self.save_button.setText(
            "Змінити"
        )

        self.editor_widget.show()

    def change_image(self):
        if self.current_index is None:
            return

        photo_dir = os.path.join(
            os.getcwd(),
            PHOTO_FOLDER
        )

        os.makedirs(
            photo_dir,
            exist_ok=True
        )

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Виберіть фото",
            photo_dir,
            "Images (*.png *.jpg *.jpeg)"
        )

        if not file_path:
            return

        file_name = os.path.basename(
            file_path
        )

        destination = os.path.join(
            PHOTO_FOLDER,
            file_name
        )

        if os.path.abspath(file_path) != os.path.abspath(destination):
            shutil.copy(file_path, destination)

        self.data[self.current_index]["image"] = destination

        save_data(self.data)

        self.refresh_cards()

        self.select_site(
            self.current_index
        )

    def move_card_up(self, index):

        if index <= 0:
            return

        # Міняємо місцями в data
        self.data[index], self.data[index - 1] = (
            self.data[index - 1],
            self.data[index]
        )

        save_data(self.data)

        # Перемальовуємо UI
        self.refresh_cards()

        # Виділяємо нову позицію
        self.current_index = index - 1
        self.select_site(self.current_index)

    def delete_site(self):
        if self.current_index is None:
            return

        site_name = self.data[self.current_index]["name"]

        safe_name = re.sub(r'[\\/*?:"<>|]', "_", site_name)

        folder_path = os.path.join(
            PHOTO_FOLDER,
            safe_name
        )

        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)

        del self.data[
            self.current_index
        ]

        save_data(self.data)

        self.current_index = None

        self.viewer.browser.setHtml("")

        self.refresh_cards()

        self.set_placeholder()

        self.url_input.clear()

        self.name_input.clear()

        self.editor_widget.hide()


app = QApplication(sys.argv)

window = MainWindow()

window.show()

sys.exit(app.exec())
