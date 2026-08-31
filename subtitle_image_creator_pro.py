import sys
import re
import json
import shutil
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QPixmap, QImage
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QLabel,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QListWidget,
    QListWidgetItem,
    QFileDialog,
    QMessageBox,
    QSpinBox,
    QComboBox,
    QColorDialog,
    QCheckBox,
    QProgressBar,
    QGroupBox,
    QFormLayout,
)


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

APP_NAME = "Subtitle Image Creator Pro"

DEFAULT_WIDTH = 1920
DEFAULT_HEIGHT = 1080
DEFAULT_FONT_SIZE = 72
DEFAULT_OUTLINE_WIDTH = 3
DEFAULT_PADDING = 80

PROJECT_VERSION = "1.0"


# ============================================================
# DATA MODEL
# ============================================================

@dataclass
class Subtitle:
    number: int
    start: str
    end: str
    text: str


# ============================================================
# MAIN APPLICATION
# ============================================================

class SubtitleImageCreatorPro(QMainWindow):

    def __init__(self):
        super().__init__()

        # ----------------------------------------------------
        # Data
        # ----------------------------------------------------

        self.subtitles = []
        self.current_index = -1

        self.font_path = ""
        self.font_display_name = "System Default"

        self.text_color = "#FFFFFF"
        self.background_color = "#000000"
        self.outline_color = "#000000"

        self.output_folder = ""

        # ----------------------------------------------------
        # Window
        # ----------------------------------------------------

        self.setWindowTitle(APP_NAME)
        self.resize(1500, 900)

        self.build_ui()
        self.apply_style()
        self.update_color_buttons()
        self.update_preview()

    # ========================================================
    # UI
    # ========================================================

    def build_ui(self):

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(10)

        # ----------------------------------------------------
        # Header
        # ----------------------------------------------------

        header_layout = QHBoxLayout()

        title_layout = QVBoxLayout()

        title = QLabel("🎬 Subtitle Image Creator Pro")
        title.setObjectName("appTitle")

        description = QLabel(
            "Create high-quality PNG subtitle images from SRT files"
        )
        description.setObjectName("appDescription")

        title_layout.addWidget(title)
        title_layout.addWidget(description)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        load_button = QPushButton("📂 Load SRT")
        load_button.clicked.connect(self.load_srt)

        save_project_button = QPushButton("💾 Save Project")
        save_project_button.clicked.connect(self.save_project)

        load_project_button = QPushButton("📁 Load Project")
        load_project_button.clicked.connect(self.load_project)

        header_layout.addWidget(load_button)
        header_layout.addWidget(save_project_button)
        header_layout.addWidget(load_project_button)

        main_layout.addLayout(header_layout)

        # ----------------------------------------------------
        # Main Splitter
        # ----------------------------------------------------

        splitter = QSplitter(Qt.Horizontal)

        splitter.addWidget(self.create_subtitle_panel())
        splitter.addWidget(self.create_preview_panel())
        splitter.addWidget(self.create_settings_panel())

        splitter.setSizes([320, 750, 360])

        main_layout.addWidget(splitter)

        # ----------------------------------------------------
        # Output Folder
        # ----------------------------------------------------

        output_layout = QHBoxLayout()

        output_label = QLabel("Output Folder:")

        self.output_folder_edit = QLineEdit()
        self.output_folder_edit.setPlaceholderText(
            "Select a folder for exported PNG images..."
        )
        self.output_folder_edit.setReadOnly(True)

        browse_output_button = QPushButton("Browse")
        browse_output_button.clicked.connect(
            self.select_output_folder
        )

        output_layout.addWidget(output_label)
        output_layout.addWidget(
            self.output_folder_edit,
            1
        )
        output_layout.addWidget(browse_output_button)

        main_layout.addLayout(output_layout)

        # ----------------------------------------------------
        # Footer
        # ----------------------------------------------------

        footer_layout = QHBoxLayout()

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        self.status_label = QLabel("Ready")

        export_selected_button = QPushButton(
            "Export Selected"
        )
        export_selected_button.clicked.connect(
            self.export_selected
        )

        export_all_button = QPushButton(
            "🚀 Export All PNGs"
        )
        export_all_button.clicked.connect(
            self.export_all
        )

        footer_layout.addWidget(
            self.progress_bar,
            1
        )

        footer_layout.addWidget(
            self.status_label
        )

        footer_layout.addWidget(
            export_selected_button
        )

        footer_layout.addWidget(
            export_all_button
        )

        main_layout.addLayout(footer_layout)

    # ========================================================
    # LEFT PANEL
    # ========================================================

    def create_subtitle_panel(self):

        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("SUBTITLES")
        title.setObjectName("sectionTitle")

        layout.addWidget(title)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(
            "🔎 Search subtitles..."
        )
        self.search_box.textChanged.connect(
            self.filter_subtitles
        )

        layout.addWidget(self.search_box)

        self.subtitle_list = QListWidget()
        self.subtitle_list.currentRowChanged.connect(
            self.subtitle_selected
        )

        layout.addWidget(
            self.subtitle_list,
            1
        )

        # ----------------------------------------------------
        # Editor
        # ----------------------------------------------------

        editor_group = QGroupBox("Edit Subtitle")

        editor_layout = QVBoxLayout(editor_group)

        self.time_label = QLabel(
            "Start: --:--:--   End: --:--:--"
        )

        self.subtitle_editor = QTextEdit()
        self.subtitle_editor.setPlaceholderText(
            "Select a subtitle to edit..."
        )

        self.subtitle_editor.textChanged.connect(
            self.update_preview
        )

        save_button = QPushButton(
            "Save Subtitle Changes"
        )

        save_button.clicked.connect(
            self.save_subtitle_changes
        )

        editor_layout.addWidget(
            self.time_label
        )

        editor_layout.addWidget(
            self.subtitle_editor
        )

        editor_layout.addWidget(
            save_button
        )

        layout.addWidget(editor_group)

        return widget

    # ========================================================
    # PREVIEW PANEL
    # ========================================================

    def create_preview_panel(self):

        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("LIVE PREVIEW")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("sectionTitle")

        layout.addWidget(title)

        self.preview_label = QLabel()

        self.preview_label.setAlignment(
            Qt.AlignCenter
        )

        self.preview_label.setMinimumSize(
            QSize(500, 400)
        )

        self.preview_label.setObjectName(
            "preview"
        )

        layout.addWidget(
            self.preview_label,
            1
        )

        refresh_button = QPushButton(
            "🔄 Refresh Preview"
        )

        refresh_button.clicked.connect(
            self.update_preview
        )

        layout.addWidget(refresh_button)

        return widget

    # ========================================================
    # SETTINGS PANEL
    # ========================================================

    def create_settings_panel(self):

        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("STYLE SETTINGS")
        title.setObjectName("sectionTitle")

        layout.addWidget(title)

        # ----------------------------------------------------
        # Image Settings
        # ----------------------------------------------------

        image_group = QGroupBox(
            "Image Settings"
        )

        image_form = QFormLayout(
            image_group
        )

        self.width_spin = QSpinBox()
        self.width_spin.setRange(
            320,
            7680
        )
        self.width_spin.setValue(
            DEFAULT_WIDTH
        )

        self.height_spin = QSpinBox()
        self.height_spin.setRange(
            240,
            4320
        )
        self.height_spin.setValue(
            DEFAULT_HEIGHT
        )

        image_form.addRow(
            "Width:",
            self.width_spin
        )

        image_form.addRow(
            "Height:",
            self.height_spin
        )

        layout.addWidget(image_group)

        # ----------------------------------------------------
        # Font
        # ----------------------------------------------------

        font_group = QGroupBox("Font")

        font_form = QFormLayout(font_group)

        self.font_label = QLabel(
            self.font_display_name
        )

        choose_font_button = QPushButton(
            "Choose Font File"
        )

        choose_font_button.clicked.connect(
            self.choose_font_file
        )

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(
            10,
            500
        )

        self.font_size_spin.setValue(
            DEFAULT_FONT_SIZE
        )

        font_form.addRow(
            "Font:",
            self.font_label
        )

        font_form.addRow(
            "",
            choose_font_button
        )

        font_form.addRow(
            "Font Size:",
            self.font_size_spin
        )

        layout.addWidget(font_group)

        # ----------------------------------------------------
        # Colors
        # ----------------------------------------------------

        color_group = QGroupBox("Colors")
        color_layout = QVBoxLayout(color_group)

        self.text_color_button = QPushButton(
            "Choose Text Color"
        )

        self.text_color_button.clicked.connect(
            self.choose_text_color
        )

        self.background_color_button = QPushButton(
            "Choose Background Color"
        )

        self.background_color_button.clicked.connect(
            self.choose_background_color
        )

        self.transparent_check = QCheckBox(
            "Transparent Background"
        )

        self.transparent_check.stateChanged.connect(
            self.update_preview
        )

        color_layout.addWidget(
            self.text_color_button
        )

        color_layout.addWidget(
            self.background_color_button
        )

        color_layout.addWidget(
            self.transparent_check
        )

        layout.addWidget(color_group)

        # ----------------------------------------------------
        # Outline
        # ----------------------------------------------------

        outline_group = QGroupBox(
            "Text Outline"
        )

        outline_form = QFormLayout(
            outline_group
        )

        self.outline_width_spin = QSpinBox()
        self.outline_width_spin.setRange(
            0,
            50
        )

        self.outline_width_spin.setValue(
            DEFAULT_OUTLINE_WIDTH
        )

        self.outline_color_button = QPushButton(
            "Choose Outline Color"
        )

        self.outline_color_button.clicked.connect(
            self.choose_outline_color
        )

        outline_form.addRow(
            "Width:",
            self.outline_width_spin
        )

        outline_form.addRow(
            "Color:",
            self.outline_color_button
        )

        layout.addWidget(outline_group)

        # ----------------------------------------------------
        # Position
        # ----------------------------------------------------

        position_group = QGroupBox(
            "Text Position"
        )

        position_form = QFormLayout(
            position_group
        )

        self.horizontal_combo = QComboBox()

        self.horizontal_combo.addItems([
            "Left",
            "Center",
            "Right",
        ])

        self.horizontal_combo.setCurrentText(
            "Center"
        )

        self.vertical_combo = QComboBox()

        self.vertical_combo.addItems([
            "Top",
            "Center",
            "Bottom",
        ])

        self.vertical_combo.setCurrentText(
            "Bottom"
        )

        self.padding_spin = QSpinBox()

        self.padding_spin.setRange(
            0,
            500
        )

        self.padding_spin.setValue(
            DEFAULT_PADDING
        )

        position_form.addRow(
            "Horizontal:",
            self.horizontal_combo
        )

        position_form.addRow(
            "Vertical:",
            self.vertical_combo
        )

        position_form.addRow(
            "Padding:",
            self.padding_spin
        )

        layout.addWidget(position_group)

        layout.addStretch()

        # ----------------------------------------------------
        # Live Preview Connections
        # ----------------------------------------------------

        controls = [
            self.width_spin,
            self.height_spin,
            self.font_size_spin,
            self.outline_width_spin,
            self.padding_spin,
        ]

        for control in controls:
            control.valueChanged.connect(
                self.update_preview
            )

        self.horizontal_combo.currentTextChanged.connect(
            self.update_preview
        )

        self.vertical_combo.currentTextChanged.connect(
            self.update_preview
        )

        return widget

    # ========================================================
    # STYLING
    # ========================================================

    def apply_style(self):

        self.setStyleSheet("""
            QMainWindow {
                background-color: #202124;
            }

            QWidget {
                font-size: 13px;
            }

            QLabel#appTitle {
                font-size: 24px;
                font-weight: bold;
            }

            QLabel#appDescription {
                color: #888888;
            }

            QLabel#sectionTitle {
                font-size: 15px;
                font-weight: bold;
            }

            QLabel#preview {
                background-color: #151515;
                border: 1px solid #555555;
                border-radius: 6px;
            }

            QGroupBox {
                font-weight: bold;
                margin-top: 8px;
                padding-top: 10px;
            }

            QPushButton {
                padding: 7px;
            }

            QLineEdit,
            QTextEdit,
            QListWidget {
                border: 1px solid #777777;
                border-radius: 4px;
            }
        """)

    # ========================================================
    # COLOR BUTTONS
    # ========================================================

    def update_color_buttons(self):

        self.text_color_button.setText(
            f"Text Color: {self.text_color}"
        )

        self.background_color_button.setText(
            f"Background: {self.background_color}"
        )

        self.outline_color_button.setText(
            f"Outline: {self.outline_color}"
        )

    # ========================================================
    # FONT HANDLING
    # ========================================================

    def choose_font_file(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Choose Font",
            "",
            "Font Files (*.ttf *.otf *.ttc)"
        )

        if not filename:
            return

        try:

            # Test font before accepting it
            ImageFont.truetype(
                filename,
                self.font_size_spin.value()
            )

            self.font_path = filename

            self.font_display_name = (
                Path(filename).name
            )

            self.font_label.setText(
                self.font_display_name
            )

            self.status_label.setText(
                "Font loaded successfully"
            )

            self.update_preview()

        except Exception as error:

            QMessageBox.warning(
                self,
                "Font Error",
                f"Unable to load font:\n\n{error}"
            )

    def get_font(self, size):

        # User-selected font
        if self.font_path:

            try:

                return ImageFont.truetype(
                    self.font_path,
                    size
                )

            except Exception:
                pass

        # Common Linux / Windows fallback fonts
        candidates = [

            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",

            "/usr/share/fonts/truetype/liberation2/"
            "LiberationSans-Regular.ttf",

            "/usr/share/fonts/truetype/liberation/"
            "LiberationSans-Regular.ttf",

            "C:/Windows/Fonts/arial.ttf",
        ]

        for candidate in candidates:

            if Path(candidate).exists():

                try:

                    return ImageFont.truetype(
                        candidate,
                        size
                    )

                except Exception:
                    continue

        return ImageFont.load_default()

    # ========================================================
    # COLOR SELECTION
    # ========================================================

    def choose_text_color(self):

        color = QColorDialog.getColor(
            QColor(self.text_color),
            self
        )

        if color.isValid():

            self.text_color = color.name()

            self.update_color_buttons()
            self.update_preview()

    def choose_background_color(self):

        color = QColorDialog.getColor(
            QColor(self.background_color),
            self
        )

        if color.isValid():

            self.background_color = color.name()

            self.update_color_buttons()
            self.update_preview()

    def choose_outline_color(self):

        color = QColorDialog.getColor(
            QColor(self.outline_color),
            self
        )

        if color.isValid():

            self.outline_color = color.name()

            self.update_color_buttons()
            self.update_preview()

    # ========================================================
    # SRT PARSING
    # ========================================================

    def load_srt(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Subtitle File",
            "",
            "Subtitle Files (*.srt)"
        )

        if not filename:
            return

        try:

            content = Path(filename).read_text(
                encoding="utf-8-sig",
                errors="replace"
            )

            subtitles = self.parse_srt(content)

            if not subtitles:

                raise RuntimeError(
                    "No valid subtitles were found."
                )

            self.subtitles = subtitles

            self.current_index = -1

            self.populate_subtitle_list()

            self.status_label.setText(
                f"Loaded {len(self.subtitles)} subtitles"
            )

            self.progress_bar.setValue(0)

        except Exception as error:

            QMessageBox.critical(
                self,
                "Load Error",
                str(error)
            )

    def parse_srt(self, content):

        subtitles = []

        # Normalize line endings
        content = (
            content
            .replace("\r\n", "\n")
            .replace("\r", "\n")
        )

        blocks = re.split(
            r"\n\s*\n",
            content.strip()
        )

        fallback_number = 1

        for block in blocks:

            lines = [
                line.rstrip()
                for line in block.splitlines()
            ]

            if len(lines) < 2:
                continue

            number = fallback_number
            timing_index = 0

            # Standard numbered subtitle
            if lines[0].strip().isdigit():

                number = int(
                    lines[0].strip()
                )

                timing_index = 1

            if timing_index >= len(lines):
                continue

            timing = lines[timing_index]

            if "-->" not in timing:
                continue

            try:

                start, end = [
                    value.strip()
                    for value in timing.split(
                        "-->",
                        1
                    )
                ]

                text_lines = lines[
                    timing_index + 1:
                ]

                text = "\n".join(
                    text_lines
                ).strip()

                if not text:
                    continue

                subtitles.append(
                    Subtitle(
                        number=number,
                        start=start,
                        end=end,
                        text=text
                    )
                )

                fallback_number += 1

            except Exception:
                continue

        return subtitles

    # ========================================================
    # SUBTITLE LIST
    # ========================================================

    def populate_subtitle_list(self):

        self.subtitle_list.blockSignals(True)
        self.subtitle_list.clear()

        for index, subtitle in enumerate(
            self.subtitles
        ):

            preview = (
                subtitle.text
                .replace("\n", " ")
            )

            if len(preview) > 60:
                preview = preview[:57] + "..."

            item = QListWidgetItem(
                f"{subtitle.number:04d}  |  "
                f"{subtitle.start}  |  "
                f"{preview}"
            )

            # Store real subtitle index
            item.setData(
                Qt.UserRole,
                index
            )

            self.subtitle_list.addItem(
                item
            )

        self.subtitle_list.blockSignals(False)

        if self.subtitle_list.count() > 0:

            self.subtitle_list.setCurrentRow(0)

    def filter_subtitles(self):

        search = (
            self.search_box.text()
            .lower()
            .strip()
        )

        for row in range(
            self.subtitle_list.count()
        ):

            item = self.subtitle_list.item(
                row
            )

            subtitle_index = item.data(
                Qt.UserRole
            )

            subtitle = self.subtitles[
                subtitle_index
            ]

            searchable_text = (
                f"{subtitle.number} "
                f"{subtitle.start} "
                f"{subtitle.end} "
                f"{subtitle.text}"
            ).lower()

            item.setHidden(
                search not in searchable_text
            )

    def subtitle_selected(self, row):

        if row < 0:
            return

        item = self.subtitle_list.item(row)

        if not item:
            return

        subtitle_index = item.data(
            Qt.UserRole
        )

        if (
            subtitle_index is None
            or subtitle_index >= len(
                self.subtitles
            )
        ):
            return

        self.current_index = subtitle_index

        subtitle = self.subtitles[
            subtitle_index
        ]

        self.subtitle_editor.blockSignals(True)

        self.subtitle_editor.setPlainText(
            subtitle.text
        )

        self.subtitle_editor.blockSignals(False)

        self.time_label.setText(
            f"Start: {subtitle.start}    "
            f"End: {subtitle.end}"
        )

        self.update_preview()

    def save_subtitle_changes(self):

        if self.current_index < 0:

            QMessageBox.warning(
                self,
                "No Subtitle Selected",
                "Please select a subtitle first."
            )

            return

        text = (
            self.subtitle_editor
            .toPlainText()
            .strip()
        )

        if not text:

            QMessageBox.warning(
                self,
                "Empty Subtitle",
                "Subtitle text cannot be empty."
            )

            return

        self.subtitles[
            self.current_index
        ].text = text

        self.refresh_subtitle_list()

        self.status_label.setText(
            "Subtitle changes saved"
        )

    def refresh_subtitle_list(self):

        selected_index = self.current_index

        self.populate_subtitle_list()

        for row in range(
            self.subtitle_list.count()
        ):

            item = self.subtitle_list.item(row)

            if item.data(Qt.UserRole) == selected_index:

                self.subtitle_list.setCurrentRow(
                    row
                )

                break

        self.filter_subtitles()

    # ========================================================
    # TEXT WRAPPING
    # ========================================================

    def get_text_bbox(
        self,
        draw,
        text,
        font,
        stroke_width=0
    ):

        return draw.textbbox(
            (0, 0),
            text,
            font=font,
            stroke_width=stroke_width
        )

    def wrap_text(
        self,
        draw,
        text,
        font,
        max_width,
        stroke_width
    ):

        lines = []

        for paragraph in text.splitlines():

            paragraph = paragraph.strip()

            if not paragraph:

                lines.append("")
                continue

            words = paragraph.split()

            current_line = ""

            for word in words:

                test_line = (
                    word
                    if not current_line
                    else current_line + " " + word
                )

                bbox = self.get_text_bbox(
                    draw,
                    test_line,
                    font,
                    stroke_width
                )

                text_width = (
                    bbox[2] - bbox[0]
                )

                if (
                    text_width <= max_width
                    or not current_line
                ):

                    current_line = test_line

                else:

                    lines.append(
                        current_line
                    )

                    current_line = word

            if current_line:

                lines.append(
                    current_line
                )

        return lines or [""]

    # ========================================================
    # IMAGE RENDERING
    # ========================================================

    def render_subtitle_image(self, text):

        width = self.width_spin.value()
        height = self.height_spin.value()

        if self.transparent_check.isChecked():

            image = Image.new(
                "RGBA",
                (width, height),
                (0, 0, 0, 0)
            )

        else:

            image = Image.new(
                "RGBA",
                (width, height),
                self.background_color
            )

        draw = ImageDraw.Draw(image)

        font = self.get_font(
            self.font_size_spin.value()
        )

        padding = self.padding_spin.value()

        outline_width = (
            self.outline_width_spin.value()
        )

        max_width = max(
            50,
            width - (padding * 2)
        )

        lines = self.wrap_text(
            draw,
            text,
            font,
            max_width,
            outline_width
        )

        line_spacing = max(
            5,
            int(
                self.font_size_spin.value()
                * 0.20
            )
        )

        measurements = []

        for line in lines:

            bbox = self.get_text_bbox(
                draw,
                line,
                font,
                outline_width
            )

            line_width = (
                bbox[2] - bbox[0]
            )

            line_height = (
                bbox[3] - bbox[1]
            )

            measurements.append(
                (
                    line_width,
                    line_height,
                    bbox
                )
            )

        total_height = (
            sum(
                item[1]
                for item
                in measurements
            )
            +
            line_spacing
            * max(0, len(lines) - 1)
        )

        vertical = (
            self.vertical_combo.currentText()
        )

        if vertical == "Top":

            y = padding

        elif vertical == "Center":

            y = (
                height - total_height
            ) // 2

        else:

            y = (
                height
                - total_height
                - padding
            )

        horizontal = (
            self.horizontal_combo.currentText()
        )

        for index, line in enumerate(
            lines
        ):

            line_width, line_height, bbox = (
                measurements[index]
            )

            if horizontal == "Left":

                x = padding

            elif horizontal == "Right":

                x = (
                    width
                    - line_width
                    - padding
                )

            else:

                x = (
                    width - line_width
                ) // 2

            # Correct bounding-box offset
            draw_x = x - bbox[0]
            draw_y = y - bbox[1]

            draw.text(
                (draw_x, draw_y),
                line,
                font=font,
                fill=self.text_color,
                stroke_width=outline_width,
                stroke_fill=self.outline_color
            )

            y += (
                line_height
                + line_spacing
            )

        return image

    # ========================================================
    # PREVIEW
    # ========================================================

    def update_preview(self):

        try:

            if (
                self.current_index >= 0
                and
                self.current_index <
                len(self.subtitles)
            ):

                text = (
                    self.subtitle_editor
                    .toPlainText()
                )

                if not text.strip():

                    text = " "

            else:

                text = (
                    "Your subtitle preview "
                    "will appear here."
                )

            image = self.render_subtitle_image(
                text
            )

            preview_image = image.copy()

            preview_image.thumbnail(
                (900, 650)
            )

            if preview_image.mode != "RGBA":

                preview_image = (
                    preview_image.convert(
                        "RGBA"
                    )
                )

            data = preview_image.tobytes(
                "raw",
                "RGBA"
            )

            qimage = QImage(
                data,
                preview_image.width,
                preview_image.height,
                QImage.Format_RGBA8888
            )

            pixmap = QPixmap.fromImage(
                qimage.copy()
            )

            self.preview_label.setPixmap(
                pixmap
            )

        except Exception as error:

            self.preview_label.setText(
                f"Preview Error:\n{error}"
            )

    # ========================================================
    # OUTPUT FOLDER
    # ========================================================

    def select_output_folder(self):

        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder"
        )

        if folder:

            self.output_folder = folder

            self.output_folder_edit.setText(
                folder
            )

            self.status_label.setText(
                "Output folder selected"
            )

    def get_output_folder(self):

        if self.output_folder:

            folder = Path(
                self.output_folder
            )

            folder.mkdir(
                parents=True,
                exist_ok=True
            )

            return folder

        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder"
        )

        if not folder:
            return None

        self.output_folder = folder

        self.output_folder_edit.setText(
            folder
        )

        return Path(folder)

    # ========================================================
    # EXPORT SELECTED
    # ========================================================

    def export_selected(self):

        if self.current_index < 0:

            QMessageBox.warning(
                self,
                "No Subtitle Selected",
                "Please select a subtitle first."
            )

            return

        output_folder = (
            self.get_output_folder()
        )

        if not output_folder:
            return

        try:

            # Use editor text so current unsaved changes
            # can still be exported
            text = (
                self.subtitle_editor
                .toPlainText()
                .strip()
            )

            if not text:

                text = self.subtitles[
                    self.current_index
                ].text

            subtitle = self.subtitles[
                self.current_index
            ]

            image = self.render_subtitle_image(
                text
            )

            output_file = (
                output_folder
                /
                f"{subtitle.number:04d}.png"
            )

            image.save(
                output_file,
                "PNG"
            )

            self.progress_bar.setValue(100)

            self.status_label.setText(
                f"Exported: {output_file.name}"
            )

            QMessageBox.information(
                self,
                "Export Complete",
                f"PNG created successfully:\n\n"
                f"{output_file}"
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Export Error",
                str(error)
            )

    # ========================================================
    # EXPORT ALL
    # ========================================================

    def export_all(self):

        if not self.subtitles:

            QMessageBox.warning(
                self,
                "No Subtitles",
                "Please load an SRT file first."
            )

            return

        output_folder = (
            self.get_output_folder()
        )

        if not output_folder:
            return

        total = len(
            self.subtitles
        )

        self.progress_bar.setValue(0)

        try:

            for index, subtitle in enumerate(
                self.subtitles,
                start=1
            ):

                self.status_label.setText(
                    f"Rendering {index}/{total}"
                )

                image = self.render_subtitle_image(
                    subtitle.text
                )

                output_file = (
                    output_folder
                    /
                    f"{subtitle.number:04d}.png"
                )

                image.save(
                    output_file,
                    "PNG"
                )

                progress = int(
                    index
                    / total
                    * 100
                )

                self.progress_bar.setValue(
                    progress
                )

                QApplication.processEvents()

            self.status_label.setText(
                f"Completed: {total} images exported"
            )

            QMessageBox.information(
                self,
                "Export Complete",
                f"Successfully created "
                f"{total} PNG images.\n\n"
                f"Output folder:\n"
                f"{output_folder}"
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Export Error",
                str(error)
            )

    # ========================================================
    # SAVE PROJECT
    # ========================================================

    def save_project(self):

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Project",
            "subtitle_project.json",
            "JSON Files (*.json)"
        )

        if not filename:
            return

        if not filename.lower().endswith(
            ".json"
        ):

            filename += ".json"

        project = {

            "application": APP_NAME,

            "version": PROJECT_VERSION,

            "created": datetime.now().isoformat(),

            "subtitles": [
                asdict(subtitle)
                for subtitle
                in self.subtitles
            ],

            "settings": {

                "width":
                    self.width_spin.value(),

                "height":
                    self.height_spin.value(),

                "font_path":
                    self.font_path,

                "font_name":
                    self.font_display_name,

                "font_size":
                    self.font_size_spin.value(),

                "text_color":
                    self.text_color,

                "background_color":
                    self.background_color,

                "transparent_background":
                    self.transparent_check
                    .isChecked(),

                "outline_width":
                    self.outline_width_spin
                    .value(),

                "outline_color":
                    self.outline_color,

                "horizontal":
                    self.horizontal_combo
                    .currentText(),

                "vertical":
                    self.vertical_combo
                    .currentText(),

                "padding":
                    self.padding_spin.value(),

                "output_folder":
                    self.output_folder,
            }
        }

        try:

            Path(filename).write_text(
                json.dumps(
                    project,
                    indent=4,
                    ensure_ascii=False
                ),
                encoding="utf-8"
            )

            self.status_label.setText(
                "Project saved successfully"
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Save Error",
                str(error)
            )

    # ========================================================
    # LOAD PROJECT
    # ========================================================

    def load_project(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Load Project",
            "",
            "JSON Files (*.json)"
        )

        if not filename:
            return

        try:

            project = json.loads(
                Path(filename).read_text(
                    encoding="utf-8"
                )
            )

            subtitle_data = project.get(
                "subtitles",
                []
            )

            self.subtitles = [
                Subtitle(**item)
                for item
                in subtitle_data
            ]

            settings = project.get(
                "settings",
                {}
            )

            self.width_spin.setValue(
                settings.get(
                    "width",
                    DEFAULT_WIDTH
                )
            )

            self.height_spin.setValue(
                settings.get(
                    "height",
                    DEFAULT_HEIGHT
                )
            )

            self.font_size_spin.setValue(
                settings.get(
                    "font_size",
                    DEFAULT_FONT_SIZE
                )
            )

            self.text_color = settings.get(
                "text_color",
                "#FFFFFF"
            )

            self.background_color = settings.get(
                "background_color",
                "#000000"
            )

            self.outline_color = settings.get(
                "outline_color",
                "#000000"
            )

            self.outline_width_spin.setValue(
                settings.get(
                    "outline_width",
                    DEFAULT_OUTLINE_WIDTH
                )
            )

            self.transparent_check.setChecked(
                settings.get(
                    "transparent_background",
                    False
                )
            )

            self.horizontal_combo.setCurrentText(
                settings.get(
                    "horizontal",
                    "Center"
                )
            )

            self.vertical_combo.setCurrentText(
                settings.get(
                    "vertical",
                    "Bottom"
                )
            )

            self.padding_spin.setValue(
                settings.get(
                    "padding",
                    DEFAULT_PADDING
                )
            )

            # Font
            saved_font_path = settings.get(
                "font_path",
                ""
            )

            if (
                saved_font_path
                and
                Path(saved_font_path).exists()
            ):

                self.font_path = (
                    saved_font_path
                )

                self.font_display_name = (
                    settings.get(
                        "font_name",
                        Path(saved_font_path).name
                    )
                )

            else:

                self.font_path = ""

                self.font_display_name = (
                    "System Default"
                )

            self.font_label.setText(
                self.font_display_name
            )

            # Output Folder
            saved_output = settings.get(
                "output_folder",
                ""
            )

            if saved_output:

                self.output_folder = (
                    saved_output
                )

                self.output_folder_edit.setText(
                    saved_output
                )

            self.update_color_buttons()

            self.current_index = -1

            self.populate_subtitle_list()

            self.update_preview()

            self.status_label.setText(
                f"Project loaded: "
                f"{len(self.subtitles)} subtitles"
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Load Error",
                str(error)
            )


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

def main():

    app = QApplication(sys.argv)

    app.setApplicationName(
        APP_NAME
    )

    window = SubtitleImageCreatorPro()

    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()