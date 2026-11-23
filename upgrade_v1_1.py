import os

WORK_DIR = "/kaggle/working/AI_Cyberdeck"
os.chdir(WORK_DIR)

# 1. Upgrade cyberdeck_os.py to inject live AST GraphRAG context + use 14B Core on Dual T4s
with open("cyberdeck_os.py", "r") as f:
    src = f.read()

src = src.replace(
    'model_id: str = "Qwen/Qwen2.5-Coder-7B-Instruct"',
    'model_id: str = "Qwen/Qwen2.5-Coder-14B-Instruct"'
)

old_prompt = 'rust_code = self._run_llm("RUST-ENGINE-ARCHITECT", f"Build a complete runnable Rust ECS game loop for: {mission}")'
new_prompt = '''from ast_memory import ASTCodebaseGraph
            ast_ctx = ASTCodebaseGraph(project_dir).build_context_map()
            rust_code = self._run_llm(
                "RUST-ENGINE-ARCHITECT",
                f"Mission: {mission}\\n\\nExisting Project AST Symbols (import via 'mod arena_map; use arena_map::*;', DO NOT redefine them):\\n{ast_ctx}\\n\\nBuild a complete runnable src/main.rs."
            )'''

src = src.replace(old_prompt, new_prompt)
with open("cyberdeck_os.py", "w") as f:
    f.write(src)

# 2. Wire Kaggle Secrets automatic GitHub auth into cyberdeck_ui.py
with open("cyberdeck_ui.py", "r") as f:
    ui = f.read()

auto_auth_snippet = '''    if auto_github:
        try:
            from kaggle_secrets import UserSecretsClient
            tok = UserSecretsClient().get_secret("GITHUB_TOKEN")
            auto_sync.setup_auto_git("nike-eng", "Nemotron-NCM", tok)
        except Exception:
            pass
        try:'''

ui = ui.replace('    if auto_github:\n        try:', auto_auth_snippet)
with open("cyberdeck_ui.py", "w") as f:
    f.write(ui)

print("Upgraded to Cyberdeck OS v1.1 (14B Dual-T4 Core + AST-Linked Synthesis + Kaggle Secrets Git)!")
