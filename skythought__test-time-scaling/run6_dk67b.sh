#!/usr/bin/env bash
set -euo pipefail

# optional filter string (first positional argument)
filter="${1:-}"

# full list of model identifiers
all_models=(
  "deepseek-ai/deepseek-coder-6.7b-instruct"
  "meta-llama/Llama-3.1-8B-Instruct"
  "microsoft/phi-4"
  "Qwen/Qwen2.5-1.5B-Instruct"
  "AIDC-AI/Marco-o1"
)

# build models array: if filter is set, only include matching models
if [[ -n "$filter" ]]; then
  models=()
  for m in "${all_models[@]}"; do
    if [[ "$m" == *"$filter"* ]]; then
      models+=("$m")
    fi
  done
else
  models=("${all_models[@]}")
fi

# list of trace names
trace_names=(
  "bug_trace_TPL_NEXT"
  "bug_trace_TPL_OUR01"
  "bug_trace_TPL_CONCISETRACE"
  "bug_trace_TPL_CODEEXECUTOR"
)

# list of methods
methods=(
  "naive"
)

# list of selection strategies
selections=(
  "first"
  "fast"
  "oracle"
  "oracle_all_rounds"
  "random"
  "generated_tests"
  "generated_tests_majority"
  "generated_tests_aware_llm_judge"
  "generated_tests_majority_llm"
  "generated_tests_tool_assisted"
  "generated_tests_majority_no_public_tests"
)

# mapping from model → port
declare -A ports=(
  ["deepseek-ai/deepseek-coder-6.7b-instruct"]=8003
  ["meta-llama/Llama-3.1-8B-Instruct"]=8004
  ["microsoft/phi-4"]=8001
  ["Qwen/Qwen2.5-1.5B-Instruct"]=8000
  ["AIDC-AI/Marco-o1"]=8002
)

for trace_name in "${trace_names[@]}"; do
  for model in "${models[@]}"; do
    for method in "${methods[@]}"; do
      for selection in "${selections[@]}"; do

        api="hosted_vllm/${model}"
        port=${ports[$model]}
        api_base="http://10.96.183.224:63019/${port}/v1"
        # sanitize model name for filenames (slashes → underscores)
        model_safe="${model//\//_}"

		export trace_name=$trace_name
        trace_name=$trace_name python evaluate_multiprocess.py \
          --difficulty=easy \
          --temperature=0.7 \
          --num_threads=8 \
          --n=16 \
          --lcb_version release_v2 \
          --num_round 3 \
          --method "$method" \
          --api_base "$api_base" \
          --api_name "$api" \
          --judge "$api" \
          --test_generator "$api" \
          --selection "$selection" \
          --result_json_path="results/${model_safe}_n_16_${trace_name}_${method}_public3_select_${selection}_easy.json"

      done
    done
  done
done
