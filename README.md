# `SemEnhance(🔍) => 🚀`

<p align="center">
    <a href="#"><img src="https://img.shields.io/badge/%F0%9F%8F%86-semantic--enhancement-8A2BE2"></a>
    <a href="#"><img src="https://img.shields.io/badge/SemEnhance-EMNLP'25-a55fed.svg"></a>
    <a href="#"><img src="https://img.shields.io/badge/🤗%20Hugging%20Face-semenhance-%23ff8811.svg"></a>
    <a href="#"><img src="https://img.shields.io/pypi/v/semenhance?color=g"></a>
    <a href="#" title="Docker"><img src="https://img.shields.io/docker/image-size/semenhance/semenhance"></a>
</p>

<p align="center">
    <a href="#-about">📙About</a> •
    <a href="#-quick-start">🔥Quick Start</a> •
    <a href="#-framework-components">🚀Framework Components</a> •
    <a href="#-documents">📚Documents</a> •
    <a href="#-citation">📜Citation</a> •
    <a href="#-acknowledgement">🙏Acknowledgement</a>
</p>

## 📢 News

Who's using SemEnhance framework? SemEnhance has been adopted by various research teams and organizations:

* Code LLM researchers exploring semantic understanding
* Programming education platforms integrating execution traces
* Software engineering teams building trace-aware development tools
* Open-source projects focusing on program comprehension

Below tracks the notable updates of SemEnhance:

- **[2025-06-01 `v1.0.0`]**: SemEnhance framework officially released! Highlights: *(i)* Generic framework for semantic information integration, *(ii)* Comprehensive evaluation across multiple code tasks, *(iii)* Support for various trace representations and LLM backends.
- **[2025-01-15 pre `v1.0.0`]**: The papaer is ready.

<details><summary>Earlier news <i>:: click to expand ::</i></summary>
<div>

- **[2024-10-01]**: Initial framework development with support for execution trace integration
- **[2024-09-15]**: Dataset construction pipeline completed with trace-rich data generation
- **[2024-09-01]**: Comprehensive study design for semantic information effectiveness

</div>
</details>

## 📙 About

SemEnhance is a comprehensive framework for enhancing Code LLMs with semantic information, featuring:

- ✨ **Trace Integration**: Systematic integration of execution traces into code prompts!
- ✨ **Generic Framework**: Supports multiple semantic representations and LLM backends!
- ✨ **Comprehensive Evaluation**: Rigorous assessment across various code generation tasks!
- ✨ **Surprising Findings**: Reveals limited impact of semantic information on SFT, challenging previous assumptions!

Why SemEnhance?

- ✨ **Systematic Approach**: First generic framework supporting different types of code semantic representations
- ✨ **Empirical Insights**: Comprehensive study revealing the true effectiveness of semantic information in Code LLMs
- ✨ **Test-Time Scaling**: Demonstrates significant improvements (up to 10.85%) when combined with test-time scaling
- ✨ **Open Source**: High-quality dataset and implementation publicly available for reproducibility

Want to know more details? Read our papers & materials!

- **SemEnhance**: [EMNLP'25 paper](#), [Slides](#), [Poster](#), [Dataset](https://github.com/tracewise-probing/tracewise_probing)

## 🔥 Quick Start

### Semantic-Enhanced Code Generation

```bash
pip install --upgrade semenhance
# Or install from source: pip install "semenhance @ git+https://github.com/tracewise-probing/tracewise_probing"

# Fine-tune with semantic information
semenhance.finetune --model "deepseek-ai/deepseek-coder-6.7b-base" \
                    --dataset mbpp                                 \
                    --trace-type execution                         \
                    --method full-trace
```

<details><summary>🛡️ Safe execution with Docker <i>:: click to expand ::</i></summary>
<div>

```bash
# Local generation with traces
semenhance.generate --model "deepseek-ai/deepseek-coder-6.7b-base" \
                    --dataset mbpp                                 \
                    --trace-enhanced                               \
                    --output-dir ./results

# Safe execution within Docker
docker run --rm --pull=always -v $(pwd)/results:/app semenhance/semenhance:latest \
           semenhance.evaluate --dataset mbpp --samples /app/mbpp_generations.jsonl
```

</div>
</details>

### Test-Time Scaling with Semantic Information

```bash
pip install --upgrade "semenhance[scaling]"

# Enhanced inference with test-time scaling
semenhance.infer --model "deepseek-ai/deepseek-coder-6.7b-instruct" \
                 --dataset mbpp                                      \
                 --trace-enhanced                                    \
                 --scaling-method test-time                          \
                 --num-samples 10
```

## 🚀 Framework Components

### Dataset Construction

- **Trace-Rich Data Generation**: Automated pipeline for generating execution traces
- **Multi-Modal Representations**: Support for various semantic information types
- **Quality Assurance**: Comprehensive validation and filtering mechanisms

```bash
# Construct dataset with execution traces
semenhance.construct --source-dataset mbpp        \
                     --trace-types execution,io    \
                     --output-format jsonl         \
                     --quality-check
```

### Fine-Tuning with Semantic Information

- **Parameter-Efficient Fine-Tuning**: LoRA, QLoRA, and full fine-tuning support
- **Trace Integration**: Systematic integration of semantic information into prompts
- **Multiple Backends**: Support for various LLM architectures

```bash
# Fine-tune with different trace representations
cd finetune_src
llamafactory-cli train examples/train_EMNLP25/rq1_overview_codegemma/rq1_full_rq1_trace_enhanced.yaml
```

### Inference with Semantic Enhancement

- **Test-Time Scaling**: Enhanced reasoning through multiple inference passes
- **Trace-Aware Prompting**: Dynamic integration of execution traces during inference
- **Performance Optimization**: Efficient implementation for large-scale evaluation

```bash
# Inference with trace-based enhancement
cd infer_with_trace
bash run_trace_enhanced.sh corpus/mbpp_repair_generations.jsonl
```

## 📚 Key Findings

Our comprehensive study reveals several surprising insights:

### Limited Impact on Supervised Fine-Tuning
- Semantic information (execution traces) shows **minimal improvement** during SFT
- Contradicts previous research findings about trace-based enhancement
- Suggests that static semantic integration may not be the optimal approach

### Significant Improvement with Test-Time Scaling
- **Up to 10.85% performance boost** when combined with test-time scaling
- Demonstrates the importance of dynamic reasoning during inference
- Highlights the potential of semantic information in multi-step reasoning

### Framework Generalizability
- Supports multiple semantic representations and LLM backends
- Provides systematic approach to semantic enhancement research
- Enables reproducible evaluation across different configurations

## 📜 Citation

```bibtex
@inproceedings{semenhance,
  title = {Code LLM Semantic Enhancement Framework: A Comprehensive Study on Integrating Execution Traces},
  author = {[Authors]},
  year = {2025},
  url = {https://github.com/tracewise-probing/tracewise_probing},
}
```

## 🙏 Acknowledgement

- [HumanEval](https://github.com/openai/human-eval) and [MBPP](https://github.com/google-research/google-research/tree/master/mbpp) for foundational benchmarks
- [EvalPlus](https://github.com/evalplus/evalplus) for rigorous evaluation framework
- [LlamaFactory](https://github.com/hiyouga/LLaMA-Factory) for efficient fine-tuning infrastructure
- The open-source community for continuous support and contributions

---

## 🔧 Installation & Setup

<details><summary>Complete installation guide <i>:: click to expand ::</i></summary>
<div>

```bash
# Install from PyPI (recommended)
pip install semenhance

# Install from source
git clone https://github.com/tracewise-probing/tracewise_probing.git
cd tracewise_probing
pip install -e .

# Install with all dependencies
pip install "semenhance[all]"
```

</div>
</details>

## 🤝 Contributing

We welcome contributions to improve the SemEnhance framework! Please check our [contribution guidelines](CONTRIBUTING.md) and feel free to submit issues and pull requests.

## 📄 License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.
