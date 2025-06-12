#!/usr/bin/env bash
set -euo pipefail

export OPENAI_API_KEY="sk-XXXXXX_XXXXX"
MAX_JOBS=4

# 1) Build array of commands
difficulties=(easy)
cmds=()
for difficulty in "${difficulties[@]}"; do
  cmds+=("python evaluate_multiprocess.py \
    --difficulty=${difficulty} \
    --temperature=0.7 \
    --num_threads=16 \
    --generator qwen7b \
        --api_name hosted_vllm/AIDC-AI/Marco-o1  \
        --api_base http://127.0.0.1:8003/v1 \
    --method naive \
    --lcb_version=release_v4 \
    --start_date=2024-08-01 \
    --end_date=2024-12-01 \
    --result_json_path=\"results_sky_v2/baselines_greedy_macro1_${difficulty}.json\"")
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
