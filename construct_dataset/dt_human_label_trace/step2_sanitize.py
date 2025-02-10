import json 
import hashlib
from glob2 import glob 
import os 
import sys 

from collections import defaultdict 

from concurrent.futures import ThreadPoolExecutor

num_workers = os.cpu_count()-1 
# from evalplus.eval import untrusted_check,is_floats 

md5_func = lambda x: hashlib.md5( x.encode("utf-8") ).hexdigest()  

import random 
# random.seed(10)

import re 
from tqdm import tqdm 
import numpy as np 

sys.path.append( "/home/xxxxxxx/wj_code/dl_execute/self-oss-instruct/selfcodealign/src/")
from star_align.utils import find_code_blocks 


import ast
import astor  # Import the astor module for un-parsing AST


import ast

def extract_function_by_name(source_code, function_name=None):
    # Parse the source code into an AST
    tree = ast.parse(source_code)
    
    # Define containers for the components we want to keep
    selected_nodes = []
    # globals = []
    # functions = []
    # classes = []
    main_block_found = False
    
    # Walk through all nodes in the AST
    for node in tree.body:
        if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
            # Collect import statements
            selected_nodes.append(node)
        elif isinstance(node, ast.Global):
            # Collect global variables
            selected_nodes.append(node)
        elif isinstance(node, ast.FunctionDef):
            # Collect function definitions
            #if node.name == function_name:
            selected_nodes.append(node)
        elif isinstance(node, ast.ClassDef):
            # Collect class definitions
            selected_nodes.append(node)
        elif isinstance(node, ast.If):
            # Check for __name__ == "__main__" block and stop processing if found
            if isinstance(node.test, ast.Compare):
                if isinstance(node.test.left, ast.Name) and node.test.left.id == "__name__":
                    if len(node.test.ops) == 1 and isinstance(node.test.ops[0], ast.Eq) and isinstance(node.test.comparators[0], ast.Str):
                        if node.test.comparators[0].s == "__main__":
                            main_block_found = True
    
    # Remove any content after the __name__ == "__main__" block if it's found
    if main_block_found:
        tree.body = [node for node in tree.body if not isinstance(node, ast.If)]
    
    # Return the desired extracted components in code form
    extracted_code = ""
    
    # Add imports
    for import_node in selected_nodes:
        extracted_code += ast.unparse(import_node) + "\n"
    
    return extracted_code



def extract_content_split_function_testcase_or_jsontest( llm_rsp, only_first_block=False  ):
    
    content_list =  find_code_blocks( llm_rsp )
    
    if not only_first_block :
        if len(content_list)!=2 :
            return None 
        testcase_str = content_list[-1]
        try :
            testcase_str = json.loads( testcase_str )
            testcase_str = json.dumps( testcase_str )
        except  json.JSONDecodeError  as ex :
            try :
                testcase_str = eval( testcase_str )
                testcase_str = json.dumps( testcase_str )
            except Exception  as ex :
                return None 
            
        return {"extracted_code":content_list[0] , "tests":  testcase_str }
    else:
        if len(content_list)<=0 :
            return None 
        extracted_code = content_list[0]
        try :
            extracted_code = extract_function_by_name( extracted_code )
        except :
            pass 
        return {"extracted_code":  extracted_code }


def read_jsonl( jsonp ):
    with open( jsonp ) as fr :
        lines = [json.loads(x) for x in fr.readlines() ]
    return lines 

def extract_content (one_f ):
    
    
    one_pid_list = read_jsonl( one_f )
        
    random.shuffle( one_pid_list )
    ## 
    ## expand the pid's info     
    # one_pid_info = [] 
    # for one_content in one_pid_list :
    
    def process_file( i ) :
        one_content = one_pid_list[i]
        uuid = one_content["uuid"]
        pid = uuid.split("###")[0]
        
        llm_rsp = one_content.pop("solution")
        if "nl2code" in pid :#pid.startswith("nl2code"):
            content_info  = extract_content_split_function_testcase_or_jsontest( llm_rsp  =llm_rsp ,only_first_block=True )
        else:
            content_info  = extract_content_split_function_testcase_or_jsontest( llm_rsp  =llm_rsp  )
        if content_info is None :
            # err_info[ uuid ] = {"status":-1,"msg":"llm_rsp block error"}
            return None  
        
        content_info = {"llm_rsp":llm_rsp, **one_content, **content_info, "pid":pid }
        return content_info 
    
    
    with ThreadPoolExecutor(max_workers=num_workers) as ex:
        predictions = ex.map(process_file, range(len(one_pid_list)))
    one_pid_info =  list(predictions)
    one_pid_info = [x  for x in one_pid_info  if x is not None ]
        # one_pid_info.append(  content_info )
    return one_pid_info 


def load_testcase_nl2code( load_p = "../dt_human_label/data/apps_nl2code_from_apps_cross_verify.jsonl" ):        
    lines = [json.loads(x) for x in open(load_p).readlines() ]
    lines = [x for x in lines if  "cvt_standard_" in x["problem_id"] ]
    lines = {"nl2code_"+x["task_id"] : x["tests"] for x in lines }
    
    return lines 


if __name__ == "__main__":
    read_p = sys.argv[-1]
    assert     os.path.isfile(read_p) , read_p 
    assert "fingerprinted000.jsonl" in os.path.basename( read_p ), read_p 
    new_save_p = read_p.replace("fingerprinted000.jsonl","fingerprinted000-extracted.jsonl" ) 
    
    extracted_list = extract_content( one_f = read_p )
    
    with open(new_save_p,"w") as fw :
        fw.write( "\n".join([json.dumps(x) for x in extracted_list ]))
    
    
