#!/usr/bin/env bash
set -euo pipefail
export OPENAI_API_KEY="sk-XXXXXX_XXXXX"

MAX_ROUND=5
MAX_JOBS=4

trace_names=(
  "bug_trace_TPL_NEXT"
  "bug_trace_TPL_OUR01"
  "bug_trace_TPL_CONCISETRACE"
  "bug_trace_TPL_CODEEXECUTOR"
  ""
)
difficulties=(easy)

# 1) Build an array of all commands
cmds=()
for trace_name in "${trace_names[@]}"; do
  for difficulty in "${difficulties[@]}"; do
    if [ -n "$trace_name" ]; then
      prefix="export trace_name='${trace_name}';"
    else
      prefix="unset trace_name;"
    fi

    cmds+=("${prefix} python evaluate_multiprocess.py \
      --difficulty='${difficulty}' \
      --temperature=0.7 \
      --num_threads=16 \
      --n=8 \
      --selection=oracle \
      --lcb_version=release_v4 \
      --start_date=2024-08-01 \
      --end_date=2024-12-01 \
      --num_round=${MAX_ROUND} \
    --api_name hosted_vllm/microsoft/phi-4     \
        --api_base http://127.0.0.1:8002/v1 \
      --selection=oracle_all_rounds \
      --result_json_path=\"results_sky_v2/sec5_${trace_name}revision_vanilla_phi4_${difficulty}_max_round_${MAX_ROUND}.json\"")
  done
done

# 2) Shuffle the commands
mapfile -t shuffled_cmds < <(printf '%s\n' "${cmds[@]}" | shuf)

# 3) Batch-run shuffled commands, $MAX_JOBS at a time
total=${#shuffled_cmds[@]}
for (( i=0; i<total; i+=MAX_JOBS )); do
  for (( j=i; j<i+MAX_JOBS && j<total; j++ )); do
    eval "${shuffled_cmds[j]}" &
  done
  wait
done

echo "✅ All jobs completed."
