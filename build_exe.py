import sys
import os
import urllib.request
import zipfile
import subprocess
import shutil

print("1. Baixando ADB (Platform Tools)...")
url = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
urllib.request.urlretrieve(url, "platform-tools.zip")

print("2. Extraindo arquivos...")
with zipfile.ZipFile("platform-tools.zip", 'r') as zip_ref:
    zip_ref.extractall(".")

print("3. Instalando PyInstaller...")
subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

print("4. Compilando o executável único (Isso pode demorar alguns minutos)...")
cmd = [
    sys.executable,
    "-m", "PyInstaller",
    "--noconsole",
    "--onefile",
    "--name", "Copiador da Tammy",
    "--icon", "NONE",
    "--add-data", "platform-tools/adb.exe;.",
    "--add-data", "platform-tools/AdbWinApi.dll;.",
    "--add-data", "platform-tools/AdbWinUsbApi.dll;.",
    "copiador_celular.py"
]
subprocess.run(cmd, check=True)

print("\n\n" + "="*50)
print("COMPILAÇÃO CONCLUÍDA COM SUCESSO!")
print("O arquivo 'Copiador da Tammy.exe' está dentro da pasta 'dist'!")
print("Ele roda em qualquer PC sem precisar de Python ou baixar o ADB!")
print("="*50)
