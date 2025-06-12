#!/usr/bin/env bash
set -euo pipefail

export OPENAI_API_KEY="sk-XXXXXX_XXXXX"
MAX_JOBS=4

trace_names=(
	""
  "bug_trace_TPL_NEXT"
  "bug_trace_TPL_OUR01"
  "bug_trace_TPL_CONCISETRACE"
  "bug_trace_TPL_CODEEXECUTOR"
)
# 1) Build array of commands
difficulties=(easy)
# medium hard)
cmds=()
for trace_name in "${trace_names[@]}"; do
for difficulty in "${difficulties[@]}"; do
    if [ -n "$trace_name" ]; then
      prefix="export trace_name='${trace_name}';"
    else
      prefix="unset trace_name;"
    fi
  cmds+=("${prefix} python evaluate_multiprocess_mbpp_v3.py \
    --difficulty=${difficulty} \
    --temperature=0.7 \
    --num_threads=16 \
    --generator qwen7b \
    --api_name hosted_vllm/Qwen/Qwen2.5-Coder-7B-Instruct \
    --api_base=http://127.0.0.1:8001/8001/v1 \
    --method naive \
    --lcb_version=release_v4 \
    --start_date=2024-08-01 \
    --end_date=2024-12-01 \
    --result_json_path=\"results_sky_v2/initv3_baselines_greedy_${trace_name}_qwen7b_${difficulty}__mbpp.json\"")
done
done

# 2) Shuffle the commands
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
