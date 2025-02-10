import os 
import json 
from glob2 import glob 


def read_jsonl( jsonp ):
    with open( jsonp ) as fr :
        lines = [json.loads(x) for x in fr.readlines() ]

    return lines 

import jinja2
environment = jinja2.Environment(loader=jinja2.FileSystemLoader("./") )

template = environment.get_template("step2_official_semcoder_refinecode_regenerate.tpl.jinja")


if __name__ =="__main__":
    search_path = "/mnt/local/home_dir/wj_code/dl_execute/LLaMA-Factory/data/backup_data/semcoder_sharegpt_office_pyx_r.jsonl"
    
    repair_lines = read_jsonl( search_path )
    
    # rationale_search_dir = "/home/xxxxxxx/wj_code/dl_execute/reverse_train_data_collecting/data/repair_docstring/save_dir"
    rationale_search_dir="/home/xxxxxxx/wj_code/dl_execute/reverse_train_data_collecting/data/valid_data_rq1_semcoder_yx_r_reconstruct"
    rationale_list =glob ( os.path.join(rationale_search_dir,"*jsonl")  )
    rationale_mapping = [ ]
    for one_rationale in rationale_list :
        rationale_mapping += read_jsonl( one_rationale )
    ## mapping 
    raw_len = len(rationale_mapping )
    rationale_mapping = {x["task_id"].split("###idx:")[-1]:x["solution"] for x in rationale_mapping  if "[RATIONALE]" in x["solution"] and "[/RATIONALE]" in x["solution"] }
    
    print ("raw.len" , raw_len ,"after filter",  len(rationale_mapping ) )
    
    
    
    
    
    item_list = [] 
    for i in range(len(repair_lines )):
        line = repair_lines[i]
        task_id = line["task_id"]
        
        
        buggy_code = line["messages"][0]["content"]
        assert "[Refined] and [/Refined]." in buggy_code 
        buggy_code = buggy_code.split("[Refined] and [/Refined].")[-1]
        
        
        rationale = rationale_mapping.get(task_id, None )
        
        
        prompt  = template.render( problem_bug_failtest=buggy_code, rationale=rationale )
        
        msg = {"prompt":prompt,  "task_id": f"step2_official_semcoder_refinecode_regenerate###source:semcoder_sharegpt_office_pyx_r###idx:{task_id}"}
        # ret_item = {"task_id":one_line["uuid"], "prompt":prompt, "fix_extracted_code": msg2 }
        item_list.append( msg )


    
        
    with open( "./data/step2_official_semcoder_refinecode_regenerate.jsonl","w") as fw :
        fw.write( "\n".join([json.dumps(x) for x in item_list]))