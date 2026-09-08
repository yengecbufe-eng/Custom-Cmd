"""
==============================================================================
# CUSTOM CMD BY LMSTUDIOS (v4) - README
==============================================================================

## 📌 About The Project
This project is an advanced Python CLI tool that customizes the default Windows 
Command Prompt (CMD) and the new Windows Terminal application. It applies custom 
HEX/ANSI TrueColor values (such as `#AAFF00`), window titles, and custom prompt 
strings, making them persistent system-wide.

---

## 🚀 Features
1. **Automatic External Console Launch:** When executed from VS Code or another IDE, 
   it automatically spawns an independent CMD window.
2. **System-Wide Persistent Color Transfer:**
   - **Legacy CMD:** Updates color tables and default screen colors via Registry (`HKCU\Console`).
   - **Windows Terminal:** Auto-locates `settings.json` and injects the custom `LMStudios Green` color scheme into profiles.
   - **AutoRun Integration:** Applies selected ANSI escape codes to every newly opened CMD tab via `Software\Microsoft\Command Processor\AutoRun`.
3. **Advanced Control Panel (`panel`):** Modify HEX colors, title, and prompt strings without leaving the interface, and apply them directly to the system.

---

## 🛠️ Installation & Execution

### Requirements
- Python 3.x
- Windows 10 / 11 Operating System

### Execution
```bash
python custom_cmd.py
