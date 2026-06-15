# Conectier - Codebase Mapping

This `GEMINI.md` file serves as a map of the **Conectier** project for AI assistants or new developers.

## 📌 Project Overview
**Conectier** is a desktop application built with Python and Flet. Its primary purpose is to connect, list, and map network shared folders (workspaces) from servers onto the user's local machine. It focuses on **Windows**, applying native commands while providing a modern, fluid Material Design interface via Flutter/Flet.

## 📂 Directory Structure & Files

- **`conectar_servidor.py`**
  - **Role:** Main Application Entry Point & GUI.
  - **Details:** Contains the Flet frontend code (`main` async function). It creates the window, defines the layout with modern components, and handles user interactions (IP, login, password inputs). It uses `asyncio.to_thread` to execute network operations asynchronously, preventing the UI from freezing.

- **`core.py`**
  - **Role:** Core Business Logic & OS Integration.
  - **Details:** Contains the heavy lifting for network operations. It is fully decoupled from the GUI.
    - `list_workspaces(ip, login, senha)`: Connects to the server and lists available shares. Uses `net view` on Windows.
    - `mount_workspaces(ip, login, senha, shares)`: Mounts the selected network shares. Uses `net use` on Windows. On Windows, it uniquely requires a `win_letter.txt` file at the root of the share to determine the drive letter.
    - `disconnect_all()`: Unmounts all network drives using `net use * /delete` (Windows).

- **`README.md`**
  - **Role:** Project Documentation.
  - **Details:** Contains instructions on how to install dependencies (like `flet`), run the app, and explains the specific rule for `win_letter.txt` on Windows.

- **`icon.png` / `icon.ico` / `icon.icns`**
  - **Role:** Application Assets.
  - **Details:** Icons used for the application executable/shortcuts (PNG for general use, ICO for Windows).

- **`.gitignore` & `.git/`**
  - **Role:** Version Control.
  - **Details:** Standard Git repository files.

## ⚙️ Key Concepts & Mechanics
1. **Asynchronous UI:** All heavy operations in `core.py` are wrapped in `asyncio.to_thread` inside `conectar_servidor.py` to ensure the Flet GUI remains highly responsive.
2. **Windows Drive Mapping (`win_letter.txt`):** Windows requires a drive letter. Conectier reads a `win_letter.txt` file placed inside the root of the network share to determine which letter (e.g., `Z:`) should be assigned. If the letter is taken by a local drive, it aborts mapping to prevent data loss or conflicts.

## 🛠 Tech Stack
- **Language:** Python 3
- **GUI Framework:** Flet (Flutter-based)
- **Theming:** Flet built-in Dark Mode & Material Design
- **OS Native Tools:** `net use`, `net view` (Windows)
