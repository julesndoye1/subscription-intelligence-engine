#!/usr/bin/env python3
"""
Subscription Intelligence Launcher
Version 1.0
"""

import shutil
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

PORT = 8502

PROJECT = Path(__file__).resolve().parent

APP = PROJECT / "app.py"


# --------------------------------------------------
# Error dialog
# --------------------------------------------------

def show_error(message):

    try:

        subprocess.run([
            "osascript",
            "-e",
            f'display dialog "{message}" buttons {{"OK"}} default button "OK"'
        ])

    except Exception:

        print(message)


# --------------------------------------------------
# Check port
# --------------------------------------------------

def port_open(port):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    result = s.connect_ex(("127.0.0.1", port))

    s.close()

    return result == 0


# --------------------------------------------------
# Find Streamlit
# --------------------------------------------------

def find_streamlit():

    candidates = [

        PROJECT / ".venv" / "bin" / "streamlit",

        PROJECT / "venv" / "bin" / "streamlit",

    ]

    for candidate in candidates:

        if candidate.exists():

            return str(candidate)

    system_streamlit = shutil.which("streamlit")

    if system_streamlit:

        return system_streamlit

    return None


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    if not APP.exists():

        show_error("app.py not found.")

        sys.exit(1)

    if port_open(PORT):

        webbrowser.open(f"http://localhost:{PORT}")

        return

    streamlit = find_streamlit()

    if streamlit is None:

        show_error("Streamlit could not be found.")

        sys.exit(1)

    try:

        subprocess.Popen(

            [

                streamlit,

                "run",

                str(APP),

                "--server.port=8502",

                "--server.headless=true",

            ],

            cwd=PROJECT,

        )

    except Exception as exc:

        show_error(str(exc))

        sys.exit(1)

    time.sleep(5)

    webbrowser.open(f"http://localhost:{PORT}")


if __name__ == "__main__":

    main()
    