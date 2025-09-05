#!/usr/bin/env python3
"""
Script per installare le dipendenze necessarie per WebLib.
"""

import sys
import subprocess

def install_dependency(package_name):
    """Installa una dipendenza."""
    print(f"Installazione di {package_name}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ {package_name} installato con successo.")
    except subprocess.CalledProcessError:
        print(f"❌ Errore durante l'installazione di {package_name}.")

def main():
    """Funzione principale."""
    # Lista delle dipendenze necessarie
    dependencies = [
        "starlette",
        "uvicorn",
        "websockets",
        "python-multipart",
        "sqlalchemy",
        "psycopg2-binary",
        "passlib",
        "python-jose",
        "bcrypt",
        "requests"
    ]
    
    print("Installazione delle dipendenze necessarie per WebLib...")
    
    confirm = input(f"Vuoi installare {len(dependencies)} dipendenze? (s/n): ")
    if confirm.lower() not in ['s', 'si', 'y', 'yes']:
        print("Installazione annullata.")
        return
    
    for dep in dependencies:
        install_dependency(dep)
    
    print("\n✅ Installazione completata.")
    print("Ora puoi eseguire gli script di test.")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
