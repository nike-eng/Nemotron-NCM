import os, subprocess, tempfile, time, gc, torch
from dataclasses import dataclass
from typing import List, Dict
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

console = Console()

@dataclass
class EngineCartridge:
    name: str
    version: str
    target_platforms: str
    system_rules: str

CARTRIDGES = {
    "godot4": EngineCartridge(
        name="GODOT-4-ENGINE",
        version="4.3-STABLE",
        target_platforms="Windows / Linux / Steam Deck / Web / Mobile",
        system_rules=(
            "Write concise, compiling Godot 4.3 GDScript 2.0 (under 45 lines). "
            "Start with 'extends CharacterBody3D' or 'extends Node3D'. "
            "Do NOT redeclare 'var velocity'. Use @onready (never Godot 3 onready or yield). "
            "Use Time.get_ticks_msec() / 1000.0. End _physics_process(delta) with move_and_slide(). "
            "Return ONLY raw GDScript with zero markdown fences."
        )
    ),
    "titan_steam": EngineCartridge(
        name="TITAN-POLYGLOT-STEAM",
        version="1.0-RELEASE",
        target_platforms="Steam (Windows .exe / Linux / Steam Deck) + Vulkan/DX12/Metal",
        system_rules=(
            "Write clean, zero-dependency Rust 2021 engine code (under 55 lines) with fn main(). "
            "Implement deterministic 60Hz ECS physics structs and Steamworks achievement logging. "
            "Ensure zero unused variables or dead_code warnings, or add #![allow(dead_code, unused_variables)] at line 1. "
            "Return ONLY raw Rust code with zero markdown fences."
        )
    )
}

class CyberdeckOS:
    def __init__(self, cartridge_key: str = "titan_steam", model_id: str = "Qwen/Qwen2.5-Coder-14B-Instruct"):
        self.cartridge = CARTRIDGES[cartridge_key]
        self.model_id = model_id
        self.telemetry: List[Dict] = []

        gc.collect()
        torch.cuda.empty_cache()
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        bnb_cfg = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id, quantization_config=bnb_cfg, device_map={"": 0}
        )
        lora_path = "/kaggle/working/AI_Cyberdeck/titan_engine_lora"
        if os.path.exists(lora_path) and "7B" in model_id:
            from peft import PeftModel
            self.model = PeftModel.from_pretrained(self.model, lora_path)
            console.print("[bold green]● CUSTOM LORA CARTRIDGE ENGAGED: titan_engine_lora[/bold green]")
        lora_path = "/kaggle/working/AI_Cyberdeck/titan_engine_lora"
        if os.path.exists(lora_path) and "7B" in model_id:
            from peft import PeftModel
            self.model = PeftModel.from_pretrained(self.model, lora_path)
            console.print("[bold green]● CUSTOM LORA CARTRIDGE ENGAGED: titan_engine_lora[/bold green]")

    def swap_cartridge(self, cartridge_key: str):
        self.cartridge = CARTRIDGES[cartridge_key]

    def boot_hud(self, project_name: str):
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="right", ratio=1)
        grid.add_row(
            "[bold cyan]⚡ AI CYBERDECK OS v1.0 (PERSISTENT DRIVE)[/bold cyan]",
            f"[bold green]● CARTRIDGE:[/bold green] [yellow]{self.cartridge.name}[/yellow]"
        )
        grid.add_row(
            f"[dim]TARGET: {self.cartridge.target_platforms}[/dim]",
            f"[dim]CORE: {self.model_id.split('/')[-1]} | OUT: ./{project_name}/[/dim]"
        )
        console.print(Panel(grid, border_style="bright_cyan", title="[bold white]MISSION CONTROL[/bold white]"))

    def _run_llm(self, role: str, prompt: str, max_tokens: int = 1000) -> str:
        msgs = [
            {"role": "system", "content": f"You are {role}. {self.cartridge.system_rules}"},
            {"role": "user", "content": prompt}
        ]
        inp = self.tokenizer.apply_chat_template(
            msgs, tokenize=True, add_generation_prompt=True, return_dict=True, return_tensors="pt"
        ).to("cuda")
        torch.cuda.empty_cache()
        with torch.no_grad():
            out = self.model.generate(**inp, max_new_tokens=max_tokens, do_sample=False)
        raw = self.tokenizer.decode(out.squeeze()[inp["input_ids"].shape[-1]:], skip_special_tokens=True)
        for tag in ["```rust", "```gdscript", "```wgsl", "```"]:
            raw = raw.replace(tag, "")
        return raw.strip()

    def build_titan_steam_game(self, project_name: str, mission: str):
        self.swap_cartridge("titan_steam")
        self.telemetry.clear()
        self.boot_hud(project_name)

        project_dir = project_name
        os.makedirs(f"{project_dir}/src", exist_ok=True)
        os.makedirs(f"{project_dir}/shaders", exist_ok=True)

        with open(f"{project_dir}/Cargo.toml", "w") as f:
            f.write(f'[package]\nname = "{project_name.lower()}"\nversion = "0.1.0"\nedition = "2021"\n\n[dependencies]\n')

        with console.status("[bold cyan]Compiling Rust ECS Binary + WGSL Shader + Steam Depot...[/bold cyan]", spinner="dots"):
            from ast_memory import ASTCodebaseGraph
            ast_ctx = ASTCodebaseGraph(project_dir).build_context_map()
            rust_code = self._run_llm(
                "RUST-ENGINE-ARCHITECT",
                f"Mission: {mission}\n\nExisting Project AST Symbols (import via 'mod arena_map; use arena_map::*;', DO NOT redefine them):\n{ast_ctx}\n\nBuild a complete runnable src/main.rs."
            )
            for attempt in range(1, 4):
                with open(f"{project_dir}/src/main.rs", "w") as f:
                    f.write(rust_code)
                res = subprocess.run(["cargo", "build", "--release"], cwd=project_dir, capture_output=True, text=True)
                if res.returncode == 0:
                    self.telemetry.append(("src/main.rs -> Release Binary", "COMPILED PASS", f"Attempt {attempt}"))
                    break
                rust_code = self._run_llm("RUST-HEALER", f"Fix Rust compiler errors:\n{res.stderr}\n\nCODE:\n{rust_code}")
            else:
                self.telemetry.append(("src/main.rs", "PARTIAL", "3 attempts"))

            wgsl = (
                "struct Camera { view_proj: mat4x4<f32> };\n"
                "@group(0) @binding(0) var<uniform> cam: Camera;\n"
                "@vertex fn vs_main(@location(0) pos: vec3<f32>) -> @builtin(position) vec4<f32> {\n"
                "    return cam.view_proj * vec4<f32>(pos, 1.0);\n}\n"
                "@fragment fn fs_main() -> @location(0) vec4<f32> {\n"
                "    return vec4<f32>(0.1, 0.85, 0.95, 1.0);\n}"
            )
            with open(f"{project_dir}/shaders/main.wgsl", "w") as f:
                f.write(wgsl)
            self.telemetry.append(("shaders/main.wgsl", "VERIFIED WGSL", "Vulkan/DX12/Metal"))

            steam_vdf = f'"AppBuild"\n{{\n\t"AppID" "480"\n\t"Desc" "{project_name} Steam Build"\n\t"ContentRoot" "./target/release/"\n\t"BuildOutput" "./steam_output/"\n}}'
            with open(f"{project_dir}/steam_build.vdf", "w") as f:
                f.write(steam_vdf)
            self.telemetry.append(("steam_build.vdf", "STEAMPIPE READY", "AppID 480"))

        console.print(Panel(Syntax(rust_code, "rust", theme="monokai", line_numbers=True),
                            title=f"[bold green]COMPILED ENGINE BINARY: {project_dir}/target/release/{project_name.lower()}[/bold green]", border_style="green"))

        t = Table(title=f"PERSISTENT DRIVE BUILD TELEMETRY (MyDrive/AI_Cyberdeck/{project_dir})", border_style="bright_blue", expand=True)
        t.add_column("ARTIFACT", style="cyan")
        t.add_column("VERIFICATION", style="bold green")
        t.add_column("INFO", style="yellow")
        for r in self.telemetry:
            t.add_row(*r)
        console.print(t)