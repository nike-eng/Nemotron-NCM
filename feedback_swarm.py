import os, subprocess
from phase2_fusion import LiveNCMCoprocessor
from ast_memory import ASTCodebaseGraph
from self_trainer import log_verified_build
import auto_sync

class BidirectionalDualHemisphere:
    """
    True Dual-Hemisphere Swarm:
    - Right Hemisphere (NCM): Solves global spatial constraints & arena topology.
    - Left Hemisphere (Autoregressive 14B/7B + LoRA): Writes sequential Rust logic & unit tests.
    - Bidirectional Feedback: Compiler/test failures route spatial bottlenecks back to NCM
      to re-solve new seeds, while syntax/logic errors route to the Autoregressive Coder.
    """
    def __init__(self, deck):
        self.deck = deck
        self.ncm = LiveNCMCoprocessor()

    def execute_with_feedback(self, project_name: str, mission: str, min_spawns: int = 3, max_rounds: int = 4):
        proj_dir = f"/kaggle/working/AI_Cyberdeck/{project_name}"
        os.makedirs(f"{proj_dir}/src", exist_ok=True)

        with open(f"{proj_dir}/Cargo.toml", "w") as f:
            f.write(f'[package]\nname = "{project_name.lower()}"\nversion = "0.1.0"\nedition = "2021"\n\n[dependencies]\n')

        seed_idx = 10
        bp = self.ncm.generate_arena_blueprint(seed_idx=seed_idx)

        for round_num in range(1, max_rounds + 1):
            print(f"\n--- [SWARM ROUND {round_num}/{max_rounds}] NCM Seed #{seed_idx} (Spawns: {len(bp['spawns'])}) ---")

            # 1. Right Hemisphere (NCM) writes spatial constants
            with open(f"{proj_dir}/src/arena_map.rs", "w") as f:
                f.write(f"// NCM Spatial Seed #{seed_idx}\n" + bp["rust_const"])

            # 2. Check if Autoregressive requirements demand more spawns/cover from NCM
            if len(bp["spawns"]) < min_spawns:
                print(f"[FEEDBACK -> NCM] Autoregressive spec requires >= {min_spawns} spawns (got {len(bp['spawns'])}). Re-solving NCM...")
                seed_idx += 17
                bp = self.ncm.generate_arena_blueprint(seed_idx=seed_idx)
                continue

            # 3. Left Hemisphere (Autoregressive Coder) reads AST & writes Rust + #[test]
            ast_ctx = ASTCodebaseGraph(proj_dir).build_context_map()
            prompt = (
                f"Mission: {mission}\n"
                f"Requirement: Must support at least {min_spawns} players using ARENA_SPAWNS.\n"
                f"AST Symbols (import via 'mod arena_map; use arena_map::*;'):\n{ast_ctx}\n"
                "Include a #[cfg(test)] mod tests block verifying ARENA_SPAWNS.len() >= "
                f"{min_spawns} and running 1 physics tick. Return ONLY raw Rust code."
            )
            rust_code = self.deck._run_llm("AUTOREGRESSIVE-SYSTEMS-CODER", prompt, max_tokens=1100)

            with open(f"{proj_dir}/src/main.rs", "w") as f:
                f.write(rust_code)

            # 4. Arbiter runs both compiler AND unit tests
            test_res = subprocess.run(["cargo", "test"], cwd=proj_dir, capture_output=True, text=True)
            if test_res.returncode == 0:
                print(f"[PASS] Both NCM Spatial Constraints & Autoregressive Rust Tests Passed on Round {round_num}!")
                log_verified_build(mission, rust_code, proj_dir)
                return rust_code

            err_log = test_res.stdout + "\n" + test_res.stderr
            if "assertion" in err_log or "index out of bounds" in err_log:
                print("[FEEDBACK -> NCM] Spatial assertion failed! Requesting new NCM topology...")
                seed_idx += 23
                bp = self.ncm.generate_arena_blueprint(seed_idx=seed_idx)
            else:
                print("[FEEDBACK -> AUTOREGRESSIVE] Syntax/type error detected. Healing code...")
                healed = self.deck._run_llm("AUTOREGRESSIVE-HEALER", f"Fix errors:\n{err_log}\n\nCODE:\n{rust_code}", max_tokens=1100)
                with open(f"{proj_dir}/src/main.rs", "w") as f:
                    f.write(healed)
                if subprocess.run(["cargo", "test"], cwd=proj_dir, capture_output=True).returncode == 0:
                    print(f"[PASS] Healed & Passed cargo test on Round {round_num}!")
                    log_verified_build(mission, healed, proj_dir)
                    return healed

        print("[WARN] Reached max feedback rounds.")
