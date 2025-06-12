#!/usr/bin/env bash
set -euo pipefail

export OPENAI_API_KEY="sk-XXXXXX_XXXXX"
MAX_JOBS=4

difficulty=easy

#python evaluate_multiprocess_dk.py \
#    --difficulty=${difficulty} \
#    --temperature=0.7 \
#    --num_threads=16 \
#    --generator qwen7b \
#    --api_name openai/gpt-4o-mini   \
#        --api_base https://api.openai.com/v1 \
#    --method naive_cot \
#    --lcb_version=release_v4 \
#    --start_date=2024-08-01 \
#    --end_date=2024-12-01 \
#    --result_json_path="results_sky_v2/baselines_cot_4omini_${difficulty}.json"


#python evaluate_multiprocess_dk.py \
#    --difficulty=${difficulty} \
#    --temperature=0.7 \
#    --num_threads=16 \
#    --generator qwen7b \
#    --api_name openai/gpt-4o-mini   \
#        --api_base https://api.openai.com/v1 \
#    --method naive_nodspy \
#    --lcb_version=release_v4 \
#    --start_date=2024-08-01 \
#    --end_date=2024-12-01 \
#    --result_json_path="results_sky_v2/baselines_4omini_${difficulty}.json"

#python evaluate_multiprocess_dk.py \
#    --difficulty=${difficulty} \
#    --temperature=0.7 \
#    --num_threads=16 \
#    --generator qwen7b \
#    --api_name openai/gpt-4o-mini   \
#        --api_base https://api.openai.com/v1 \
#    --method naive \
#    --lcb_version=release_v4 \
#    --start_date=2024-08-01 \
#    --end_date=2024-12-01 \
#    --result_json_path="results_sky_v2/baselines_greedy_4omini_${difficulty}.json"

















export OPENAI_API_KEY="sk-XXXXXX"
MAX_JOBS=4

difficulty=easy

python evaluate_multiprocess_dk.py \
    --difficulty=${difficulty} \
    --temperature=0.7 \
    --num_threads=16 \
    --generator qwen7b \
    --api_name openai/deepseek-chat   \
        --api_base https://api.deepseek.com \
    --method naive_cot \
    --lcb_version=release_v4 \
    --start_date=2024-08-01 \
    --end_date=2024-12-01 \
    --result_json_path="results_sky_v2/baselines_cot_dkv3_${difficulty}.json"


OPENAI_BASE_URL=https://api.deepseek.com python evaluate_multiprocess_dk.py \
    --difficulty=${difficulty} \
    --temperature=0.7 \
    --num_threads=16 \
    --generator qwen7b \
    --api_name deepseek-chat   \
        --api_base https://api.deepseek.com \
    --method naive_nodspy \
    --lcb_version=release_v4 \
    --start_date=2024-08-01 \
    --end_date=2024-12-01 \
    --result_json_path="results_sky_v2/baselines_dkv3_${difficulty}.json"

python evaluate_multiprocess_dk.py \
    --difficulty=${difficulty} \
    --temperature=0.7 \
    --num_threads=16 \
    --generator qwen7b \
    --api_name openai/deepseek-chat  \
        --api_base https://api.deepseek.com \
    --method naive \
    --lcb_version=release_v4 \
    --start_date=2024-08-01 \
    --end_date=2024-12-01 \
    --result_json_path="results_sky_v2/baselines_greedy_dkv3_${difficulty}.json"
