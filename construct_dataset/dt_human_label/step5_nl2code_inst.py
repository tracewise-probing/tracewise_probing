import os 
import json 
from tqdm import tqdm 
import random 
import traceback 
import jinja2
environment = jinja2.Environment(loader=jinja2.FileSystemLoader("./") )

template = environment.get_template("step5_nl2code.tpl.jinja")

template_testcase = environment.get_template("step5_nl2code_testcase.tpl.jinja")

import tiktoken
encoding = tiktoken.encoding_for_model("gpt-4o-mini")
def num_tokens_from_string(string: str ) -> int:
    """Returns the number of tokens in a text string."""
    num_tokens = len(encoding.encode(string))
    return num_tokens

def read_jsonl( jsonp ):
    
    with open( jsonp ) as fr :
        lines = [json.loads(x) for x in fr.readlines() ]
    return lines 

import  copy 

if __name__ =="__main__":
    
    read_p = "data/apps_nl2code_from_apps_cross_verify.jsonl"
    
    lines = read_jsonl( read_p )
    
    task_list = []
    task_testcase_list = []
    
    for i in tqdm ( range( len(lines) ) ) :
        item = lines[i ]
        
        task_id = item["task_id"]
        task_id = task_id .replace ("cvt_standard_","nl2code_cvt_standard_")
        task_withtestcase_id = task_id .replace ("cvt_standard_","nl2cod_withtest_cvt_standard_")
        
        prompt = template.render( **item )
        tk_size = num_tokens_from_string( prompt)
        assert tk_size<10000 
        task_list.append( {"task_id":task_id, "prompt":prompt, "tk_size":tk_size } )
        
        try  :
            item1 = copy.deepcopy(item)
            tests =  item1["tests"]
            tests = json.loads( tests )
            assert tests["fn_name"] in item["starter_code"], ( tests, item1["starter_code"], "======"*8 ,item1 )
            tests = json.dumps( tests, indent=4 )
            item1["tests"] = tests 
            prompt_withtestcase = template_testcase.render( **item1 )
            
            tk_size = num_tokens_from_string( prompt_withtestcase )
            if tk_size<10000:
                task_testcase_list.append( {"task_id":task_withtestcase_id, "prompt":prompt_withtestcase , "tk_size":tk_size } )
            # else:
            #     task_testcase_list.append( {"task_id":task_withtestcase_id, "prompt":prompt , "tk_size":-1 } )
            
        except ValueError as ex :
            traceback.print_exc()
            pass 
            
        
        
    random.shuffle( task_list )
    random.shuffle( task_testcase_list )
    print ("w/o testcase" , len(task_list) )
    lines_str = "\n".join([json.dumps(x) for x in task_list])
    with open("./data/rq1_corpus_nl2code_apps_HE.jsonl","w") as fw:
        fw.write( lines_str )
        
        
    print ("w/ testcase" , len(task_testcase_list) )
    lines_str = "\n".join([json.dumps(x) for x in task_testcase_list])
    with open("./data/rq1_corpus_nl2code_withtestcase_apps_HE.jsonl","w") as fw:
        fw.write( lines_str )
        
        