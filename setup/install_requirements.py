# setup/install_requirements.py
import subprocess

def install():
    print("[1/3] Installing Python packages...")
    subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)
    print("[Y] Python packages installed.")

if __name__ == "__main__":
    install()
