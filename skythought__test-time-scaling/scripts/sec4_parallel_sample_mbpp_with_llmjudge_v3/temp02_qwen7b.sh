#!/usr/bin/env bash
set -euo pipefail
export OPENAI_API_KEY="sk-XXXXXX_XXXXX"

MAX_JOBS=16

trace_names=(
  "bug_trace_TPL_NEXT"
  "bug_trace_TPL_OUR01"
  "bug_trace_TPL_CONCISETRACE"
  "bug_trace_TPL_CODEEXECUTOR"
  ""
)

difficulties=(easy)
ns=(64)

# 1) Build array of all commands
cmds=()
for trace_name in "${trace_names[@]}"; do
  for difficulty in "${difficulties[@]}"; do
    for n in "${ns[@]}"; do
      if [ -n "$trace_name" ]; then
        prefix="export trace_name='${trace_name}';"
      else
        prefix="unset trace_name;"
      fi

      cmds+=("${prefix} python evaluate_multiprocess_mbpp_v2.py \
        --difficulty='${difficulty}' \
        --temperature=0.2 \
        --num_threads=32 \
        --n='${n}' \
        --selection=generated_tests_majority_llm \
        --lcb_version=release_v4 \
        --start_date=2024-08-01 \
        --end_date=2024-12-01 \
        --no_refine \
        --num_round=1 \
        --api_name=openai/Qwen/Qwen2.5-Coder-7B-Instruct \
        --api_base=http://127.0.0.1:8001/8001/v1 \
        --result_json_path='results_sky_v2/sec4_llmscore_parallel_sample_temp02_${trace_name}_qwen_7b_${difficulty}_n_${n}__mbpp.json'")
    done
  done
done

# 2) Shuffle the commands
mapfile -t shuffled_cmds < <(printf '%s\n' "${cmds[@]}" | shuf)

# 3) Batch-run shuffled commands, $MAX_JOBS at a time
total=${#shuffled_cmds[@]}
for ((i=0; i<total; i+=MAX_JOBS)); do
  for ((j=i; j<i+MAX_JOBS && j<total; j++)); do
    eval "${shuffled_cmds[j]}" &
  done
  wait
done

echo "✅ All jobs completed."
