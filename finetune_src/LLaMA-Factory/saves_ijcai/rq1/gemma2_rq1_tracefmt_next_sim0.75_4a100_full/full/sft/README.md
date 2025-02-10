---
library_name: transformers
license: other
base_model: google/gemma-2-9b
tags:
- llama-factory
- full
- generated_from_trainer
model-index:
- name: sft
  results: []
---

<!-- This model card has been generated automatically according to the information the Trainer had access to. You
should probably proofread and complete it, then remove this comment. -->

# sft

This model is a fine-tuned version of [google/gemma-2-9b](https://huggingface.co/google/gemma-2-9b) on the semcoder_sharegpt_office_pyx_inxout_monologue_30k, the semcoder_sharegpt_office_pyx_nl2code and the rq1_tracefmt_next_sim0.75 datasets.

## Model description

More information needed

## Intended uses & limitations

More information needed

## Training and evaluation data

More information needed

## Training procedure

### Training hyperparameters

The following hyperparameters were used during training:
- learning_rate: 2e-05
- train_batch_size: 4
- eval_batch_size: 8
- seed: 42
- distributed_type: multi-GPU
- num_devices: 6
- gradient_accumulation_steps: 8
- total_train_batch_size: 192
- total_eval_batch_size: 48
- optimizer: Use OptimizerNames.ADAMW_TORCH with betas=(0.9,0.999) and epsilon=1e-08 and optimizer_args=No additional optimizer arguments
- lr_scheduler_type: cosine
- lr_scheduler_warmup_steps: 5
- num_epochs: 2.0

### Training results



### Framework versions

- Transformers 4.46.1
- Pytorch 2.5.1+cu124
- Datasets 2.21.0
- Tokenizers 0.20.3
