import os, shutil, subprocess, torch
os.environ["HF_HOME"] = "/tmp/hf_cache"
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from phase2_fusion import LiveNCMCoprocessor
from ast_memory import ASTCodebaseGraph
from self_trainer import log_verified_build
import auto_sync

MODEL_ID = "Qwen/Qwen2.5-Coder-14B-Instruct"
RULES = (
    "Write clean, zero-dependency Rust 2021 engine code with fn main() and a #[cfg(test)] mod tests suite. "
    "Import NCM constants via 'mod arena_map; use arena_map::*;'. "
    "Add #![allow(dead_code, unused_variables)] at line 1. Return ONLY raw Rust code with zero markdown fences."
)

def run_14b_build(project_name: str, mission: str):
    proj_dir = f"/kaggle/working/AI_Cyberdeck/{project_name}"
    os.makedirs(f"{proj_dir}/src", exist_ok=True)
    with open(f"{proj_dir}/Cargo.toml", "w") as f:
        f.write(f'[package]\nname = "{project_name.lower()}"\nversion = "0.1.0"\nedition = "2021"\n\n[dependencies]\n')

    bp = LiveNCMCoprocessor().generate_arena_blueprint(seed_idx=77)
    with open(f"{proj_dir}/src/arena_map.rs", "w") as f:
        f.write("// NCM Seed #77\n" + bp["rust_const"])

    ast_ctx = ASTCodebaseGraph(proj_dir).build_context_map()

    bnb_cfg = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, quantization_config=bnb_cfg, device_map={"": 0})

    def ask_14b(prompt: str) -> str:
        msgs = [{"role": "system", "content": RULES}, {"role": "user", "content": prompt}]
        inp = tok.apply_chat_template(msgs, tokenize=True, add_generation_prompt=True, return_dict=True, return_tensors="pt").to("cuda:0")
        out = model.generate(**inp, max_new_tokens=900, do_sample=False)
        raw = tok.decode(out.squeeze()[inp["input_ids"].shape[-1]:], skip_special_tokens=True)
        return raw.replace("```rust", "").replace("```", "").strip()

    code = ask_14b(f"Mission: {mission}\n\nAST Symbols:\n{ast_ctx}\n\nInclude #[cfg(test)] mod tests verifying collision resolution and Steam achievement unlock.")

    for attempt in range(1, 4):
        with open(f"{proj_dir}/src/main.rs", "w") as f:
            f.write(code)
        res = subprocess.run(["cargo", "test"], cwd=proj_dir, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"[PASS] 14B Chief Architect + NCM Passed cargo test on Attempt {attempt}!")
            log_verified_build(mission, code, proj_dir)
            break
        print(f"[HEALING] Attempt {attempt} -> 14B fixing compiler feedback...")
        code = ask_14b(f"Fix Rust compiler errors:\n{res.stderr}\n\nCODE:\n{code}")

    from kaggle_secrets import UserSecretsClient
    gh_tok = UserSecretsClient().get_secret("GITHUB_TOKEN")
    auto_sync.setup_auto_git("nike-eng", "Nemotron-NCM", gh_tok)
    auto_sync.sync_now(f"14B Chief Architect + NCM Verified Build ({project_name})")

if __name__ == "__main__":
    run_14b_build(
        "Titan14BPhysicsCore",
        "Build a deterministic 3D swept-sphere vs pillar collision solver and rollback state hash verifier using ARENA_SPAWNS, ARENA_OBJECTIVES, and COVER_PILLAR_COUNT."
    )
