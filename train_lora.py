import os, json, torch
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, TrainingArguments, Trainer, DataCollatorForLanguageModeling
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

DATASET_PATH = "/kaggle/working/AI_Cyberdeck/cyberdeck_verified_dataset.jsonl"
OUTPUT_LORA = "/kaggle/working/AI_Cyberdeck/titan_engine_lora"
BASE_MODEL = "Qwen/Qwen2.5-Coder-7B-Instruct"

def train_cartridge_lora():
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError("Dataset missing! Run batch_swarm.py first.")

    rows = [json.loads(line) for line in open(DATASET_PATH)]
    print(f"Loaded {len(rows)} compiler-verified training examples.")

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    tokenizer.pad_token = tokenizer.eos_token

    def tokenize_chat(example):
        text = tokenizer.apply_chat_template(example["messages"], tokenize=False)
        enc = tokenizer(text, truncation=True, max_length=768, padding="max_length")
        enc["labels"] = enc["input_ids"].copy()
        return enc

    ds = Dataset.from_list(rows).map(tokenize_chat, remove_columns=["messages"])

    bnb_cfg = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)
    model = AutoModelForCausalLM.from_pretrained(BASE_MODEL, quantization_config=bnb_cfg, device_map={"": 0})
    model = prepare_model_for_kbit_training(model)

    lora_cfg = LoraConfig(
        r=16, lora_alpha=32, target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_dropout=0.05, bias="none", task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, lora_cfg)

    args = TrainingArguments(
        output_dir=OUTPUT_LORA,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=2,
        max_steps=15,
        learning_rate=2e-4,
        fp16=True,
        logging_steps=3,
        save_strategy="no",
        report_to="none"
    )

    trainer = Trainer(
        model=model,
        train_dataset=ds,
        data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False),
        args=args
    )
    trainer.train()
    model.save_pretrained(OUTPUT_LORA)
    tokenizer.save_pretrained(OUTPUT_LORA)
    print(f"Custom LoRA Cartridge saved to {OUTPUT_LORA}!")

if __name__ == "__main__":
    train_cartridge_lora()
