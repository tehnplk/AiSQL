import sys
from dotenv import load_dotenv
import os

def load_env_for_pyinstaller():
    """โหลด .env file สำหรับ PyInstaller"""
    if getattr(sys, "frozen", False):
        # PyInstaller executable
        try:
            env_path = os.path.join(sys._MEIPASS, ".env")
        except:
            env_path = os.path.join(os.path.dirname(sys.executable), ".env")
    else:
        # Python script
        env_path = ".env"

    if os.path.exists(env_path):
        load_dotenv(env_path)
        return True
    return False
