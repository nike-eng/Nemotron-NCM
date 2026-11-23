import os, subprocess
from tiered_brain import TieredCyberdeckBrain
from phase2_fusion import LiveNCMCoprocessor
from ast_memory import ASTCodebaseGraph
from self_trainer import log_verified_build
import auto_sync

RULES = (
    "Write clean, zero-dependency Rust 2021 engine code with fn main() and a #[cfg(test)] mod tests suite. "
    "Import NCM constants via 'mod arena_map; use arena_map::*;'. "
    "Add #![allow(dead_code, unused_variables)] at line 1. Return ONLY raw Rust code."
)

def build_with_32b_brain(project_name: str, mission: str):
    proj_dir = f"/kaggle/working/AI_Cyberdeck/{project_name}"
    os.makedirs(f"{proj_dir}/src", exist_ok=True)
    with open(f"{proj_dir}/Cargo.toml", "w") as f:
        f.write(f'[package]\nname = "{project_name.lower()}"\nversion = "0.1.0"\nedition = "2021"\n\n[dependencies]\n')

    bp = LiveNCMCoprocessor().generate_arena_blueprint(seed_idx=77)
    with open(f"{proj_dir}/src/arena_map.rs", "w") as f:
        f.write("// NCM Seed #77\n" + bp["rust_const"])

    ast_ctx = ASTCodebaseGraph(proj_dir).build_context_map()
    brain = TieredCyberdeckBrain(initial_tier="heavy")

    prompt = (
        f"Mission: {mission}\n\n"
        f"AST Symbols:\n{ast_ctx}\n\n"
        "Include #[cfg(test)] mod tests verifying deterministic physics, collision resolution, and Steam achievement unlock."
    )
    code = brain.generate("32B-CHIEF-ARCHITECT", RULES, prompt, tier="heavy", max_tokens=1300)

    for attempt in range(1, 4):
        with open(f"{proj_dir}/src/main.rs", "w") as f:
            f.write(code)
        res = subprocess.run(["cargo", "test"], cwd=proj_dir, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"[PASS] 32B Heavy Brain + NCM Compiled & Passed cargo test on Attempt {attempt}!")
            log_verified_build(mission, code, proj_dir)
            break
        print(f"[HEALING] Attempt {attempt} compiler feedback -> 32B Brain refining...")
        code = brain.generate("32B-DEBUG-SPECIALIST", RULES, f"Fix errors:\n{res.stderr}\n\nCODE:\n{code}", tier="heavy", max_tokens=1300)

    try:
        from kaggle_secrets import UserSecretsClient
        tok = UserSecretsClient().get_secret("GITHUB_TOKEN")
        auto_sync.setup_auto_git("nike-eng", "Nemotron-NCM", tok)
        auto_sync.sync_now(f"Brain Upgrade: 32B Dual-T4 Build ({project_name})")
    except Exception as e:
        print("Sync note:", e)

if __name__ == "__main__":
    build_with_32b_brain(
        "Titan32BPhysicsCore",
        "Build a deterministic 3D swept-sphere vs pillar collision solver and rollback state hash verifier using ARENA_SPAWNS, ARENA_OBJECTIVES, and COVER_PILLAR_COUNT."
    )
