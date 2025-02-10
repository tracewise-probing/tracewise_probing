import os 
import json 
from glob2 import glob 
import numpy as np 

from collections import defaultdict 
import ast
import re 

def read_jsonl(jsonp ):
    with open( jsonp )  as fr :
        lines = [json.loads(x) for x in fr.readlines() ]
    return lines 


import ast
import inspect




def extract_function_signature( code , fn_name ):
    def _extract_function_signature(code: str, target_function_name: str) -> str:
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return None
    
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == target_function_name:
                args = ", ".join([arg.arg for arg in node.args.args])
                if node.args.vararg:
                    args += ", *" + node.args.vararg.arg
                if node.args.kwarg:
                    args += ", **" + node.args.kwarg.arg
                
                signature = f"def {node.name}({args}):"
                return signature
    
            elif isinstance(node, ast.ClassDef):
                for class_node in ast.walk(node):
                    if isinstance(class_node, ast.FunctionDef) and class_node.name == target_function_name:
                        args = ", ".join([arg.arg for arg in class_node.args.args])
                        if class_node.args.vararg:
                            args += ", *" + class_node.args.vararg.arg
                        if class_node.args.kwarg:
                            args += ", **" + class_node.args.kwarg.arg
                        signature = f"class {node.name}:\n    def {class_node.name}({args}):"
                        return signature
        return None
    
    
    finx = _extract_function_signature( code, target_function_name=fn_name )
    if finx is not None :
        return finx 
    
    def _extract():
        # Parse the code to create the AST
        try :
            tree = ast.parse(code)
        except :
            print ( code )
            return None 
    
        # Extract function signatures
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Get the function signature
                if node.name.strip() == fn_name.strip():
                    func_signature = f"def {node.name}({', '.join(arg.arg for arg in node.args.args)}):"
                    return func_signature 
    #
    fun_sg = _extract()
    
    
    if fun_sg is not None and "self" in fun_sg :
        mx = re.findall( r"\(\s*self\s*,", code )
        if mx is not None and len(mx) >0 :
            fun_sg  = "class Solution:\n    {}".format( fun_sg )
    return fun_sg 


if __name__=="__main__":
    corpus_dir = "/home/xxxxxxx/wj_code/dl_execute/ijcai25_tracewise/construct_dataset/dt_human_label/data/apps_problem.jsonl"
    corpus_dict =  read_jsonl( corpus_dir )
    corpus_dict = {x["pid"]:x  for x in corpus_dict }
    print ("total corpus" , len(corpus_dict) )
    
    search_dir = "/home/xxxxxxx/wj_code/dl_execute/ijcai25_tracewise/construct_dataset/dt_human_label/data/execute_dirs"
    
    f_list = glob( os.path.join(search_dir, "*extracted-verified.jsonl" ) )
    
    final_lines = []
    for one_f in f_list :
        lines = read_jsonl(one_f)
        final_lines += lines 
        
    raw_len = len( final_lines )    
    ### filter only verify 
    print ("raw.len", raw_len )
    final_lines = [x  for x in final_lines if x["verify"] ]
    print ("only verify ", len(final_lines) )
    
    ## sort the source 
    pid_collection = defaultdict( list )
    
    SORT_ORDER = {'apps':0, 'cross_1':1, 'verify':2 }
    final_lines.sort(key=lambda val: SORT_ORDER[val["source"] ] )
    
    # source_list = [x.get("source") for x in final_lines ]
    # print ( np.unique(source_list,return_counts=True ), source_list[:20], source_list[-20:] )
    threhold =2
    flattern_total_list = []
    
    for line_i in range(len(final_lines)) :
        line = final_lines[ line_i ]
        pid = line["task_id"].split("###")[0]
        final_lines[ line_i ].pop("pid",None)
        final_lines[ line_i ]["problem_id"]= pid
        
        if pid in pid_collection :
            exist = pid_collection[pid]
            if len(exist ) < threhold :
                pid_collection[pid].append( final_lines[ line_i ] )
                flattern_total_list.append( final_lines[ line_i ] )
        else:
            pid_collection[pid].append( final_lines[ line_i ] )
            flattern_total_list.append( final_lines[ line_i ] )
    
    print ("total corupus" , len(flattern_total_list)  , ", unique pid" , len( pid_collection ) )
    ### 
    
    
    
    ### read  nl2code curpus 
    for i in range(len(flattern_total_list) ) :
        line = flattern_total_list[i]
        flattern_total_list[i] ["status"] = 1 
        source = line["source"]
        
        corpus = corpus_dict[ line["problem_id"] ]
        flattern_total_list[i] ["question"] = corpus["question"]
        if source =="apps":
            flattern_total_list[i] ["fn_name"] = corpus["fn_name"]
            # flattern_total_list[i] ["starter_code"] = corpus["x_starter_code"]
            flattern_total_list[i] ["tests"] = corpus["input_output"]
            assert flattern_total_list[i] ["fn_name"] is not None ,(flattern_total_list[i], corpus )
            assert flattern_total_list[i] ["fn_name"] in flattern_total_list[i] ["tests"]   ,(flattern_total_list[i], corpus )
        else:
            inxout = json.loads( line["tests"] )
            flattern_total_list[i] ["fn_name"] = inxout["fn_name"]
            # flattern_total_list[i] ["starter_code"] = inxout["x_starter_code"]
            # flattern_total_list[i] ["tests"] = corpus["input_output"]
            assert flattern_total_list[i] ["fn_name"] is not None ,(flattern_total_list[i], corpus )
            assert flattern_total_list[i] ["fn_name"] in flattern_total_list[i] ["tests"]  ,(flattern_total_list[i], corpus )
        
        
        fn_name = flattern_total_list[i]["fn_name"]
        assert fn_name is not None , (flattern_total_list[i], corpus )
        
        extracted_code = flattern_total_list[i]["extracted_code"]
        
        func_signature = extract_function_signature( code=extracted_code , fn_name=fn_name )
        if func_signature is None :
            if  "lambda"  not in extracted_code:
                flattern_total_list[i] ["status"] = -1 
                continue 
            flattern_total_list[i]["starter_code"]= fn_name 
            # with open("/tmp/sp_code.txt","a") as fw:
            #     fw.write("\n========="*4)
            #     fw.write(extracted_code)
                
            flattern_total_list[i] ["status"] = 0 
            continue 
        
        assert func_signature is not None , ( extracted_code , fn_name )
        assert fn_name in func_signature , ( func_signature , fn_name )
        flattern_total_list[i]["starter_code"]= func_signature 
        
    raw_len = len( flattern_total_list )
    lines_str = [ json.dumps(x) for x in flattern_total_list if x["status"]>=0 ]
    raw_len_filter = len( lines_str )
    print ("processed", raw_len_filter , "total", raw_len )
    
    with open("./data/apps_nl2code_from_apps_cross_verify.jsonl", "w") as fw:
        fw.write( "\n".join(lines_str ) )
        
        
        
    