import os, json
from ast_memory import ASTCodebaseGraph
from phase2_fusion import LiveNCMCoprocessor

DATASET_PATH = "/kaggle/working/AI_Cyberdeck/cyberdeck_verified_dataset.jsonl"

def log_verified_build(mission: str, verified_code: str, project_root: str = "/kaggle/working/AI_Cyberdeck/CyberArenaEngine"):
    ast_context = ASTCodebaseGraph(project_root).build_context_map()
    ncm_bp = LiveNCMCoprocessor().generate_arena_blueprint(seed_idx=42)

    record = {
        "messages": [
            {
                "role": "system",
                "content": "You are the Titan Polyglot Engine Core. Use the provided NCM spatial constants and AST symbol map to write zero-error compiling engine code."
            },
            {
                "role": "user",
                "content": f"MISSION: {mission}\n\nNCM ARENA CONSTANTS:\n{ncm_bp['rust_const']}\n{ast_context}"
            },
            {
                "role": "assistant",
                "content": verified_code
            }
        ]
    }
    with open(DATASET_PATH, "a") as f:
        f.write(json.dumps(record) + "\n")
    count = sum(1 for _ in open(DATASET_PATH))
    print(f"Logged verified build to {DATASET_PATH} (Total verified examples: {count})")

def seed_from_current_engine():
    base = "/kaggle/working/AI_Cyberdeck/CyberArenaEngine"
    for rel, mission in [
        ("src/main.rs", "Implement deterministic 60Hz Rust ECS player physics and Steam achievement verification."),
        ("src/arena_map.rs", "Define NCM-verified 3D arena spawn points, objectives, and cover pillar constants."),
        ("shaders/main.wgsl", "Write cross-platform WGSL vertex and fragment shaders for Vulkan/DX12/Metal.")
    ]:
        full = os.path.join(base, rel)
        if os.path.exists(full):
            with open(full, "r") as f:
                log_verified_build(mission, f.read(), base)

if __name__ == "__main__":
    seed_from_current_engine()
