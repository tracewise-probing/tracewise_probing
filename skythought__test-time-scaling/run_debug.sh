#!/usr/bin/env bash
set -euo pipefail

# optional filter string (first positional argument)
filter="${1:-}"

# full list of model identifiers
all_models=(
  "openai/gpt-4o-mini"
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
  "oracle"
  "oracle_all_rounds"
  "random"
  "generated_tests"
  "generated_tests_majority"
)

# mapping from model → port
declare -A ports=(
  ["openai/gpt-4o-mini"]=-1
  ["deepseek-ai/deepseek-coder-6.7b-instruct"]=8003
  ["meta-llama/Llama-3.1-8B-Instruct"]=8004
  ["microsoft/phi-4"]=8001
  ["Qwen/Qwen2.5-1.5B-Instruct"]=8000
  ["AIDC-AI/Marco-o1"]=8002
)

# maximum concurrent jobs
max_jobs=4

# throttle: wait for at least one background job to finish before returning
throttle() {
  while (( $(jobs -p | wc -l) >= max_jobs )); do
    wait -n
  done
}

# run a single evaluation in the background
run_task() {
  local trace_name=$1
  local model=$2
  local method=$3
  local selection=$4

  # look up port for this model
  local port=${ports[$model]:-}
  if [[ -z "$port" ]]; then
    echo "ERROR: no port mapping for model '$model'" >&2
    exit 1
  fi

  local api="hosted_vllm/${model}"
  local model_safe="${model//\//_}"
  local api_base="http://127.0.0.1:${port}/v1"

  export trace_name

  echo  evaluate_multiprocess.py \
    --difficulty=easy \
    --temperature=0.7 \
    --num_threads=8 \
    --n=16 \
    --lcb_version release_v2 \
    --num_round 3 \
    --method "$method" \
    --api_name "$api" \
    --api_base "$api_base" \
    --judge "$api" \
    --test_generator "$api" \
    --selection "$selection" \
    --result_json_path="results/debug_${model_safe}_n_16_${trace_name}_${method}_public3_select_${selection}_easy.json"
}

# launch all combinations with up to $max_jobs in flight
for trace_name in "${trace_names[@]}"; do
  for model in "${models[@]}"; do
    for method in "${methods[@]}"; do
      for selection in "${selections[@]}"; do
        throttle
        run_task "$trace_name" "$model" "$method" "$selection" &
      done
    done
  done
done

# wait for any remaining jobs
wait
