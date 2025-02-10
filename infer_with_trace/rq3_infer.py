import json 
import os 
import sys 

sys.path.append( "../construct_dataset")
import dt_human_label.utils.tpl_trace_formater as tpl_trace 
# from concurrent.futures import ThreadPoolExecutor

# sys.path.append( ".")
# from utils import evalplus_evaluate 
from utils.evalplus_evaluate import partial_evaluate
from utils.utils import read_jsonl, md5func,get_cache_path,write_jsonl,num_tokens_from_string


def build_conversation_prompts( solution, testcase_index, trace_name ):
    
    assert pass_str  == "fail"
    return trace_str 

def verify_correctness(solution, task_id ):
    
    return {"base":"pass or not ", "plus":"pass or not ", "base_err_index":[], "plus_err_index":[], }



def request_from_model( dataset_dict  , model   ):
    
    pass 





def build_prompt( evaluation_list ,  trace_fmt_name, max_tk_size=12000 ):
    mapping = {
       "next": "bug_trace_TPL_NEXT",
       "exe": "bug_trace_TPL_CODEEXECUTOR",
       "our": "bug_trace_TPL_OUR01",
       "concise": "bug_trace_TPL_CONCISETRACE",
       "naive": "bug_notrace",
        }
    def _build_pmpt ( your_trace ):
        prompt_str = """Provide a self-contained, buggy Python function or class that fails specific tests. Correct the provided BUGGY_PROGRAM. Output only the corrected code; do not include explanations, test cases, examples, or execution results."""
        prompt_suffix = "\n\nnow, given the correct program, you can start with\n ```"
        prompt_str = prompt_str + your_trace +prompt_suffix 
        return prompt_str 
    
    trace_name = mapping[trace_fmt_name]
    trace_name_backup = mapping["naive"]
        
    for i in  range(len(evaluation_list)):
        one_item  = evaluation_list[i]
        trace_str = one_item.get("base_trace",None).get(trace_name,None ) or one_item.get("base_trace",None).get(trace_name_backup,None )
        assert trace_str is not None 
        evaluation_list[i] ["prompt"] =  _build_pmpt(  your_trace= trace_str  )
        evaluation_list[i] ["token_size"]  = num_tokens_from_string( evaluation_list[i] ["prompt"]  )
        if evaluation_list[i] ["token_size"]  >max_tk_size:
            evaluation_list[i] ["prompt"] =  _build_pmpt(  your_trace= one_item.get("base_trace",None).get(trace_name_backup,None )  )
            evaluation_list[i] ["token_size"]  = num_tokens_from_string( evaluation_list[i] ["prompt"]  )
            assert evaluation_list[i] ["token_size"]  < max_tk_size, ( evaluation_list[i] , )
            
    return evaluation_list


fmt_name_list = ["next","exe","naive","concise","our","semcoder","only-error"] 
    
    
def main( 
        load_path="corpus/humaneval_repair_generations.jsonl",
        save_dir="./tmp/",
        cache_dir = "./cache/",
        next_round = 1, # "tmp/humaneval_repair_round1_prompt.jsonl",
        fmt_name="next"
        ):
    assert fmt_name in fmt_name_list , (fmt_name, "-->", fmt_name_list )

    
    dataset="humaneval" if "humaneval" in os.path.basename(load_path) else "mbpp" 
    
    assert dataset in ["humaneval","mbpp"]
    
    cache_path = get_cache_path( cache_dir = cache_dir , load_path = load_path )
    
    save_path = os.path.basename( load_path ).replace(".jsonl",f"_round{next_round}_fmt{fmt_name}_prompt.jsonl")
    save_path = os.path.join(save_dir, save_path )
    print ("save_path", save_path)    

    init_solutions = read_jsonl(load_path )# "corpus/humaneval_repair_prompt.jsonl" )
    init_solutions = [{**x, "_identifier":"{}###llm_md5:{}".format(
            x["task_id"],
            md5func( x["solution"] )
            ) } for x in init_solutions ]

    if not  os.path.isfile( cache_path ):
        exec_info_list =  partial_evaluate(dataset=dataset, samples=  init_solutions )
        write_jsonl(json_list=exec_info_list ,  save_path=cache_path )
    else:
        print ("load from cache ", cache_path )
        exec_info_list = read_jsonl(jsonp =cache_path )
        
    exec_info_list = build_prompt( exec_info_list, trace_fmt_name=fmt_name )

    with open(save_path ,"w") as fw :
        fw.write("\n".join( [json.dumps(x) for x in exec_info_list   ] ) )
    

    
if __name__=="__main__":
    import fire 
    fire.Fire( main  )
    #
    # main( )


    
    