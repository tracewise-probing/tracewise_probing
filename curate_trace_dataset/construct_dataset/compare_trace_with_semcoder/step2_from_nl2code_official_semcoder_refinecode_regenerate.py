import os 
import json 
from glob2 import glob 


def read_jsonl( jsonp ):
    with open( jsonp ) as fr :
        lines = [json.loads(x) for x in fr.readlines() ]

    return lines 

import jinja2
environment = jinja2.Environment(loader=jinja2.FileSystemLoader("./") )

template = environment.get_template("step2_from_nl2code_official_semcoder_refinecode_regenerate.tpl.jinja")


if __name__ =="__main__":
    search_path = "/home/xxxxxxx/wj_code/dl_execute/LLaMA-Factory/data/semcoder_sharegpt_office_pyx_nl2code.jsonl"
    
    repair_lines = read_jsonl( search_path )
    
    # rationale_search_dir = "/home/xxxxxxx/wj_code/dl_execute/reverse_train_data_collecting/data/repair_docstring/save_dir"
    # rationale_search_dir="/home/xxxxxxx/wj_code/dl_execute/reverse_train_data_collecting/data/valid_data_rq1_semcoder_yx_r_reconstruct"
    # rationale_list =glob ( os.path.join(rationale_search_dir,"*jsonl")  )
    # rationale_mapping = [ ]
    # for one_rationale in rationale_list :
    #     rationale_mapping += read_jsonl( one_rationale )
    # ## mapping 
    # raw_len = len(rationale_mapping )
    # rationale_mapping = {x["task_id"].split("###idx:")[-1]:x["solution"] for x in rationale_mapping  if "[RATIONALE]" in x["solution"] and "[/RATIONALE]" in x["solution"] }
    
    print ("after filter",  len(repair_lines ) )
    
    
    
    
    split_str_list=[    
        "Write a solution to the following coding problem:\nYou are given",
        "Write a solution to the following coding problem:\nYou are tasked",
        "Write a solution to the following coding problem:\nYou are required",
        "Write a solution to the following coding problem:\n",
        ]
    
    item_list = [] 
    for i in range(len(repair_lines )):
        line = repair_lines[i]
        task_id = line["task_id"]
        
        
        instruction_str = line["messages"][0]["content"]
        for t in split_str_list :
            if t in instruction_str:
                instruction_str = instruction_str.split(t)[-1]
                break 
            
        instruction_str = instruction_str.strip()
        assert "Write a solution to the following coding problem" not in instruction_str 
        
        
        imple_str  = line["messages"][1]["content"]
        # imple_str  = imple_str.strip("````")
        assert "```" in imple_str 
        
        
        prompt  = template.render( 
            problem=instruction_str, 
            code_str=imple_str )
        
        msg = {"prompt":prompt,  "task_id": f"step2_official_semcoder_refinecode_regenerate###source:semcoder_sharegpt_office_pyx###idx:{task_id}"}
        # ret_item = {"task_id":one_line["uuid"], "prompt":prompt, "fix_extracted_code": msg2 }
        item_list.append( msg )


    
        
    with open( "./data/step2_from_nl2code_official_semcoder_refinecode_regenerate.jsonl","w") as fw :
        fw.write( "\n".join([json.dumps(x) for x in item_list]))