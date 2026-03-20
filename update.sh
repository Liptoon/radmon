#!/bin/bash
# Radmon Updater

echo "[*] Pulling latest changes from GitHub..."
git config core.fileMode false
git pull origin main


echo "[*] Updating dependencies in venv..."
./venv/bin/pip install --upgrade git+https://github.com/Liptoon/radiacode.git

if [ -f "requirements.txt" ]; then
    ./venv/bin/pip install -r requirements.txt
fi

chmod +x radmon.py

echo "----------------------------------------------------------"
echo "[OK] System updated to the latest version!"
echo "----------------------------------------------------------"