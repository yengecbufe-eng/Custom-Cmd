import os
import sys
import random
import re
import subprocess
import winreg
import json

# VS Code veya başka bir yerden çalıştırıldığında harici Windows CMD penceresi açma
if os.name == 'nt' and 'LAUNCHED_IN_CMD' not in os.environ:
    os.environ['LAUNCHED_IN_CMD'] = '1'
    script_path = os.path.abspath(__file__)
    subprocess.Popen(f'start cmd /k ""{sys.executable}" "{script_path}""', shell=True)
    sys.exit(0)

# Windows Konsolunda Virtual Terminal Processing (ANSI TrueColor) açma
if os.name == 'nt':
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

CONFIG_FILE = os.path.join(os.environ.get("TEMP", "."), "lmstudios_cmd_settings.txt")

DEFAULT_CONFIG = {
    "bg_color": "0",
    "fg_color": "A",
    "hex_color": "AAFF00",
    "prompt": "merhaba istanbul negırı>",
    "title": "CUSTOM CMD BY LMSTUDIOS v4",
    "auto_launch": "0",
    "min_delay": "10",
    "max_delay": "60"
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            config = DEFAULT_CONFIG.copy()
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        config[k] = v
            return config
        except Exception:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()

def save_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            for k, v in config.items():
                f.write(f"{k}={v}\n")
    except Exception:
        pass

config = load_config()

def set_cmd_title(title):
    if os.name == 'nt':
        os.system(f'title {title}')

def extract_hex(raw_input):
    matches = re.findall(r'#?([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b', raw_input)
    if matches:
        clean = matches[0].upper()
        if len(clean) == 3:
            return f"{clean[0]*2}{clean[1]*2}{clean[2]*2}"
        return clean
    return None

def hex_to_ansi(hex_code):
    clean_hex = extract_hex(hex_code) or "AAFF00"
    r = int(clean_hex[0:2], 16)
    g = int(clean_hex[2:4], 16)
    b = int(clean_hex[4:6], 16)
    return f"\033[38;2;{r};{g};{b}m"

def apply_color(hex_code):
    print(hex_to_ansi(hex_code), end="")

def apply_to_windows_terminal(hex_color):
    """
    Yeni Windows Terminal'in (görseldeki sekmeli ekran) settings.json dosyasına rengi yazar.
    """
    appdata = os.environ.get("LOCALAPPDATA", "")
    wt_path = os.path.join(appdata, "Packages")
    if not os.path.exists(wt_path):
        return

    for folder in os.listdir(wt_path):
        if "WindowsTerminal" in folder:
            settings_json = os.path.join(wt_path, folder, "LocalState", "settings.json")
            if os.path.exists(settings_json):
                try:
                    with open(settings_json, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    scheme_name = "LMStudios Green"
                    new_scheme = {
                        "name": scheme_name,
                        "background": "#0C0C0C",
                        "foreground": f"#{hex_color}",
                        "black": "#0C0C0C",
                        "blue": "#0037DA",
                        "cyan": "#3A96DD",
                        "green": f"#{hex_color}",
                        "purple": "#881798",
                        "red": "#C50F1F",
                        "white": "#CCCCCC",
                        "yellow": "#C19C00"
                    }

                    if "schemes" not in data:
                        data["schemes"] = []

                    data["schemes"] = [s for s in data["schemes"] if s.get("name") != scheme_name]
                    data["schemes"].append(new_scheme)

                    if "profiles" in data and "defaults" in data["profiles"]:
                        data["profiles"]["defaults"]["colorScheme"] = scheme_name

                    with open(settings_json, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=4)
                except Exception:
                    pass

def apply_colors_to_windows_system(bg_code, fg_code, custom_hex=None):
    """
    Eski klasik CMD ve yeni Windows Terminal için renkleri ve AutoRun başlangıcını aktarır.
    """
    if os.name == 'nt':
        # 1. Klasik CMD Registry ayarları
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Console", 0, winreg.KEY_SET_VALUE)
            bg_int = int(bg_code, 16)
            fg_int = int(fg_code, 16)
            screen_colors = (bg_int << 4) | fg_int
            winreg.SetValueEx(key, "ScreenColors", 0, winreg.REG_DWORD, screen_colors)
            
            if custom_hex:
                r, g, b = int(custom_hex[0:2], 16), int(custom_hex[2:4], 16), int(custom_hex[4:6], 16)
                bgr_val = (b << 16) | (g << 8) | r
                winreg.SetValueEx(key, "ColorTable10", 0, winreg.REG_DWORD, bgr_val)

            winreg.CloseKey(key)
        except Exception:
            pass

        # 2. CMD açıldığında renk basması için AutoRun kaydı
        try:
            key_proc = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Command Processor", 0, winreg.KEY_SET_VALUE)
            if custom_hex:
                r, g, b = int(custom_hex[0:2], 16), int(custom_hex[2:4], 16), int(custom_hex[4:6], 16)
                autorun_cmd = f'echo \x1b[38;2;{r};{g};{b}m'
                winreg.SetValueEx(key_proc, "AutoRun", 0, winreg.REG_SZ, autorun_cmd)
            winreg.CloseKey(key_proc)
        except Exception:
            pass

        # 3. Windows Terminal için JSON güncellemesi
        if custom_hex:
            apply_to_windows_terminal(custom_hex)

def settings_panel():
    global config
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        apply_color(config["hex_color"])
        is_auto = config.get("auto_launch", "0") == "1"
        
        print("==================================================")
        print("          LMSTUDIOS CONTROL PANEL / SETTINGS      ")
        print("==================================================")
        print(f"  1. Change Text HEX Color          [Current: #{config['hex_color']}]")
        print(f"  2. Change Standard Color Code     [Current: BG={config['bg_color']} FG={config['fg_color']}]")
        print(f"  3. Change Prompt Text             [Current: {config['prompt']}]")
        print(f"  4. Change Window Title           [Current: {config['title']}]")
        print(f"  5. Toggle Random Auto-Launch     [Current: {'ENABLED' if is_auto else 'DISABLED'}]")
        print("  6. SAVE & APPLY TO SYSTEM (CMD & TERMINAL)")
        print("==================================================")
        
        choice = input("Select an option (1-6): ").strip()

        if choice == "1":
            raw_hex = input("Enter HEX Color Code (e.g. AAFF00): ")
            parsed_hex = extract_hex(raw_hex)
            if parsed_hex:
                config["hex_color"] = parsed_hex
                save_config(config)
                apply_color(parsed_hex)
                print(f"✅ Custom HEX set to #{parsed_hex}!")
            else:
                print("❌ Invalid HEX code!")
            input("Press Enter to continue...")

        elif choice == "2":
            print("\nColor Codes: 0=Black, 1=Blue, 2=Green, 3=Cyan, 4=Red, 5=Purple, 6=Yellow, 7=White, A=LightGreen")
            bg = input("Enter Background Code (0-F): ").strip().upper()
            fg = input("Enter Foreground Code (0-F): ").strip().upper()
            if len(bg) == 1 and len(fg) == 1 and bg in "0123456789ABCDEF" and fg in "0123456789ABCDEF":
                config["bg_color"] = bg
                config["fg_color"] = fg
                save_config(config)
                os.system(f"color {bg}{fg}")
                print("✅ Standard colors updated!")
            else:
                print("❌ Invalid code!")
            input("Press Enter to continue...")

        elif choice == "3":
            new_prompt = input("Enter new prompt string: ").strip()
            if new_prompt:
                config["prompt"] = new_prompt
                save_config(config)
                print("✅ Prompt updated!")
            input("Press Enter to continue...")

        elif choice == "4":
            new_title = input("Enter new window title: ").strip()
            if new_title:
                config["title"] = new_title
                set_cmd_title(new_title)
                save_config(config)
                print("✅ Title updated!")
            input("Press Enter to continue...")

        elif choice == "5":
            config["auto_launch"] = "0" if is_auto else "1"
            save_config(config)
            print("✅ Auto-Launch toggled!")
            input("Press Enter to continue...")

        elif choice == "6":
            save_config(config)
            apply_colors_to_windows_system(config["bg_color"], config["fg_color"], config["hex_color"])
            apply_color(config["hex_color"])
            print("\n✅ SUCCESS: Colors saved to Windows System, Registry & Windows Terminal!")
            input("Press Enter to return...")
            break

def custom_cmd_app():
    set_cmd_title(config["title"])
    os.system('cls' if os.name == 'nt' else 'clear')
    apply_color(config["hex_color"])

    print("=" * 60)
    print("          CUSTOM CMD BY LMSTUDIOS (v4)          ")
    print("=" * 60)
    print("Type 'panel' to open settings, 'help' for commands, 'exit' to quit.\n")

    while True:
        try:
            apply_color(config["hex_color"])
            command = input(f"{config['prompt']} ").strip()

            if not command:
                continue

            if command.lower() in ["exit", "quit"]:
                break

            elif command.lower() in ["panel", "settings"]:
                settings_panel()
                os.system('cls' if os.name == 'nt' else 'clear')
                apply_color(config["hex_color"])
                print("=" * 60)
                print("          CUSTOM CMD BY LMSTUDIOS (v4)          ")
                print("=" * 60)

            elif command.lower() == "help":
                print("\n[ Custom Commands ]")
                print("  panel     - Open Control Panel & Save Settings to System")
                print("  clear     - Clear screen")
                print("  exit      - Close terminal\n")

            elif command.lower() == "clear":
                os.system('cls' if os.name == 'nt' else 'clear')

            else:
                os.system(command)

        except KeyboardInterrupt:
            print("\nUse 'exit' to quit.")

if __name__ == "__main__":
    custom_cmd_app()
