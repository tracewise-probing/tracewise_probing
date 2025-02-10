import os 
import json 



def read_jsonl( jsonp ):
    with open( jsonp ) as fr :
        lines = [json.loads(x) for x in fr.readlines() ]

    return lines 

import jinja2
environment = jinja2.Environment(loader=jinja2.FileSystemLoader("./") )

template = environment.get_template("step1_copy_step9_v2_semcoder.tpl.jinja")


if __name__ =="__main__":
    search_path = "/mnt/local/home_dir/wj_code/dl_execute/LLaMA-Factory/data/backup_data/semcoder_sharegpt_office_pyx_r.jsonl"
    
    repair_lines = read_jsonl( search_path )
    
    
    item_list = [] 
    for i in range(len(repair_lines )):
        line = repair_lines[i]
        task_id = line["task_id"]
        
        fix_code = line["messages"][1]["content"]
        assert "[/MONOLOGUE]" in fix_code 
        fix_code = fix_code.split("[/MONOLOGUE]")[-1]
        
        buggy_code = line["messages"][0]["content"]
        assert "[Refined] and [/Refined]." in buggy_code 
        buggy_code = buggy_code.split("[Refined] and [/Refined].")[-1]
        
        
        
        
        prompt  = template.render( OUR_TRACE=buggy_code, CORRECTED_PROGRAM=fix_code )
        
        msg = {"prompt":prompt ,"buggy_code":buggy_code , "fix_code":fix_code, "task_id": f"semcoder_reconstruct_phi4###source:semcoder_sharegpt_office_pyx_r###idx:{task_id}"}
        # ret_item = {"task_id":one_line["uuid"], "prompt":prompt, "fix_extracted_code": msg2 }
        item_list.append( msg )


    
        
    with open( "./data/step1_compare_trace_with_semcoder.jsonl","w") as fw :
        fw.write( "\n".join([json.dumps(x) for x in item_list]))