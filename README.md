# Gaming Guide Launcher

Gaming Guide Launcher is a desktop application built with Python and PySide6 that allows you to create a personal collection of websites, guides, wikis, and gaming resources in one modern interface.

The application can cache web pages and images locally for faster viewing and offline access.

---

## Features

- Modern dark UI
- Add and manage website cards
- Custom images for every site
- Local HTML caching
- Automatic image downloading
- Offline viewing support
- Drag-style card ordering
- Fast local loading
- Fullscreen support (F11)

---

## Screenshots

<img width="1365" height="721" alt="image" src="https://github.com/user-attachments/assets/da22310b-0031-4137-ba56-a4142bd318eb" />
<img width="955" height="463" alt="image" src="https://github.com/user-attachments/assets/f5882808-7de9-4a76-bfef-3fab49d3de02" />
<img width="1127" height="720" alt="image" src="https://github.com/user-attachments/assets/5fcf1c58-b87c-4bc1-a211-cf9508c023d3" />
<img width="1362" height="727" alt="image" src="https://github.com/user-attachments/assets/25d79b93-5edf-4f6d-a747-aa4d31c61752" />
<img width="1357" height="710" alt="image" src="https://github.com/user-attachments/assets/04cc6a3b-1bfd-493b-9ae7-596b10bbe859" />

---

## Installation

### 1. Clone repository

```bash
git clone https://github.com/YOUR_USERNAME/GamingGuideLauncher.git
```

### 2. Open project folder

```bash
cd GamingGuideLauncher
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run application

```bash
python main.py
```

---

## Requirements

- Python 3.10+
- Windows recommended

---

## Technologies Used

- Python
- PySide6
- Requests
- BeautifulSoup4

---

## How It Works

The application downloads HTML pages and images from websites, then stores them locally inside the `PhotoG` folder.

Cached pages are automatically reused for faster loading.

---

## Project Status

This project is currently under development.

---

## License

MIT License
