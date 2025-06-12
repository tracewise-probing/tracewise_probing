#!/usr/bin/env bash
#set -euo pipefail

# list of scripts to run
scripts=(
  "scripts/baselines/dk7b.sh"
  "scripts/baselines/llama8b.sh"
  "scripts/baselines/marcon-o1.sh"
  "scripts/baselines/phi4.sh"
  "scripts/baselines_selfdebug/dk7b_n_1_debug_public3_random3.sh"
  "scripts/baselines_selfdebug/llam8b_n_1_debug_public3_random3.sh"
  "scripts/baselines_selfdebug/marcon-o1_n_1_debug_public3_random3.sh"
  "scripts/baselines_selfdebug/phi4_n_1_debug_public2_random3.sh"
  "scripts/final_oracle/4omini_n_16_debug_public3_select_oracle.sh"
  "scripts/majority_baselines/dk7b_n_16_majority2.sh"
  "scripts/majority_baselines/llam8b_n_16_majority2.sh"
  "scripts/majority_baselines/macron-o1_n_16_majority.sh"
  "scripts/majority_baselines/phi4_n_16_majority.sh"
)

max_jobs=5

for script in "${scripts[@]}"; do
  echo "→ Launching: $script"
  # wait until there are fewer than $max_jobs background jobs running
  while [ "$(jobs -rp | wc -l)" -ge "$max_jobs" ]; do
    sleep 1
  done
  bash "$script" &
done

# wait for all to finish
wait
echo "✅ All jobs completed."

