
export OPENAI_API_KEY="sk-xxx"

root="./save_dir"

dt=$1


if [ -n "$2" ]; then
	fname="llm_gen_long.py"
echo $fname 
	python $fname  --model "gpt-4o" --dataset $dt \
     --root $root --jsonl_fmt \
        --greedy  --resume --backend openai --base_url "https://api.openai.com/v1/"
else
	fname="llm_gen_v2.py"

echo $fname 

for i in {1..100}; do 
	python $fname  --model "gpt-4o" --dataset $dt \
     --root $root --jsonl_fmt \
        --greedy  --resume --backend openai --base_url "https://api.openai.com/v1/"
done 

fi
