# Code LLM Semantic Enhancement Framework

## Overview

Code Large Language Models (Code LLMs) have revolutionized programming with their advanced capabilities. However, they face critical limitations in reasoning about runtime behavior and understanding program functionality, which hinders their post-training and practical deployment. Specifically, Code LLMs struggle with:
1. **Reasoning about program execution behavior**: They often fail to interpret what programs actually do during runtime.
2. **Inconsistent semantic representation**: Existing methods inconsistently represent semantic information (e.g., execution traces), limiting their ability to generalize and reason effectively.

To address these challenges, we introduce a **generic framework** that integrates semantic information (e.g., execution traces) into code task-relevant prompts. This framework systematically enhances the reasoning capabilities of Code LLMs by leveraging trace-based semantic information during supervised fine-tuning (SFT) and post-phase inference. Our experiments reveal that while semantic information has limited impact on SFT, it significantly improves Code LLM performance by up to **10.85%** when combined with test-time scaling.

---

## Repository Structure

This repository contains the following folders:

1. **`construct_dataset`**:  
   Tools and scripts for curating and preparing datasets, including trace-rich data for training and evaluation.

2. **`finetune_src`**:  
   Source code and configurations for supervised fine-tuning (SFT) of Code LLMs, including integration of semantic information.

3. **`infer_with_trace`**:  
   Code and utilities for inference with trace-based semantic information, enabling enhanced reasoning during post-phase inference.


---

## Getting Started

### 1. Dataset Construction
Navigate to the `construct_dataset` folder to curate and prepare your dataset. Follow the instructions in the folder's README to generate trace-rich data for training and evaluation.

### 2. Fine-Tuning Code LLMs
To fine-tune Code LLMs with semantic information, use the scripts and configurations provided in the `finetune_src` folder. Example command:
```bash
cd  finetune_src

llamafactory-cli train examples/train_ijcai25/rq1_overview_codegemma/rq1_full_rq1_notrace_baseline.yaml
```

### 3. Inference with Trace-Based Semantic Information
For inference with trace-enhanced prompts, refer to the `infer_with_trace` folder. Example command:
```bash
bash _run_dkchat.sh  corpus/mbpp_repair_generations.jsonl 
```

---

## Key Findings

- **Limited Impact on SFT**: Semantic information (e.g., execution traces) has minimal impact on supervised fine-tuning, contrary to previous research findings.
- **Significant Improvement with Test-Time Scaling**: When combined with test-time scaling, semantic information boosts Code LLM performance by up to **10.85%** on various code tasks.

---

## Reproducibility

We provide detailed logs, configurations, and scripts to ensure reproducibility. Refer to the respective folders for instructions on dataset preparation, fine-tuning, and inference.

---

## Contributions

We welcome contributions to improve this framework! will continiously to contribute the repository and submit pull requests for review in recently.

---

## License

This project is licensed under the [MIT License](LICENSE). Feel free to use, modify, and distribute the code for academic and commercial purposes.

---

For questions or feedback, please open an issue or contact us at issue page. 

