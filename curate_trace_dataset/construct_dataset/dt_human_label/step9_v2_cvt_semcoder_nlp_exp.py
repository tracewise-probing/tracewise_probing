import json 
import os 
import random 
random.seed(42)
from tqdm import tqdm 

import jinja2
environment = jinja2.Environment(loader=jinja2.FileSystemLoader("./") )

template = environment.get_template("step9_v2_semcoder.tpl.jinja")


def read_jsonl( josnp ):
    with open( josnp ) as fr :
        lines = [json.loads(x) for x in fr.readlines() ]
        
    return lines 



if __name__=="__main__":
    
    
    p_list = [
        "/home/xxxxxxx/wj_code/dl_execute/LLaMA-Factory/data/rq1_tracefmt_our_rnd.jsonl",
        "/home/xxxxxxx/wj_code/dl_execute/LLaMA-Factory/data/rq1_tracefmt_our_sim0.75.jsonl",
        "/home/xxxxxxx/wj_code/dl_execute/LLaMA-Factory/data/rq1_tracefmt_our_sim0.jsonl",
        ]
    final_lines = []
    
    for p in p_list :
        final_lines += read_jsonl( p )
        
    print ("raw jobs:" , len( final_lines ) )
    final_lines = {x["uuid"]:x for x in final_lines }
    final_lines = list( final_lines.values () )
    
    print ("tasked jobs:" , len( final_lines ) )
    
    ret_list = []
    
    for one_line in tqdm( final_lines ):
        
        msg1 = one_line["messages"][0]["content"]
        msg1 = msg1.split("now you can output the correct code here ")[0]
        msg1 = msg1.split("## Trace \n")[-1]
        assert "## Trace" not in msg1 
        assert "now you can output" not in msg1 
        
        msg2 = one_line["messages"][1]["content"]
        
        prompt  = template.render( OUR_TRACE=msg1, CORRECTED_PROGRAM=msg2 )
        
        ret_item = {"task_id":one_line["uuid"], "prompt":prompt, "fix_extracted_code": msg2 }
        
        ret_list.append( ret_item )

    random.shuffle( ret_list )

    with open( "./data/step9_cvt_semcoder_task_withcorrected.jsonl","w") as fw :
        fw.write( "\n".join([json.dumps(x) for x in ret_list]))