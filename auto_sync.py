import os, shutil, subprocess, datetime

DRIVE_DIR = "/kaggle/working/AI_Cyberdeck"
STAGE_DIR = "/tmp/cyberdeck_stage"

def _run(cmd, cwd=STAGE_DIR, check=True):
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if check and res.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{res.stderr}")
    return res

def setup_auto_git(github_user: str, repo_name: str, github_token: str, email: str = "cyberdeck@auto.dev"):
    shutil.rmtree(STAGE_DIR, ignore_errors=True)
    os.makedirs(STAGE_DIR, exist_ok=True)

    _run(["git", "init", "-b", "main"])
    _run(["git", "config", "user.name", github_user])
    _run(["git", "config", "user.email", email])

    remote_url = "https:" + chr(47)*2 + github_user + ":" + github_token + chr(64) + "github.com" + chr(47) + github_user + chr(47) + repo_name + ".git"
    _run(["git", "remote", "add", "origin", remote_url])
    print(f"Auto-Git stage ready -> {github_user}/{repo_name}")

def sync_now(commit_msg: str = None):
    if not os.path.exists(os.path.join(STAGE_DIR, ".git")):
        raise RuntimeError("Run setup_auto_git(...) once first!")
import json, os, subprocess
from datetime import datetime, timezone

def write_session_state(
    work_dir="/kaggle/working/AI_Cyberdeck",
    blox_repo="nike-eng/Blox-Studio",
    ncm_repo="nike-eng/Nemotron-NCM",
):
    dataset_path = os.path.join(work_dir, "cyberdeck_verified_dataset.jsonl")
    lora_dir = os.path.join(work_dir, "titan_engine_lora")

    verified_count = 0
    last_task = "none"
    if os.path.exists(dataset_path):
        with open(dataset_path, "r", encoding="utf-8") as f:
            lines = [ln.strip() for ln in f if ln.strip()]
            verified_count = len(lines)
            if lines:
                try:
                    last_task = json.loads(lines[-1]).get("task", "unknown")[:60]
                except Exception:
                    last_task = "parsed_entry"

    lora_ready = os.path.exists(os.path.join(lora_dir, "adapter_model.safetensors")) or os.path.exists(
        os.path.join(lora_dir, "adapter_model.bin")
    )

    # Check disk headroom on /kaggle/working
    st = os.statvfs("/kaggle/working")
    free_gb = round((st.f_bavail * st.f_frsize) / (1024**3), 2)

    state_md = f"""# SESSION_STATE (AUTO-GENERATED)
- **Updated (UTC):** {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")}
- **Active Repo:** `{ncm_repo}` | **Sibling Sync Repo:** `{blox_repo}`
- **Verified Builds (`cyberdeck_verified_dataset.jsonl`):** {verified_count} (Last: `{last_task}`)
- **LoRA Adapter (`titan_engine_lora/`):** {"READY" if lora_ready else "MISSING"}
- **`/kaggle/working` Free Disk:** {free_gb} GB / 19.5 GB
"""
    with open(os.path.join(work_dir, "SESSION_STATE.md"), "w", encoding="utf-8") as f:
        f.write(state_md)

    # Mirror clean files from Google Drive to /tmp staging (skipping heavy target/ build artifacts)
    for item in os.listdir(STAGE_DIR):
        if item != ".git":
            p = os.path.join(STAGE_DIR, item)
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)

    shutil.copytree(
        DRIVE_DIR, STAGE_DIR, dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("target", "__pycache__", "*.pyc", ".git")
    )

    if not commit_msg:
        commit_msg = f"Cyberdeck Auto-Build: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    _run(["git", "add", "-A"])
    res = _run(["git", "commit", "-m", commit_msg], check=False)
    if "nothing to commit" in res.stdout + res.stderr:
        print("Drive & GitHub already 100% synced.")
        return

    _run(["git", "push", "-u", "origin", "main", "--force"])
    print(f"Auto-Committed & Pushed to GitHub: '{commit_msg}'")
