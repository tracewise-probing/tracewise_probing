#!/bin/bash

MAX_ROUND=3
for difficulty in easy medium hard
do
    python evaluate_multiprocess.py \
        --difficulty=${difficulty} \
        --temperature=0.7 \
        --num_threads=32 \
        --n=16 \
        --selection oracle_all_rounds \
        --lcb_version release_v4 --start_date 2024-08-01 --end_date 2024-12-01 \
        --num_round ${MAX_ROUND} \
        --result_json_path="results_sky_v2/final_4omini_n_16_debug_public3_select_oracle_${difficulty}.json"
done
