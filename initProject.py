import os

class Text:
    Runtime = """import sys
import importlib.machinery
import importlib.util
import Frameworks.Logger as Logger
from dataclasses import dataclass

@dataclass
class Configuation:
    IS_DEVMODE   = True             
    APP_PATH     = 'Sources/example.py'    # fallback path

    IS_LOWGPU    = False           # disable animation
    UI_SCALE     = 1.3             # scale of UI
    UI_FPS       = 200             # animation fps
    UI_THEME     = 'dark' 
    UI_LOCALE    = 'zh'    
    UI_ANIMATIME = 500
    UI_FAMILY    = '源流黑体 CJK'
    SET_USER     = 'root'
    SET_UID      = 1000
    SET_MUTE     = False           # disable sound play

class AppRuntime():
    def getApp(self):
        if sys.argv[-1].endswith('.py'):
            spec = importlib.util.spec_from_file_location("loaded_module", self.config.APP_PATH)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        
        elif sys.argv[-1].endswith('.app'):
            loader = importlib.machinery.SourcelessFileLoader("loaded_module", self.config.APP_PATH)
            module = loader.load_module()

        else:
            Logger.output('Unsupported executable format', type=Logger.Type.ERROR)
            exit()

        return module

    def __init__(self):
        self.config = Configuation()

        if self.config.IS_DEVMODE:
            Logger.output(f"Launching app: {self.config.APP_PATH}", type=Logger.Type.INFO)

        if self.config.IS_LOWGPU:
            self.config.UI_ANIMATIME = 0

        self.target = self.getApp()


if __name__ == "__main__":
    runtime = AppRuntime()
    runtime.target.Application(runtime.config)"""
    
    Device = """import platform
import subprocess
import threading
import psutil
import cpuinfo
import socket
import playsound

class SoundSystem:
    def getSpeakerVolume() -> int:
        if platform.system() == 'Windows':
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            from comtypes import CLSCTX_ALL

            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)
            volume_scalar = volume.GetMasterVolumeLevelScalar()

            return round(volume_scalar * 100)

        
        elif platform.system() == 'Linux':
            try:
                output = subprocess.check_output(["amixer", "get", "Master"])
                lines = output.decode().splitlines()

                for line in lines:
                    if "%" in line and "Mono:" in line or "Front Left:" in line or "Right:" in line:
                        parts = line.strip().split()
                        for part in parts:
                            if part.endswith("%") and part.startswith("["):
                                return int(part[1:-2]) if part.endswith("]%") else int(part[1:-1])
            except Exception as e:
                return None
            
    def playSound(path: str):
        threading.Thread(target=playsound.playsound, args=[path], daemon=True).start()
        

class HardwareInfo:
    def getCPU():
        info = cpuinfo.get_cpu_info()
        return {
            'brand': info.get('brand_raw', 'Unknown'),
            'arch': platform.machine(),
            'cores_physical': psutil.cpu_count(logical=False),
            'cores_logical': psutil.cpu_count(logical=True),
            'frequency': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {}
        }
    
    def getMemory():
        mem = psutil.virtual_memory()
        return {
            'total': f'{mem.total / (1024 ** 3):.2f} GB',
            'available': f'{mem.available / (1024 ** 3):.2f} GB',
            'used': f'{mem.used / (1024 ** 3):.2f} GB',
            'percent': f'{mem.percent} %'
        }

    def getDisk():
        disks = []
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                disks.append({
                    'device': part.device,
                    'mountpoint': part.mountpoint,
                    'fstype': part.fstype,
                    'total': f'{usage.total / (1024 ** 3):.2f} GB',
                    'used': f'{usage.used / (1024 ** 3):.2f} GB',
                    'free': f'{usage.free / (1024 ** 3):.2f} GB',
                    'percent': f'{usage.percent} %'
                })
            except:
                pass
        return disks

    def getNetwork():
        interfaces = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        net_info = {}
        for iface_name, addrs in interfaces.items():
            net_info[iface_name] = {
                'is_up': stats[iface_name].isup if iface_name in stats else None,
                'speed': stats[iface_name].speed if iface_name in stats else None,
                'addresses': [addr.address for addr in addrs if addr.family == socket.AF_INET]
            }
        return net_info
    
    def getBattery():
        battery = psutil.sensors_battery()
        if not battery:
            return None
        return {
            'percent': f'{battery.percent} %',
            'plugged_in': battery.power_plugged,
            'time_left': f'{battery.secsleft // 60} min' if battery.secsleft != psutil.POWER_TIME_UNLIMITED else 'Unlimited'
        }"""

    Logger = """import datetime
import inspect
import sys
import re
import os
from colorama import Fore, Style, Back, init

init(autoreset=True)

class Type:
    INFO  = f'{Back.BLUE} INFO {Back.RESET}'
    ERROR = f'{Back.RED}{Style.BRIGHT} FAIL {Back.RESET}{Fore.RED}'
    WARN  = f'{Back.YELLOW} WARN {Back.RESET}{Fore.YELLOW}'
    DEBUG = f'{Back.MAGENTA} DEBG {Back.RESET}'

_log_history = []
_log_file = 'latest.log'

try:
    with open(_log_file, 'w'):
        pass
except Exception as e:
    print(f"Error initializing log file: {e}", file=sys.stderr)

def _get_caller_info():
    frame = inspect.stack()[2]
    filename = os.path.basename(frame.filename)
    module_name = os.path.splitext(filename)[0]
    return module_name

def _strip_ansi(text: str) -> str:
    ansi_escape = re.compile(r'\\x1B(?:[@-Z\\\\-_]|\\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def output(message: str, *, end: str = '\\n', type: str = Type.INFO):
    now = datetime.datetime.now().strftime('%H:%M:%S')
    module_name = _get_caller_info()

    formatted = f"{Back.GREEN} {now} {Back.CYAN} {module_name} {type} {message} {Style.RESET_ALL}"
    print(formatted, end=end)

    plain_level = _strip_ansi(type)
    log_entry = f"{now} {module_name} {plain_level} {message}"
    _log_history.append(log_entry)

    try:
        with open(_log_file, 'a') as f:
            f.write(log_entry + '\\n')
    except Exception as e:
        print(f"Error writing to log: {e}", file=sys.stderr)

"""
    
    Utils = """import datetime
import sys
import threading
from lunardate import LunarDate
import playsound
from PIL import (
    Image, 
    ImageFilter, 
    ImageDraw, 
    ImageOps,
)

class Utils():
    def __init__(self, args):
        self.UI_LOCALE = args.UI_LOCALE
        self.SET_MUTE = args.SET_MUTE        
        self.UI_SCALE = args.UI_SCALE

    def playsound(self, path: str):
        if not self.SET_MUTE:
            threading.Thread(target=playsound.playsound, args=[path], daemon=True).start()

    def getChineseDate(self, date = None) -> dict:
        if date is None:
            date = datetime.now()

        lunar_date = LunarDate.fromSolarDate(date.year, date.month, date.day)

        weekday_list = ["一", "二", "三", "四", "五", "六", "日"]
        weekday = weekday_list[date.weekday()]

        month_list = ["", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二"]
        day_list = [
            "", "初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
            "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
            "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十"
        ]

        heavenly_stems = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        earthly_branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        gz_year = f"{heavenly_stems[(lunar_date.year - 4) % 10]}{earthly_branches[(lunar_date.year - 4) % 12]}"

        lunar_month_text = f"闰{month_list[lunar_date.month]}" if lunar_date.isLeapMonth else f"{month_list[lunar_date.month]}"

        return {
            "solar": {
                "year": date.year,
                "month": date.month,
                "day": date.day,
                "weekday": f"星期{weekday}",
            },
            "lunar": {
                "year": lunar_date.year,
                "month": lunar_date.month,
                "day": lunar_date.day,
                "is_leap_month": lunar_date.isLeapMonth,
                "gz_year": gz_year,
                "month_text": lunar_month_text,
                "day_text": day_list[lunar_date.day]
            }
        }

    def getScaled(self, number: float) -> int:
        return int(number * self.UI_SCALE)

    @staticmethod
    def bindCanvaScroll(cv, root):
        def on_linux(event):
            if event.num == 4:
                cv.yview_scroll(-1, "units")
            elif event.num == 5:
                cv.yview_scroll(1, "units")

        def on_other(event):
            cv.yview_scroll(-1 * (event.delta // 120), "units")  # Windows/macOS

        def on_resize(event):
            if hasattr(cv, 'configure'):
                cv.configure(scrollregion=cv.bbox("all"))

        if sys.platform.startswith('linux'):
            cv.bind_all("<Button-4>", on_linux)
            cv.bind_all("<Button-5>", on_linux)
        else:
            cv.bind_all("<MouseWheel>", on_other)

        root.bind("<Configure>", on_resize)

    @staticmethod
    def makeImageBlur(img: Image.Image, radius: int = 10) -> Image.Image:
        return img.filter(ImageFilter.GaussianBlur(radius=radius))

    
    @staticmethod
    def makeRadiusImage(img: Image.Image, radius: int = 30, alpha: float = 0.5) -> Image.Image:
        img = img.convert("RGBA")

        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)

        draw.rounded_rectangle(
            (0, 0, img.size[0], img.size[1]), radius, fill=int(256 * alpha))

        img.putalpha(mask)

        return img

    
    @staticmethod
    def makeMaskImage(size: tuple, color: tuple) -> Image.Image:
        return Image.new("RGBA", size=size, color=color)

    
    @staticmethod
    def mergeImage(image: Image.Image, alpha: Image.Image) -> Image.Image:
        if image.format != 'RGBA': # ValueError: image has wrong mode 
            image = image.convert('RGBA')

        if alpha.format != 'RGBA':
            alpha = alpha.convert('RGBA')
        return Image.alpha_composite(image, alpha)

    
    @staticmethod
    def getProportionalImage(img: Image.Image, size: tuple) -> Image.Image:
        target_width, target_height = size
        scale_width = target_width / img.width
        scale_height = target_height / img.height
        scale = min(scale_width, scale_height)
        
        new_width = int(img.width * scale)
        new_height = int(img.height * scale)
        
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        resized_img = ImageOps.fit(resized_img, (target_width, target_height), Image.Resampling.LANCZOS, 0, (0.5, 0.5))
        
        return resized_img"""
    
    Example = """import Frameworks.Logger as Logger


class Application:
    def __init__(self, args):
        Logger.output('Hello, World!')"""
    
    Build = """make = {
    'Sources/example.py': 'Releases/example.app',
}

















import os
import sys
import py_compile
import Frameworks.Logger as Logger

def build_project(build_map: dict[str, str]):
    Logger.output('Starting project build...')
    total = len(build_map)

    for idx, (src, dst) in enumerate(build_map.items(), start=1):
        if not os.path.exists(src):
            Logger.output(f"[{idx}/{total}] Source file not found: {src}, skipping...", type=Logger.Type.ERROR)
            sys.exit(1)

        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            py_compile.compile(src, cfile=dst, doraise=True)
            Logger.output(f"[{idx}/{total}] {src} -> {dst}", type=Logger.Type.INFO)
        except py_compile.PyCompileError as e:
            Logger.output(f"[{idx}/{total}] Syntax error in {src}:\\n{e}", type=Logger.Type.ERROR)
            sys.exit(1)

    Logger.output('Project build complete.')

if __name__ == "__main__":
    build_project(make)


"""

    Ignore = """
########################
    


########################

# Project
initProject.py
*.log

# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so
*.pyc

# Virtual environments
env/
venv/
.venv/

# pipenv
Pipfile.lock

# Poetry
poetry.lock

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# Pytest
.pytest_cache/

# Coverage reports
htmlcov/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover

# Jupyter Notebook
.ipynb_checkpoints

# IPython history
.history

# PyInstaller
# Usually these files are written by a python script from a template
*.manifest
*.spec
build

# Build artifacts
build/
dist/
*.egg-info/
.eggs/
*.egg

# Unit test / coverage reports
.tox/
.nox/

# Editor
.vscode/
.idea/

# Darwin
.DS_Store

# Windows
Thumbs.db
ehthumbs.db
Desktop.ini

# Logs
*.log

# dotenv
.env
.env.*

# SQLite
*.sqlite3

# Editor backups
*~
*.swp
*.swo
"""

os.makedirs('Releases', exist_ok=True)
os.makedirs('Frameworks', exist_ok=True)
os.makedirs('Sources', exist_ok=True)

with open('Frameworks/Logger.py', 'w', encoding='utf-8') as f:
    f.write(Text.Logger)

with open('Frameworks/Utils.py', 'w', encoding='utf-8') as f:
    f.write(Text.Utils)

with open('Frameworks/Device.py', 'w', encoding='utf-8') as f:
    f.write(Text.Device)

with open('Sources/example.py', 'w', encoding='utf-8') as f:
    f.write(Text.Example)

with open('.gitignore', 'w', encoding='utf-8') as f:
    f.write(Text.Ignore)

with open('run.py', 'w', encoding='utf-8') as f:
    f.write(Text.Runtime)

with open('omake.py', 'w', encoding='utf-8') as f:
    f.write(Text.Build)