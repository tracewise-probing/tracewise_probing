#!/usr/bin/env bash
set -euo pipefail

# your OpenAI key
export OPENAI_API_KEY="sk-XXXXXX_XXXXX"

MAX_JOBS=4

trace_names=(
  ""
)

difficulties=(easy)

# 1) build an array of all commands
cmds=()
for trace_name in "${trace_names[@]}"; do
  for difficulty in "${difficulties[@]}"; do
    if [ -n "$trace_name" ]; then
      prefix="export trace_name='${trace_name}';"
    else
      prefix="unset trace_name;"
    fi

    cmds+=("${prefix} python evaluate_multiprocess_mbpp.py \
      --difficulty='${difficulty}' \
      --temperature=0.7 \
      --num_threads=16 \
      --n=16 \
      --test_generator='gpt-4o-mini' \
      --lcb_version='release_v4' \
      --start_date='2024-08-01' \
      --end_date='2024-12-01' \
      --num_round=1 \
      --no_dspy_gen \
      --api_name='Qwen/Qwen2.5-Coder-7B-Instruct' \
      --api_base='http://127.0.0.1:8001/8001/v1' \
      --selection='generated_tests_majority_no_public_tests' \
      --result_json_path='results_sky_v2/majority${trace_name}_qwen7b_n_16_${difficulty}__mbpp.json'")
  done
done

# 2) shuffle the commands
mapfile -t shuffled_cmds < <(printf '%s\n' "${cmds[@]}" | shuf)

# 3) batch-run them MAX_JOBS at a time
total=${#shuffled_cmds[@]}
for ((i=0; i<total; i+=MAX_JOBS)); do
  for ((j=i; j<i+MAX_JOBS && j<total; j++)); do
    eval "${shuffled_cmds[j]}" &
  done
  wait
done

echo "✅ All jobs completed."
