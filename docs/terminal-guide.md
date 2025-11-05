# Terminal User Guide

This guide helps apply the workspace patch, create a Python virtual environment, install dependencies, and run unit and E2E tests locally (Windows PowerShell instructions).

## 1) Apply the patch (if you still want to try)
If you have a `patch.diff` file (provided earlier), from your repository root run:

```powershell
# from the repo root
git apply C:\workspace\patch.diff || git apply --reject --whitespace=fix C:\workspace\patch.diff
```

If `git apply` fails with "corrupt patch" or similar, use the manual steps below (copy the files from the patch into the repo or re-run the patch generation step on the remote repo).

## 2) Create a venv and activate it

```powershell
# create venv
python -m venv .venv
# activate (PowerShell)
.\.venv\Scripts\Activate.ps1
# upgrade pip
python -m pip install --upgrade pip
```

## 3) Install Python dependencies
If this repository includes `requirements.txt`:

```powershell
pip install -r requirements.txt
```

If no `requirements.txt` is available, install the minimal test deps:

```powershell
pip install pytest playwright
python -m playwright install
```

## 4) Run unit tests (pytest)

```powershell
# run all unit tests (fast)
python -m pytest -q tests/test_inventory.py tests/test_messages.py
```

## 5) Run Playwright E2E tests locally (optional)

1. Start the web app in one terminal (enable FLASK_SECRET env var):

```powershell
$env:FLASK_SECRET = 'please-change-me'
python -m inventory.web
```

2. In another terminal (with venv activated):

```powershell
python -m pytest -q tests/e2e/test_toasts_playwright.py
```

If Playwright tests require browsers:

```powershell
python -m playwright install
```

## 6) Committing the guide
From the repo root (PowerShell):

```powershell
git add docs\terminal-guide.md
git commit -m "docs: add terminal user guide"
git push origin main
```

## Notes on failures
- If `git push` fails due to authentication, follow the normal GitHub auth flow (personal access token or Git credential manager).
- If `git apply` reports corrupt patch, best options are:
  - Re-generate the patch from the source workspace and retry, or
  - Manually copy the missing files into the repository and commit them.

---
Guide created by the automation tool. Update the guide as needed for your repository specifics.
