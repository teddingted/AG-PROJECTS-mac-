# AutoPlotDigitizer V1 - Windows Porting Kit

This folder contains the source code for **V1** (Desktop, with Advanced Pattern Detection).

## How to Build (On Windows)
1.  **Install Python 3.10+**.
2.  **Install Dependencies**:
    ```powershell
    pip install -r requirements.txt
    pip install pyinstaller
    ```
3.  **Build EXE**:
    ```powershell
    pyinstaller AutoPlotDigitizer.spec
    ```
4.  **Run**: Find the exe in `dist/AutoPlotDigitizer.exe`.
