# Building AutoPlotDigitizer V2 for Windows

This guide explains how to package the application into a single, standalone executable (`.exe`) that runs on Windows without requiring Python installation.

## Prerequisites (Windows)
1.  **Install Python 3.10+**: Download from [python.org](https://www.python.org/downloads/windows/). Ensure you check "Add Python to PATH" during installation.
2.  **Verify Installation**: Open PowerShell or Command Prompt and run:
    ```powershell
    python --version
    pip --version
    ```

## Step 1: Install Dependencies
Navigate to the project directory in PowerShell/CMD and run:
```powershell
pip install -r requirements.txt
pip install pyinstaller
```

## Step 2: Build the Executable
Run the following command to create the standalone EXE:
```powershell
pyinstaller AutoPlotDigitizer.spec
```

## Step 3: Locate the Application
*   Once the build completes, go to the `dist` folder.
*   You will find `AutoPlotDigitizer.exe`.
*   **That's it!** You can copy this single file to any Windows PC and run it.

## Troubleshooting
*   **Missing DLLs**: If `cv2` raises errors, install `opencv-python-headless`:
    ```powershell
    pip install opencv-python-headless
    ```
*   **Console Window**: The currently configured spec file hides the console (`console=False`). If the app crashes immediately, edit `AutoPlotDigitizer.spec`, change `console=True`, rebuild, and run from terminal to see error messages.
