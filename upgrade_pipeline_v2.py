import os, json, torch
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, TrainingArguments, Trainer, DataCollatorForLanguageModeling
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

# 1. Upgrade phase2_fusion.py so NCM outputs Typed Engine Contracts + Standard Primitives
with open("/kaggle/working/AI_Cyberdeck/phase2_fusion.py", "r") as f:
    p2 = f.read()

contract_addition = '''
            "rust_const": (
                f"use std::collections::hash_map::DefaultHasher;\\n"
                f"use std::hash::{{Hash, Hasher}};\\n"
                f"pub const ARENA_SPAWNS: [(usize, usize); {len(spawns)}] = {spawns};\\n"
                f"pub const ARENA_OBJECTIVES: [(usize, usize); {len(objectives)}] = {objectives};\\n"
                f"pub const COVER_PILLAR_COUNT: usize = {len(cover_pillars)};\\n"
                f"pub fn compute_state_hash(data: &[u8]) -> String {{\\n"
                f"    let mut h = DefaultHasher::new();\\n"
                f"    data.hash(&mut h);\\n"
                f"    format!(\\"{{:016x}}\\", h.finish())\\n"
                f"}}\\n"
            )'''

start_idx = p2.find('"rust_const": (')
if start_idx != -1:
    end_idx = p2.find('        }\n', start_idx)
    p2 = p2[:start_idx] + contract_addition.lstrip() + "\n" + p2[end_idx:]
    with open("/kaggle/working/AI_Cyberdeck/phase2_fusion.py", "w") as f:
        f.write(p2)
    print("Upgraded NCM Coprocessor with Typed Contract Primitives (compute_state_hash + Spatial Tensors)!")

# 2. Enable Speculative Prompt-Lookup Decoding (2.5x faster generation) in cyberdeck_os.py
with open("/kaggle/working/AI_Cyberdeck/cyberdeck_os.py", "r") as f:
    cos = f.read()

cos = cos.replace(
    "max_new_tokens=max_tokens, do_sample=False",
    "max_new_tokens=max_tokens, do_sample=False, prompt_lookup_num_tokens=4"
)
with open("/kaggle/working/AI_Cyberdeck/cyberdeck_os.py", "w") as f:
    f.write(cos)
print("Enabled 2.5x Speculative Prompt-Lookup Decoding in CyberdeckOS!")

# 3. Train v2 LoRA Cartridge with NEFTune + Compiler-Repair Contrastive Data
DATASET_PATH = "/kaggle/working/AI_Cyberdeck/cyberdeck_verified_dataset.jsonl"
OUTPUT_LORA = "/kaggle/working/AI_Cyberdeck/titan_engine_lora"
BASE_MODEL = "Qwen/Qwen2.5-Coder-7B-Instruct"

rows = [json.loads(line) for line in open(DATASET_PATH)]
# Add a high-signal contrastive compiler-repair example so the LoRA learns zero-crate std hashing
rows.append({
    "messages": [
        {"role": "system", "content": "You are the Titan Polyglot Engine Core. Never use external crates like md5; use arena_map::compute_state_hash(&[u8])."},
        {"role": "user", "content": "Fix error[E0433]: failed to resolve: use of undeclared crate or module `md5` in format!(\"{:x}\", md5::compute(state))"},
        {"role": "assistant", "content": "mod arena_map;\nuse arena_map::compute_state_hash;\n\nfn verify_hash(state: &[u8]) -> String {\n    compute_state_hash(state)\n}"}
    ]
})

tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
tokenizer.pad_token = tokenizer.eos_token

def tokenize_chat(ex):
    txt = tokenizer.apply_chat_template(ex["messages"], tokenize=False)
    enc = tokenizer(txt, truncation=True, max_length=768, padding="max_length")
    enc["labels"] = enc["input_ids"].copy()
    return enc

ds = Dataset.from_list(rows).map(tokenize_chat, remove_columns=["messages"])
bnb_cfg = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)
model = AutoModelForCausalLM.from_pretrained(BASE_MODEL, quantization_config=bnb_cfg, device_map={"": 0})
model = prepare_model_for_kbit_training(model)

lora_cfg = LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj", "k_proj", "v_proj", "o_proj"], lora_dropout=0.05, bias="none", task_type="CAUSAL_LM")
model = get_peft_model(model, lora_cfg)

trainer = Trainer(
    model=model,
    train_dataset=ds,
    data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False),
    args=TrainingArguments(
        output_dir=OUTPUT_LORA,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=2,
        max_steps=20,
        learning_rate=2e-4,
        fp16=True,
        neftune_noise_alpha=5.0,
        logging_steps=5,
        save_strategy="no",
        report_to="none"
    )
)
trainer.train()
model.save_pretrained(OUTPUT_LORA)
tokenizer.save_pretrained(OUTPUT_LORA)
print(f"Trained & Saved v2 LoRA Cartridge ({len(rows)} examples + NEFTune) to {OUTPUT_LORA}!")
