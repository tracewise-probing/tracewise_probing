import json 
import  os 

import tiktoken
from glob2 import glob 

from concurrent.futures import ThreadPoolExecutor
encoding = tiktoken.encoding_for_model("gpt-4o-mini")

num_workers = os.cpu_count()-1 


def num_tokens_from_string(string: str ) -> int:
    num_tokens = len(encoding.encode(string))
    return num_tokens


def read_json( jsonp ):
    with open(jsonp) as fr:
        flines = fr.readlines() 
        try :
            lines = [json.loads(x) for x in  flines ]
        except  json.JSONDecodeError :
            new_line = []
            for one_l in  flines:
                try :
                    new_line.append( json.loads( one_l) )
                except  json.JSONDecodeError :
                    pass 
            return  new_line 
    return lines 

def pair_apps_buggy_fix(  ):

    fix_path = "data/with_simscore_apps_nl2code_from_apps_buggy_fix_pair.jsonl"
    fix_gt_line =  read_json(  fix_path )
    
    
    lines = {x["buggy_uuid"]:x for x in fix_gt_line }
    
    return lines


build_tpl = """
Provide a self-contained, buggy Python function or class that fails specific tests. Correct the provided BUGGY_PROGRAM. Output only the corrected code; do not include explanations, test cases, examples, or execution results.
{{trace_str}}
now you can output the correct code here 
```python
"""

if __name__ == "__main__":

    GLOB_GT_FIX = pair_apps_buggy_fix() 
    assert type(GLOB_GT_FIX) == dict , ( type(GLOB_GT_FIX), "GLOB_GT_FIX.type")
    print ( len(GLOB_GT_FIX), "GLOB_GT_FIX.len" )
    
    
    search_dir = "/home/xxxxxxx/wj_code/dl_execute/reverse_train_data_collecting/data/valid_data_rq1_corpus_nl2code_apps_HE"
    pttern = "*fingerprinted000-extracted-verified-accutraced.jsonl"
    trace_p_list = glob( os.path.join( search_dir, pttern ) )
    
    print ("total find trace file", len(trace_p_list) )
    
    
    
    trace_list = []
    for onef in trace_p_list :
        lines = read_json( onef )
        trace_list.extend( lines )
        
    print ("total find trace lines", len(trace_list) )
    
    
    
    
    
    def process_file( i ):
        if i% 1000 ==0 :
            print ( i , "/", len(trace_list) )
        item = trace_list[i]
        buggy_uuid = item["uuid"]
        
        if buggy_uuid not in GLOB_GT_FIX :
            return None, -1  
        
        gt_corpus = GLOB_GT_FIX[ buggy_uuid ]
        bug_code_trace = item["extracted_code"]
        bug_code_gt_trace = gt_corpus["buggy_extracted_code"]
        
        if bug_code_trace !=   bug_code_gt_trace :
            return None, -2 
        
        item["fix_extracted_code"]= gt_corpus["fix_extracted_code"]
        item["sim_score"]= gt_corpus["sim_score"]
        
        
        trace_next = build_tpl.replace("{{trace_str}}",  item ["bug_trace_TPL_NEXT"] )
        trace_our  = build_tpl.replace("{{trace_str}}",  item ["bug_trace_TPL_OUR01"] )
        trace_concise = build_tpl.replace("{{trace_str}}",  item ["bug_trace_TPL_CONCISETRACE"] )
        trace_exe  = build_tpl.replace("{{trace_str}}",   item ["bug_trace_TPL_CODEEXECUTOR"] )

        item["msg_next"]= [{"role":"user","content":trace_next}, {"role":"assistant","content": "```python\n{}\n```".format( item["fix_extracted_code"] ) }  ]
        item["msg_our"]= [{"role":"user","content":trace_our}, {"role":"assistant","content": "```python\n{}\n```".format( item["fix_extracted_code"] ) }  ]
        item["msg_concise"]= [{"role":"user","content":trace_concise}, {"role":"assistant","content": "```python\n{}\n```".format( item["fix_extracted_code"] ) }  ]
        item["msg_exe"]= [{"role":"user","content":trace_exe}, {"role":"assistant","content": "```python\n{}\n```".format( item["fix_extracted_code"] ) }  ]
        
        item["tksize_next"]= num_tokens_from_string( str( item["msg_next"] ) )
        item["tksize_our"]= num_tokens_from_string( str( item["msg_our"] ) )
        item["tksize_concise"]= num_tokens_from_string( str( item["msg_concise"] ) )
        item["tksize_exe"]= num_tokens_from_string( str( item["msg_exe"] ) )
        
        return item ,1 
    
    
    with ThreadPoolExecutor(max_workers=num_workers) as ex:
        predictions = ex.map(process_file, range(len(trace_list)))
    predictions =  list(predictions)
    raw_len = len( predictions )
    predictions = [x  for x,y in predictions  if y>=1 ]
    
    print ("filter =", len(predictions) , "/" , raw_len )
        
    msg_str = "\n".join( [json.dumps(x) for x in predictions ] ) 
    with open("./data/rq1_corpus_nl2code_apps_HE_trace_presetation.jsonl","w") as fw:
        fw.write( msg_str )
        