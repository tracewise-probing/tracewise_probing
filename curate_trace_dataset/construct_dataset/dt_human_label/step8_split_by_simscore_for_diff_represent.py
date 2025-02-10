import json 
import os 
import random 

random.seed(42)

def read_jsonl( jsonp  ):
    with open( jsonp ) as fr :
        lines =[ json.loads(x) for x in fr.readlines() ] 
    return lines 



def build_msg( item  ):
    bug,fix = item["extracted_code"], item["fix_extracted_code"]
    
    msg="""
Provide a self-contained, buggy Python function or class that fails specific tests. Correct the provided BUGGY_PROGRAM. Output only the corrected code; do not include explanations, test cases, examples, or execution results.
**BUGGY_PROGRAM**
```python
{}
```
""".format( bug )
    fixmsg = """
```python
{}
```
""".format( fix )
    
    ret_item = {
        "messages":    [ {"role":"user","content":msg }, {"role":"assistant","content":fixmsg },  ] ,   
        "uuid":item["uuid"],
        "sim_score":item["sim_score"],
        "token_size":-1
        }
    return ret_item 

if __name__=="__main__":
    josnp = "./data/rq1_corpus_nl2code_apps_HE_trace_presetation.jsonl"
    
    
    sim_score_threhold = 0.75
    
    
    raw_lines = read_jsonl( josnp )
    
    
    greater_than_list = [ x   for x in raw_lines if x["tksize_next"]< 2048 and \
                         x["tksize_our"]< 2048 and \
                          x["tksize_concise"]< 2048 and \
                          x["tksize_exe"]< 2048 and \
                          x["sim_score"] > sim_score_threhold 
                          ]
    print ("init. list" ,len(greater_than_list) )
    
    
    tracename = ["next","our","exe","concise"]
    
    for one_trace in tracename:
        xname = f"msg_{one_trace}"
        tk_xname = f"tksize_{one_trace}"
        trace_x_list = [{"messages":x[ xname ],"uuid":x["uuid"],"token_size":x[tk_xname]  ,"sim_score":x["sim_score"] } for x in  greater_than_list ]
        save_path = f"./data/llama-factory/rq1_tracefmt_{one_trace}_sim{sim_score_threhold}.jsonl"
        with open( save_path , "w") as fw:
            fw.write( "\n".join([json.dumps(x) for x in trace_x_list ]))
            
            
    naive_list = [ build_msg(x) for x in greater_than_list ]
    save_path = f"./data/llama-factory/rq1_tracefmt_naive_sim{sim_score_threhold}.jsonl"
    with open( save_path , "w") as fw:
        fw.write( "\n".join([json.dumps(x) for x in naive_list ]))
            
            
    



    less_than_list = [ x   for x in raw_lines if x["tksize_next"]< 2048 and \
                         x["tksize_our"]< 2048 and \
                          x["tksize_concise"]< 2048 and \
                          x["tksize_exe"]< 2048 and \
                          x["sim_score"] < sim_score_threhold 
                          ]
    print ("init. list" ,len(less_than_list) )
    random.shuffle( less_than_list )
    less_than_list = less_than_list[ :len(greater_than_list) ]
    print ("than. list" ,len(less_than_list) )
    
    tracename = ["next","our","exe","concise"]
    
    for one_trace in tracename:
        xname = f"msg_{one_trace}"
        tk_xname = f"tksize_{one_trace}"
        trace_x_list = [{"messages":x[ xname ],"uuid":x["uuid"],"token_size":x[tk_xname]  ,"sim_score":x["sim_score"] } for x in  less_than_list ]
        save_path = f"./data/llama-factory/rq1_tracefmt_{one_trace}_sim0.jsonl"
        with open( save_path , "w") as fw:
            fw.write( "\n".join([json.dumps(x) for x in trace_x_list ]))
            
    naive_list = [ build_msg(x) for x in less_than_list ]
    save_path = f"./data/llama-factory/rq1_tracefmt_naive_sim0.jsonl"
    with open( save_path , "w") as fw:
        fw.write( "\n".join([json.dumps(x) for x in naive_list ]))
            


    rnd_list = [ x   for x in raw_lines if x["tksize_next"]< 2048 and \
                         x["tksize_our"]< 2048 and \
                          x["tksize_concise"]< 2048 and \
                          x["tksize_exe"]< 2048 
                          ]
    random.shuffle( rnd_list )
    print ("init. list" ,len(rnd_list) )
    rnd_list = rnd_list[ :len(greater_than_list) ]
    print ("than. list" ,len(rnd_list) )
    
    tracename = ["next","our","exe","concise"]
    
    for one_trace in tracename:
        xname = f"msg_{one_trace}"
        tk_xname = f"tksize_{one_trace}"
        trace_x_list = [{"messages":x[ xname ],"uuid":x["uuid"],"token_size":x[tk_xname]  ,"sim_score":x["sim_score"] } for x in  rnd_list ]
        save_path = f"./data/llama-factory/rq1_tracefmt_{one_trace}_rnd.jsonl"
        with open( save_path , "w") as fw:
            fw.write( "\n".join([json.dumps(x) for x in trace_x_list ]))
            
    naive_list = [ build_msg(x) for x in rnd_list ]
    save_path = f"./data/llama-factory/rq1_tracefmt_naive_rnd.jsonl"
    with open( save_path , "w") as fw:
        fw.write( "\n".join([json.dumps(x) for x in naive_list ]))
            
