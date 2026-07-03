# AGENTS.md

Windows-only desktop app. Python 3 + [Flet](https://flet.dev) GUI for mapping SMB network shares via `net use` / `net view`. No macOS/Linux runtime support despite cross-platform toolchain.

## Commands

```bash
# Setup
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt

# Run app (entry point)
python conectar_servidor.py

# Build standalone .exe (windowed, no console) → dist/Conectier.exe
pyinstaller Conectier.spec
```

No tests, no linter, no type checker, no CI configured. Verify changes by running the app on Windows.

## Architecture

Two-file split. Keep it strict: OS operations never in UI file, UI never in core.

- `conectar_servidor.py` — Flet UI entry point. `main(page)` async fn. All `core.*` calls wrapped in `asyncio.to_thread` to keep GUI responsive. Do not call `core` fns directly on the event loop.
- `core.py` — business logic, fully decoupled from GUI. Three public fns:
  - `list_workspaces(ip, login, senha)` → `(success, shares[], error_msg)`
  - `mount_workspaces(ip, login, senha, shares)` → `(success_count, error_str)`
  - `disconnect_all()` → `(success, msg)`
  - All return 3/2-tuples with error strings, never raise on Windows failures.

## Windows Conventions

- **`subprocess.run` always uses list args, never `shell=True`.** This is intentional (security + Windows arg parsing). Keep it.
- Error 1219 (multiple SMB sessions) is auto-recovered by deleting ghost `\\ip\IPC$` sessions before retry — preserve this logic in `list_workspaces`.
- Credentials stored via `cmdkey` in Windows Credential Manager using **bare IP** as target (`/add:{ip}`, not `\\ip` — cmdkey rejects `\\ip` with "parameter is incorrect" on some Windows builds) and user formatted as `ip\login` (when no domain). This is what enables `/persistent:yes` reconnection after reboot. The cmdkey call must check returncode + stderr and surface failures — silent failure leaves no credential and the drive shows a red X after reboot.
- Drive letters come from `win_letter.txt` at the **root of each share** (not local). Single letter (`Z`) or `Z:`. Missing/invalid → that share is skipped with error, others continue. Local-drive letter conflicts abort that share; same-server network conflicts are remapped; other-server conflicts are reported.

## Build Artifacts

- `build/`, `dist/`, `Conectier.spec` are PyInstaller outputs/config. `dist/Conectier.exe` is the shipped binary.
- `icon.png` is bundled into the exe via `Conectier.spec` `datas=`; `icon.ico` is the Windows exe icon. Keep both in sync if branding changes.

## Existing AI Docs

- `GEMINI.md` — prior codebase map. Architectural facts there are accurate but less detailed than this file; defer here on conflicts.
- `README.md` — user-facing, Portuguese. Documents `win_letter.txt` rules and install steps.
