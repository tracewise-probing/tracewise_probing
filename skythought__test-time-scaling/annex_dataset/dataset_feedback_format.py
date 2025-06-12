import json 
import os 
import sys
import traceback 
import copy 
from tqdm import tqdm 
import random 
random.seed(42)

cur_dir = os.path.dirname(__file__)
sys.path.append( os.path.join(cur_dir,"..",))

from collections import defaultdict

from trace_formater.live_code_bench_execute_plus_v2 import run_test_func_snoopy, run_test_std_snoopy
from live_code_bench_execute import run_test_func
from load_mbpp import get_mbpp_dataset_in_lcb_all_buggycode 


import tiktoken
encoding = tiktoken.encoding_for_model("gpt-4o-mini")
def num_tokens_from_string(string: str) -> int:
    """Returns the number of tokens in a text string."""
    num_tokens = len(encoding.encode(string))
    return num_tokens

def truncate_str(
    req_str: str,
    max_token_size: int = 2048,
    # encoding_name: str = "cl100k_base"
) -> str:
    """
    Truncate the input string so that its token count (by tiktoken) 
    does not exceed max_token_size. Uses the given encoding.
    """
    # get the tokenizer for your model (e.g. gpt-4 uses "cl100k_base")
    if req_str is None:
        return ""
    if not isinstance(req_str, str):
        return ""
    if not req_str.strip():
        return ""
        # encode returns a list of token IDs
    tokens = encoding.encode(req_str)
    
    # if we're already within limits, return original
    if len(tokens) <= max_token_size:
        return req_str
    
    # otherwise cut and decode back to text
    truncated_tokens = tokens[:max_token_size]
    return encoding.decode(truncated_tokens)



# def get_mbpp_dataset_in_lcb_all_buggycode():
#     dt = get_mbpp_dataset_in_lcb()
#     with open("./annex_dataset/mbpp_repair_generations.jsonl") as fr :
#         lines= [json.loads(x) for x in fr.readlines() ]
#         mbpp_all_buggycode = {x["task_id"]:x  for x in lines }
#     new_dt = []
#     for item in dt :
#         assert  item["task_id"] in mbpp_all_buggycode 
#         buggy_prompt = mbpp_all_buggycode[ item["task_id"]]["prompt"]
#         buggy_prompt = buggy_prompt.replace("Do not include any explanation.","")
#         assert "explanation" not in buggy_prompt.lower(), buggy_prompt
#         item["question_content"] =buggy_prompt
#
#         new_dt.append( item )
#     return new_dt 

def safe_str(value, max_length=1024 ):
    """Convert a value to a string safely, truncating if too long."""
    try:
        s = str(value)
    except Exception:
        s = f"<unrepresentable object {type(value).__name__}>"

    if len(s) > max_length:
        s = s[:max_length] + f"... [truncated, total length={len(s)}]"
    return s



TRACE_NAME_LIST = [  
    "bug_trace_TPL_NEXT",
  "bug_trace_TPL_OUR01",
  "bug_trace_TPL_CONCISETRACE",
  "bug_trace_TPL_CODEEXECUTOR",
]
def explore_mbpp_with_trace_formating(mbpp_dataset, max_test_c=5, max_token_size=1024 ):

    def extract_buggy_code (xstr):
        # return xstr 
        xstr = xstr .split("```python",1)[-1]
        xstr = xstr .split("```",1)[0]
        if "```" in xstr :
            xstr = xstr .split("**buggy program**",1)[-1]
            xstr = xstr .split("```",1)[0]
            
        return xstr 
    
    def format_feedback(test_input,test_output,output_value,output_trace=None):
        if output_trace is None :
            output_error = (
                f"FAIL: For test input: {safe_str(test_input)}. "
                f"Expected output is: {safe_str(test_output)}, but got: {safe_str(output_value)}."
                f"{safe_str(output_trace)}"
            )
        else:
            output_error = (
                f"FAIL: For  "
                f"{safe_str(output_trace)}"
            )
        tk_size = num_tokens_from_string( output_error )
        if tk_size>max_token_size:
            output_error = truncate_str( output_error , max_token_size)
        return output_error


    trace_name  = TRACE_NAME_LIST [0]
    
    task_list = []
    
    for i in tqdm( range( len(mbpp_dataset)  )):
        item = mbpp_dataset[i]
        task_id = item ["task_id"]
        new_prompt = item["question_content"].replace("\nyour correct program is \n```python\n","")
        completion = extract_buggy_code( item["question_content"] )
        
        assert "your correct" not in new_prompt, item 
        
        is_extracted = False 
        test_cases =  item["public_test_cases"]
        
        random.shuffle( test_cases )

        # print ( completion )
        
        feed_back_list = defaultdict( list )

        
        for i, test_case in enumerate(test_cases):
            test_input = test_case["input"]
            test_output = test_case["output"]
            output_trace = None 
            ## 
            if len( set(  feed_back_list[trace_name] )  )>= max_test_c:
                break 
            
            try :
                passed, output_value = run_test_func(
                    completion, is_extracted,
                    copy.deepcopy(test_input), copy.deepcopy(test_output)
                )
                
                if not passed:
                    ix_syntax = str(output_value).startswith( "Error: "  )
                    
                    # print ("output_value", output_value, "is_syntax:", ix_syntax  )
                    _, _, output_trace = run_test_func_snoopy(
                        completion, is_extracted,
                        copy.deepcopy(test_input), copy.deepcopy(test_output)
                    )
                    
                    for trace_name in TRACE_NAME_LIST:
                        output_trace_named = output_trace[trace_name] if output_trace and type(output_trace)==dict else None
                        output_trace_named = format_feedback(
                            test_input,
                            test_output,
                            output_value,
                            output_trace=output_trace_named)
                        
                        feed_back_list[trace_name].append( output_trace_named )
                        
            except Exception as ex :
                # print ( "---->"*10 )
                # print ( completion , ex )#, item["question_content"] )
                pass
            finally:
                if output_trace is None :
                    output_trace = ""
        
        rolename_list = [("raw",0)]
        for ii in range(max_test_c):
            rolename_list+=[(x,ii+1) for x in TRACE_NAME_LIST]
            
            
        # print ( len(set(  feed_back_list[trace_name] ) ), "feedback.len" )           
        # print ("completion\n\n")
        for trace_name,case_size in rolename_list:
            if trace_name == "raw":
                p_str = new_prompt
                task_list.append({"role":trace_name,"task_id":task_id,"prompt":p_str, "entry_point":item["starter_code"] } )
            else:
                x_feedback  = feed_back_list[trace_name]
                x_feedback  = x_feedback[:case_size]
                x_feedback  = [f"[TEST {idx}] {x} " for  idx,x in  enumerate(x_feedback) ] 
                x_feedback = "\n".join( x_feedback )
                
                p_str = f"{new_prompt} \n, {x_feedback} "
                
                task_list.append({"role":"{}_{}".format(trace_name,case_size),"task_id":task_id,"prompt":p_str , "entry_point":item["starter_code"] } )
        
    return task_list 
        

if __name__ == "__main__":
    
    
    dt = get_mbpp_dataset_in_lcb_all_buggycode()
    
    trace_name = ""
    x_task_list = explore_mbpp_with_trace_formating ( mbpp_dataset=dt , )
    
    role_list = list(set ([x["role"] for x in x_task_list ])) 
    for role in role_list :
        x_task_list_sub = [x  for x in x_task_list if x["role"]==role ]
        json_str = "\n".join([json.dumps(x) for x in x_task_list_sub ])
        with open(f"annex_dataset/{role}__job_list.jsonl","w") as  fw :
            fw.write( json_str )    
        
        