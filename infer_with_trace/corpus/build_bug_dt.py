import os 
import json 

import ast
import fire 
from evalplus.data import  get_human_eval_plus, get_mbpp_plus

from tqdm import tqdm 

import jinja2
environment = jinja2.Environment(loader=jinja2.FileSystemLoader("./") )

# template = environment.get_template("default_buggy.tpl.jinja")


def extract_docstring(code):
    try:
        tree = ast.parse(code)
    except :
        return code 
    # Check if the first element in the body of the AST is a module or function and extract the docstring
    if isinstance(tree, ast.Module):
        # Extract the docstring from the module or function definition
        docstring = ast.get_docstring(tree)
        return docstring
    return code

from evalplus.data import  get_human_eval_plus, get_mbpp_plus

buggy_meta=  {
    "humaneval":"./humaneval_repair_prompt.jsonl",
    "mbpp":"./mbpp_repair_prompt.jsonl",
    }

tpl_meta ={
    "bug_msg": "default_buggy.tpl.jinja",
    "bug_testcase_msg_docstring": "default_buggy.tpl.jinja",
    "bug_msg_same_train": "default_buggy.tpl.jinja",
}
# default_meta = "prompt,bug"
# default_meta = "bug"
import subprocess

def check_error_msg():

    if not os.path.isfile("humaneval_repair_prompt.jsonl"):
        cmd1="evalplus.evaluate --dataset humaneval  --samples humaneval_repair_prompt.jsonl "
        result = subprocess.run(cmd1, shell=True )
        #, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if not os.path.isfile("mbpp_repair_prompt.jsonl"):
        cmd2="evalplus.evaluate --dataset mbpp  --samples mbpp_repair_prompt.jsonl "
        result = subprocess.run(cmd2, shell=True )
    

    

def main(save_dir="./trace_dirs"):
    
    check_error_msg()
    
    for dt_name in ["humaneval","mbpp"] :
        
        for tpl_name in  list( tpl_meta ):
            
            if dt_name=="humaneval":
                gt_dt = get_human_eval_plus() 
            else:
                gt_dt = get_mbpp_plus() 
                
            buggy_path = buggy_meta[dt_name]
            
            buggy_lines= [json.loads(x) for x in  open(buggy_path).readlines() ] 
            ## combine 
            print ("load gt ", len(gt_dt) )
        
            tpl_handle =template = environment.get_template( tpl_meta[tpl_name] )
        
            task_list = []
            
            for i in tqdm( range(len(buggy_lines)) ) :
                buggy_line = buggy_lines[i]
                task_id = buggy_line["task_id"]
                assert task_id in gt_dt , ( task_id , list( gt_dt ) )
                gt_line = gt_dt[task_id]
                prompt = gt_line["prompt"]
                if dt_name == "humaneval":
                    doc_string = extract_docstring( prompt )
                else:
                    doc_string = prompt ## mbpp 
                
                error_message= buggy_line.get("error_message",None)
                trace_message= buggy_line.get("trace_message",None)
                
                meta= {
                    "tpl" : tpl_name , 
                    "task_id": task_id, #line["solution"],
                    "buggy_code": buggy_line["solution"],
                    "nl2code_prompt": prompt, 
                    "canonical_solution": gt_line["canonical_solution"], 
                    "entry_point": gt_line["entry_point"],
                    "description":doc_string,
        
                    "failed_testcases":doc_string,
                    "error_message":error_message,
                    "trace_message":trace_message,
                    
                    }
                
                prompt_str = tpl_handle.render(**meta)
                
                task_list.append({
                    **gt_line,
                    "task_id": task_id , 
                    "prompt": prompt_str.strip() , 
                    })
            
            
            with open(save_path, "w") as fw:
                fw.write("\n".join([json.dumps(x) for x in task_list]))
     
        
    
if __name__=="__main__":
    fire.Fire(main)
    pass 