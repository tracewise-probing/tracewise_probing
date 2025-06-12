#!/usr/bin/env bash
set -euo pipefail

export OPENAI_API_KEY="sk-XXXXXX_XXXXX"

# optional filter string (first positional argument)
filter="${1:-}"

# full list of model identifiers
all_models=(
  "deepseek/deepseek-chat"
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
  "selfdebug"
  "naive"
  "naive_cot"
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

# mapping from model → port (if you ever need it)
declare -A ports=(
  ["deepseek/deepseek-chat"]=-1
)

# maximum concurrent jobs
max_jobs=16

# throttle: wait for at least one background job to finish before returning
throttle() {
  while (( $(jobs -p | wc -l) >= max_jobs )); do
    # wait -n waits for the next job to exit (Bash ≥4.3)
    wait -n
  done
}

# run a single evaluation in the background
run_task() {
  local trace_name=$1
  local model=$2
  local method=$3
  local selection=$4

  local api="hosted_vllm/${model}"
  local model_safe="${model//\//_}"

  # propagate trace_name in case evaluate_multiprocess.py reads it from env
  export trace_name

  python evaluate_multiprocess_dk.py \
    --difficulty=easy \
    --temperature=0.7 \
    --num_threads=8 \
    --n=16 \
    --lcb_version release_v2 \
    --num_round 3 \
    --method "$method" \
    --api_name "$api" \
    --judge "$api" \
    --test_generator "$api" \
    --selection "$selection" \
    --result_json_path="results/${model_safe}_n_16_${trace_name}_${method}_public3_select_${selection}_easy.json"
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
