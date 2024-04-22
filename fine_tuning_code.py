import os
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    AutoTokenizer,
    TrainingArguments,
    pipeline,
)
from peft import LoraConfig, PeftModel, prepare_model_for_kbit_training
from trl import SFTTrainer
import subprocess

# Define the list of packages to install
packages = [
    "transformers",
    "datasets",
    "accelerate",
    "peft",
    "trl",
    "bitsandbytes",
    "wandb"
]

# Loop through the list of packages and install them one by one
for package in packages:
    subprocess.run(["pip", "install", "-q", "-U", package])

import json

# Load the API token from the secrets file
with open('secrets.json') as f:
    secrets = json.load(f)

# Get the API token
hf_token = secrets["hf_token"]



# Model
base_model = "NousResearch/Meta-Llama-3-8B"
new_model = "llama-3-8b-PhiloSloppy"

# Dataset
dataset = load_dataset("manoj-dhakal/PhiloSloppy_Socrates", split="train")

# Tokenizer
tokenizer = AutoTokenizer.from_pretrained(base_model, use_fast=True)
tokenizer.pad_token = tokenizer.unk_token
tokenizer.padding_side = "right"

"""Learn more about padding [in the following article](https://medium.com/towards-data-science/padding-large-language-models-examples-with-llama-2-199fb10df8ff) written by Benjamin Marie."""

# Quantization configuration
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

# LoRA configuration
peft_config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=['up_proj', 'down_proj', 'gate_proj', 'k_proj', 'q_proj', 'v_proj', 'o_proj']
)

# Load base moodel
model = AutoModelForCausalLM.from_pretrained(
    base_model,
    quantization_config=bnb_config,
    device_map={"": 0}
)

# Cast the layernorm in fp32, make output embedding layer require grads, add the upcasting of the lmhead to fp32
model = prepare_model_for_kbit_training(model)


# Set training arguments
training_arguments = TrainingArguments(
        output_dir="./results",
        num_train_epochs=1,
        per_device_train_batch_size=10,
        gradient_accumulation_steps=1,
        evaluation_strategy="steps",
        eval_steps=1000,
        logging_steps=1,
        optim="paged_adamw_8bit",
        learning_rate=2e-4,
        lr_scheduler_type="linear",
        warmup_steps=10,
        report_to="wandb",
        max_steps=2, # Remove this line for a real fine-tuning
)

# Set supervised fine-tuning parameters
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    eval_dataset=dataset,
    peft_config=peft_config,
    dataset_text_field="Instructions",
    max_seq_length=512,
    tokenizer=tokenizer,
    args=training_arguments,
)

# Train model
trainer.train()

# Save trained model
trainer.model.save_pretrained(new_model)


# Run text generation pipeline with our model
prompt = "What is a large language model?"
instruction = f"### Instruction:\n{prompt}\n\n### Response:\n"
pipe = pipeline(task="text-generation", model=model, tokenizer=tokenizer, max_length=128)
result = pipe(instruction)
print(result[0]['generated_text'][len(instruction):])

# Empty VRAM
del model
del pipe
del trainer
import gc
gc.collect()
gc.collect()

"""Merging the base model with the trained adapter."""

# Reload model in FP16 and merge it with LoRA weights
model = AutoModelForCausalLM.from_pretrained(
    base_model,
    low_cpu_mem_usage=True,
    return_dict=True,
    torch_dtype=torch.float16,
    device_map={"": 0},
)
model = PeftModel.from_pretrained(model, new_model)
model = model.merge_and_unload()

# Reload tokenizer to save it
tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

"""Optional: pushing the model and tokenizer to the Hugging Face Hub."""

model.push_to_hub(new_model, use_temp_dir=False, token=hf_token)
tokenizer.push_to_hub(new_model, use_temp_dir=False, token=hf_token)

