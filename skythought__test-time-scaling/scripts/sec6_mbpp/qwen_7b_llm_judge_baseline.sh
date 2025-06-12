
MAX_ROUND=5


export OPENAI_API_KEY="sk-XXXXXX_XXXXX"

# list of trace names
trace_names=(
  ""
  "bug_trace_TPL_NEXT"
  "bug_trace_TPL_OUR01"
  "bug_trace_TPL_CONCISETRACE"
  "bug_trace_TPL_CODEEXECUTOR"
)

for trace_name in "${trace_names[@]}"; do


for difficulty in easy 
do
      if [ -z "$trace_name" ]; then
        unset trace_name
      else
        export trace_name
      fi
    python evaluate_multiprocess_mbpp.py \
        --difficulty=${difficulty} \
        --temperature=0.7 \
        --num_threads=16 \
        --n=8 \
        --selection=generated_tests_aware_llm_judge\
        --test_generator openai/gpt-4o-mini \
        --lcb_version release_v4 \
        --start_date 2024-08-01 \
        --end_date 2024-12-01 \
        --num_round ${MAX_ROUND} \
        --api_name openai/Qwen/Qwen2.5-Coder-7B-Instruct \
        --api_base http://127.0.0.1:8001/8001/v1 \
        --result_json_path="results_sky_v2/sec6_${trace_name}qwen7b_llm_judge_baseline_${difficulty}_max_round_${MAX_ROUND}__mbpp.json" \
        --load_cached_preds \
        --cached_preds_path="results_sky_v2/sec5_revision_vanilla_qwen_7b_${difficulty}_max_round_${MAX_ROUND}__mbpp.json"
done


done