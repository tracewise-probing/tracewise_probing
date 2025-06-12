#!/usr/bin/env bash
set -euo pipefail
export OPENAI_API_KEY="sk-XXXXXX_XXXXX"

MAX_JOBS=4

trace_names=(
  ""
)

difficulties=(easy medium hard)
ns=(1 2 4 8 16 32 64 128)

# 1) Build array of commands
cmds=()
for trace_name in "${trace_names[@]}"; do
  for difficulty in "${difficulties[@]}"; do
    for n in "${ns[@]}"; do
      if [ -n "$trace_name" ]; then
        prefix="export trace_name='${trace_name}';"
      else
        prefix="unset trace_name;"
      fi
      cmds+=("${prefix} python evaluate_multiprocess.py \
        --difficulty='${difficulty}' \
        --temperature=0.7 \
        --num_threads=32 \
        --n='${n}' \
        --selection=oracle \
        --lcb_version=release_v4 \
        --start_date=2024-08-01 \
        --end_date=2024-12-01 \
        --no_refine \
        --num_round=1 \
        --api_name=openai/Qwen/Qwen2.5-Coder-7B-Instruct \
        --api_base=http://127.0.0.1:8001/8001/v1 \
        --result_json_path='results_sky_v2/sec4_parallel_sample_vanilla_${trace_name}_qwen_7b_${difficulty}_n_${n}.json'")
    done
  done
done

# 2) Shuffle commands
mapfile -t shuffled_cmds < <(printf '%s\n' "${cmds[@]}" | shuf)

# 3) Batch-run shuffled commands in groups of $MAX_JOBS
total=${#shuffled_cmds[@]}
for (( i=0; i<total; i+=MAX_JOBS )); do
  for (( j=i; j<i+MAX_JOBS && j<total; j++ )); do
    eval "${shuffled_cmds[j]}" &
  done
  wait
done

echo "✅ All jobs completed."
