#!/usr/bin/env bash
set -euo pipefail
export OPENAI_API_KEY="sk-XXXXXX_XXXXX"

MAX_ROUND=3            # rounds per evaluation
MAX_JOBS=4             # max concurrent jobs

# Trace-name options (empty entry means “no trace”)
trace_names=(
  "bug_trace_TPL_NEXT"
  "bug_trace_TPL_OUR01"
  "bug_trace_TPL_CONCISETRACE"
  "bug_trace_TPL_CODEEXECUTOR"
  ""
)

# Difficulty levels
difficulties=(easy medium hard)

# ----------------------------------------------------------------------
# Build the list of commands
# ----------------------------------------------------------------------
cmds=()

for trace in "${trace_names[@]}"; do
  for diff in "${difficulties[@]}"; do

    # Result-file suffix (use ‘no_trace’ when trace is empty)
    suffix=${trace:-no_trace}

    # Common CLI arguments
    args=(
      python evaluate_multiprocess.py
      --difficulty "${diff}"
      --temperature 0.7
      --num_threads 16
      --n 1
      --selection random
        --api_name hosted_vllm/deepseek-ai/deepseek-coder-6.7b-instruct
        --api_base http://10.96.183.224:63019/8003/v1
      --lcb_version release_v4
      --start_date 2024-08-01
      --end_date 2024-12-01
      --num_round "${MAX_ROUND}"
        --result_json_path="results_sky_v2/final_${suffix}_dk7b_n_1_debug_public3_select_random_${diff}.json"
    )

    if [[ -n "$trace" ]]; then
      cmds+=("trace_name='${trace}' ${args[*]}")
    else
      cmds+=("unset trace_name; ${args[*]}")
    fi
  done
done

# ----------------------------------------------------------------------
# Shuffle commands to balance load
# ----------------------------------------------------------------------
mapfile -t cmds < <(printf '%s\n' "${cmds[@]}" | shuf)

# ----------------------------------------------------------------------
# Execute commands with concurrency control
# ----------------------------------------------------------------------
for cmd in "${cmds[@]}"; do
  # Start job in background
  eval "${cmd}" &

  # Throttle to at most $MAX_JOBS parallel jobs
  while (( $(jobs -rp | wc -l) >= MAX_JOBS )); do
    sleep 1
  done
done

# Wait for all jobs to finish
wait
echo "✅  All jobs completed."


