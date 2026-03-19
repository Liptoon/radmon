#!/bin/bash
# Radmon Updater

echo "[*] Pulling latest changes from GitHub..."
git pull origin main

echo "[*] Updating dependencies in venv..."
./venv/bin/pip install --upgrade git+https://github.com/Liptoon/radiacode.git

./venv/bin/pip install -r requirements.txt

chmod +x radmon.py

echo "----------------------------------------------------------"
echo "[OK] System updated to the latest version!"
echo "----------------------------------------------------------"