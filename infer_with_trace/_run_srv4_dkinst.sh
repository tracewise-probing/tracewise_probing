
export OPENAI_API_KEY="xxxx"

root="./save_dir"

dt=$1


if [ -n "$2" ]; then
	fname="llm_gen_long.py"
echo $fname 
	python $fname  --model "deepseek-coder-6.7b-instruct" --dataset $dt \
     --root $root --jsonl_fmt \
        --greedy  --resume --backend openai --base_url "http://10.96.182.166:50621/v1/"
else
	fname="llm_gen_v2.py"

echo $fname 

for i in {1..100}; do 
	python $fname  --model "deepseek-coder-6.7b-instruct" --dataset $dt \
     --root $root --jsonl_fmt \
        --greedy  --resume --backend openai --base_url "http://10.96.182.166:50621/v1/"
done 

fi
