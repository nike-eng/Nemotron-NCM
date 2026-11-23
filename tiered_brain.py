import os, gc, shutil, torch
os.environ["HF_HOME"] = "/tmp/hf_cache"
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel
from rich.console import Console

console = Console()

class TieredCyberdeckBrain:
    def __init__(self, initial_tier: str = "heavy"):
        self.fast_id = "Qwen/Qwen2.5-Coder-7B-Instruct"
        self.heavy_id = "Qwen/Qwen2.5-Coder-32B-Instruct"
        self.lora_path = "/kaggle/working/AI_Cyberdeck/titan_engine_lora"
        self.active_tier = None
        self.tokenizer = None
        self.model = None
        self.load_tier(initial_tier)

    def _clear_vram_and_disk_cache(self):
        if self.model is not None:
            del self.model
            del self.tokenizer
            self.model = None
            self.tokenizer = None
        gc.collect()
        torch.cuda.empty_cache()
        shutil.rmtree("/tmp/hf_cache/hub", ignore_errors=True)

    def load_tier(self, tier: str):
        if self.active_tier == tier and self.model is not None:
            return
        self._clear_vram_and_disk_cache()

        bnb_cfg = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True
        )

        if tier == "fast":
            console.print("[bold cyan]⚡ Engaging Tier 1 Brain: Qwen-7B + Custom titan_engine_lora[/bold cyan]")
            self.tokenizer = AutoTokenizer.from_pretrained(self.fast_id)
            base = AutoModelForCausalLM.from_pretrained(self.fast_id, quantization_config=bnb_cfg, device_map={"": 0})
            self.model = PeftModel.from_pretrained(base, self.lora_path) if os.path.exists(self.lora_path) else base
        else:
            console.print("[bold magenta]🧠 Engaging Tier 2 Heavy Brain: Qwen2.5-Coder-32B-Instruct (Dual-T4 Split)[/bold magenta]")
            self.tokenizer = AutoTokenizer.from_pretrained(self.heavy_id)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.heavy_id,
                quantization_config=bnb_cfg,
                device_map="auto",
                max_memory={0: "13.5GiB", 1: "13.5GiB"}
            )
        self.active_tier = tier

    def generate(self, role: str, system_rules: str, prompt: str, tier: str = "heavy", max_tokens: int = 1300) -> str:
        self.load_tier(tier)
        msgs = [
            {"role": "system", "content": f"You are {role}. {system_rules}"},
            {"role": "user", "content": prompt}
        ]
        inp = self.tokenizer.apply_chat_template(
            msgs, tokenize=True, add_generation_prompt=True, return_dict=True, return_tensors="pt"
        ).to("cuda:0")
        out = self.model.generate(**inp, max_new_tokens=max_tokens, do_sample=False)
        raw = self.tokenizer.decode(out.squeeze()[inp["input_ids"].shape[-1]:], skip_special_tokens=True)
        for tag in ["```rust", "```gdscript", "```wgsl", "```"]:
            raw = raw.replace(tag, "")
        return raw.strip()
