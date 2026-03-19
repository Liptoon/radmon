#!/bin/bash
# Radiacode (RADMON) Installer

# Sprawdzenie uprawnień 
if [ "$EUID" -ne 0 ]; then 
  echo "[!] Run this script with sudo: sudo ./install.sh"
  exit
fi

echo " Radmon - Installer (by Publius)"
echo "[*] Creating Python virtual environment..."
python3 -m venv venv

echo "[*] Installing library from GitHub (Liptoon/radiacode)..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install git+https://github.com/Liptoon/radiacode.git

echo "[*] Installing remaining dependencies..."
./venv/bin/pip install -r requirements.txt

echo "[*] Setting Bluetooth permissions for user $SUDO_USER..."
usermod -aG bluetooth $SUDO_USER

echo "[*] Creating symbolic link in /usr/local/bin/radmon..."
ln -sf $(pwd)/radmon.py /usr/local/bin/radmon
chmod +x radmon.py

echo "----------------------------------------------------------"
echo "[OK] Installation completed successfully!"
echo "[!] You can now run radmon using the command: radmon"
echo "[!] Try radmon -h for usage instructions."
echo "[!] Remember to restart your user session."
echo "----------------------------------------------------------"
