save_dir="./repair_results"
mkdir -p $save_dir 


your_corpsu=$1

if [ ! -f $your_corpsu ]; then 

	echo "not find your input "$your_corpsu
	exit 1 

fi 

export HUMANEVAL_OVERRIDE_PATH=corpus/humaneval_trace.jsonl  
export MBPP_OVERRIDE_PATH=corpus/mbpp_trace.jsonl  




evalplus.codegen \
	--model "phi-4" \
	--greedy \
	--resume \
	--root $save_dir \
	 --dataset humaneval \
	 --base_url "http://127.0.0.1:8004/v1/" \
	  --backend openai
	  
	  
	