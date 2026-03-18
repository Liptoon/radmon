#!/bin/bash
# DonnaMamma Radiacode (RADMON) Installer

# Sprawdzenie uprawnień 
if [ "$EUID" -ne 0 ]; then 
  echo "[!] Uruchom ten skrypt przez sudo: sudo ./install.sh"
  exit
fi

echo " Radmon - Instalator (by Publius)"
echo "[*] Tworzenie izolowanego srodowiska venv..."
python3 -m venv venv

echo "[*] Instalacja biblioteki z GitHub (Liptoon/radiacode)..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install git+https://github.com/Liptoon/radiacode.git

echo "[*] Instalacja pozostalych zaleznosci..."
./venv/bin/pip install -r requirements.txt

echo "[*] Ustawianie uprawnien Bluetooth dla uzytkownika $SUDO_USER..."
usermod -aG bluetooth $SUDO_USER

echo "[*] Tworzenie dowiazania symbolicznego w /usr/local/bin/radmon..."
ln -sf $(pwd)/radmon.py /usr/local/bin/radmon
chmod +x radmon.py

echo "----------------------------------------------------------"
echo "[OK] Instalacja zakonczona pomyslnie!"
echo "[!] Możesz teraz uruchomic radmon za pomoca polecenia: radmon"
echo "[!] Pamietaj o restarcie sesji uzytkownika."
echo "----------------------------------------------------------"
