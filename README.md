# 🎬 SubtitleCanvas

A modern desktop application for converting **SRT subtitle files into beautifully styled PNG subtitle images**.

Built with **Python**, **PySide6**, and **Pillow**, SubtitleCanvas provides an easy visual workflow for loading subtitles, editing text, designing subtitle styles, previewing the results, and exporting individual or complete subtitle image sequences.

---

## ✨ Features

### 📂 SRT Subtitle Support

- Load standard `.srt` subtitle files
- Parse subtitle numbers
- Read start and end timestamps
- Support multi-line subtitle text
- Browse all loaded subtitles in a list
- Search through subtitles quickly

### ✏️ Subtitle Editing

- Select individual subtitles
- Edit subtitle text directly
- Save changes to the loaded subtitle list
- Preview edited text before exporting

### 🖼️ Subtitle Image Generation

Generate one PNG image for each subtitle.

Example workflow:

    movie.srt
        │
        ▼
    SubtitleCanvas
        │
        ▼
    0001.png
    0002.png
    0003.png
    0004.png

Each subtitle can be exported as a high-quality PNG image.

---

## 🎨 Visual Styling

SubtitleCanvas provides controls for customizing subtitle appearance.

### Image Settings

- Adjustable image width
- Adjustable image height
- High-resolution output support

Example resolutions:

- 1920 × 1080
- 1280 × 720
- 1080 × 1920

---

### 🔤 Font Support

- Choose `.ttf` font files
- Choose `.otf` font files
- Choose `.ttc` font collections
- Adjustable font size
- System font fallback

Selected font files are used directly by Pillow for subtitle image rendering.

---

### 🌈 Colour Controls

Customize:

- Text colour
- Background colour
- Text outline colour

A transparent background mode is also available.

---

### ✨ Text Outline

Add an outline around subtitle text to improve readability.

Controls include:

- Outline width
- Outline colour

---

### 📐 Text Positioning

Control subtitle placement using:

- Left alignment
- Centre alignment
- Right alignment
- Top positioning
- Centre positioning
- Bottom positioning
- Adjustable padding

---

### 📝 Automatic Word Wrapping

SubtitleCanvas automatically wraps long subtitle text so that it fits inside the configured image width.

Multi-line subtitles are also supported.

---

## 👁️ Live Preview

The application provides a live preview of the subtitle image.

The preview updates when changing:

- Subtitle text
- Font size
- Image dimensions
- Text position
- Padding
- Outline settings
- Background settings
- Colours

This allows you to experiment with the subtitle design before exporting.

---

## 📤 Export Options

### Export Selected Subtitle

Export the currently selected subtitle as an individual PNG image.

Example:

    0001.png

### Export All Subtitles

Generate an entire sequence:

    0001.png
    0002.png
    0003.png
    0004.png
    0005.png

The export process includes:

- Progress tracking
- Status updates
- Error handling
- Automatic output folder creation

---

## 💾 Project Save and Load

SubtitleCanvas can save your work as a JSON project file.

A project stores:

- Subtitle text
- Subtitle timing
- Image width
- Image height
- Font settings
- Font size
- Text colour
- Background colour
- Transparent background setting
- Outline width
- Outline colour
- Horizontal alignment
- Vertical alignment
- Padding
- Output folder

This allows you to continue working later without reconfiguring your design.

---

# 🖥️ Application Workflow

    ┌──────────────┐
    │   Load SRT   │
    └──────┬───────┘
           │
           ▼
    ┌───────────────────┐
    │ Browse Subtitles  │
    └─────────┬─────────┘
              │
              ▼
    ┌───────────────────┐
    │ Edit Subtitle     │
    └─────────┬─────────┘
              │
              ▼
    ┌───────────────────┐
    │ Design Appearance │
    │ Font • Colour     │
    │ Outline • Position│
    └─────────┬─────────┘
              │
              ▼
    ┌───────────────────┐
    │   Live Preview    │
    └─────────┬─────────┘
              │
              ▼
    ┌───────────────────┐
    │ Export PNG Images │
    └───────────────────┘

---

# 📁 Project Structure

    SubtitleCanvas/
    │
    ├── subtitle_image_creator_pro.py
    │
    ├── README.md
    ├── requirements.txt
    ├── .gitignore
    │
    └── examples/
        └── sample.srt

---

# 🚀 Installation

## 1. Clone the Repository

```bash
git clone git@github.com:Fanu2/SubtitleCanvas.git
```

Enter the project directory:

```bash
cd SubtitleCanvas
```

---

## 2. Create a Virtual Environment

```bash
python3 -m venv .venv
```

Activate it on Linux:

```bash
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Running the Application

Start SubtitleCanvas with:

```bash
python3 subtitle_image_creator_pro.py
```

The main application window will open.

---

# 📄 Example SRT File

The included sample file can be found at:

    examples/sample.srt

Example SRT format:

```srt
1
00:00:01,000 --> 00:00:05,000
Some people enter your life...
and quietly change everything.

2
00:00:06,000 --> 00:00:10,000
Then there was you.

3
00:00:11,000 --> 00:00:15,000
A beautiful surprise
I never knew I was waiting for.
```

---

# 🛠️ Requirements

SubtitleCanvas requires:

- Python 3.10 or later
- PySide6
- Pillow

Dependencies:

```text
PySide6>=6.8
Pillow>=10.0
```

---

# 🧩 Current Capabilities

| Feature | Status |
|---|---|
| Load SRT files | ✅ |
| Parse subtitle timing | ✅ |
| Multi-line subtitles | ✅ |
| Subtitle search | ✅ |
| Subtitle editing | ✅ |
| Live preview | ✅ |
| PNG generation | ✅ |
| Batch PNG export | ✅ |
| Individual PNG export | ✅ |
| Font file selection | ✅ |
| TTF font support | ✅ |
| OTF font support | ✅ |
| Text colour | ✅ |
| Background colour | ✅ |
| Transparent background | ✅ |
| Text outline | ✅ |
| Position controls | ✅ |
| Padding controls | ✅ |
| Automatic text wrapping | ✅ |
| Save project | ✅ |
| Load project | ✅ |

---

# 🔮 Future Ideas

SubtitleCanvas is intentionally focused on **subtitle graphics creation** rather than becoming a full video editor.

Possible future enhancements include:

- 🎨 Subtitle style templates
- 🌟 Text shadow effects
- ✨ Text glow effects
- 🟦 Rounded subtitle backgrounds
- 🎭 Gradient text
- 🔤 Advanced typography controls
- 📋 Subtitle timing editor
- 🕒 Visual subtitle timeline
- 📦 Export presets
- 🖼️ JPG and WebP export
- 📺 Video background preview
- 🎬 Optional video subtitle rendering
- 🔧 FFmpeg integration

---

# 🎯 Project Philosophy

SubtitleCanvas is designed around a simple idea:

> **Load subtitles. Design them visually. Export high-quality subtitle graphics.**

The goal is to provide a lightweight, focused, offline-friendly desktop tool for creating subtitle graphics without the complexity of a full video editing application.

---

# 🛡️ Offline-Friendly

SubtitleCanvas is designed to work locally on your computer.

It does not require:

- A cloud account
- An online service
- An AI subscription
- A remote server

Your subtitle files and generated images remain under your control.

---

# 🧰 Built With

- **Python**
- **PySide6** — Desktop user interface
- **Pillow** — High-quality image rendering

---

# 🤝 Contributions

Ideas, improvements, bug reports, and feature suggestions are welcome.

Potential areas for contribution include:

- Subtitle templates
- UI improvements
- Additional export formats
- Font handling
- Rendering improvements
- Platform testing
- Documentation

---

# ⭐ SubtitleCanvas

**Turn subtitles into beautiful visual graphics.**

    SRT
     ↓
    Edit
     ↓
    Style
     ↓
    Preview
     ↓
    PNG Images
