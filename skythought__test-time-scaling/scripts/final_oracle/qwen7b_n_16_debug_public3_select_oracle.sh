#!/usr/bin/env bash
set -euo pipefail
export OPENAI_API_KEY="sk-XXXXXX_XXXXX"

MAX_ROUND=3
MAX_JOBS=4

trace_names=(
  "bug_trace_TPL_NEXT"
  "bug_trace_TPL_OUR01"
  "bug_trace_TPL_CONCISETRACE"
  "bug_trace_TPL_CODEEXECUTOR"
  ""
)

difficulties=(easy medium hard)

# 1) Build an array of all commands
cmds=()
for trace_name in "${trace_names[@]}"; do
  for difficulty in "${difficulties[@]}"; do
    if [ -n "$trace_name" ]; then
      cmd="export trace_name='${trace_name}'; python evaluate_multiprocess.py \
        --difficulty=${difficulty} \
        --temperature=0.7 \
        --num_threads=32 \
        --n=16 \
        --api_name=\"openai/Qwen/Qwen2.5-Coder-7B-Instruct\" \
        --api_base=\"http://127.0.0.1:8001/8001/v1\" \
        --selection=\"oracle_all_rounds\" \
        --lcb_version=\"release_v4\" \
        --start_date=\"2024-08-01\" \
        --end_date=\"2024-12-01\" \
        --num_round=${MAX_ROUND} \
        --result_json_path=\"results_sky_v2/final_${trace_name}qwen7b_n_16_debug_public3_select_oracle_${difficulty}.json\""
    else
      cmd="unset trace_name; python evaluate_multiprocess.py \
        --difficulty=${difficulty} \
        --temperature=0.7 \
        --num_threads=32 \
        --n=16 \
        --api_name=\"openai/Qwen/Qwen2.5-Coder-7B-Instruct\" \
        --api_base=\"http://127.0.0.1:8001/8001/v1\" \
        --selection=\"oracle_all_rounds\" \
        --lcb_version=\"release_v4\" \
        --start_date=\"2024-08-01\" \
        --end_date=\"2024-12-01\" \
        --num_round=${MAX_ROUND} \
        --result_json_path=\"results_sky_v2/final_qwen7b_n_16_debug_public3_select_oracle_${difficulty}.json\""
    fi
    cmds+=("$cmd")
  done
done

# 2) Shuffle the array
mapfile -t shuffled_cmds < <(printf '%s\n' "${cmds[@]}" | shuf)

# 3) Batch-run 4 at a time
total=${#shuffled_cmds[@]}
for ((i=0; i<total; i+=MAX_JOBS)); do
  for ((j=i; j<i+MAX_JOBS && j<total; j++)); do
    eval "${shuffled_cmds[j]}" &
  done
  wait
done

echo "✅ All jobs completed."
