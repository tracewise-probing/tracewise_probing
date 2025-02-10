import json 
import os 
import sys 
import sys 

import hashlib
from tqdm import tqdm 
from glob2 import glob 

md5func =lambda x: hashlib.md5(x.encode('utf-8')).hexdigest() 


def read_jsonl( jsonp ):
    with open( jsonp ) as fr :
        lines = [json.loads(x) for x in fr.readlines() ]
    return lines 





import jinja2
environment = jinja2.Environment(loader=jinja2.FileSystemLoader("./") )

template = environment.get_template("step3_official_semcoder_refinecode_regenerate_UT2Fix.tpl.jinja")


def build_fix_buggy_code ( item ):
    msg = template.render( **item )
    if len(item["tests"] ) <=0:
        msg=  msg.replace("```\n** Test Cases ** \n```python","")
    return msg 
    ## extracted_code__tests__output 
    ##extracted_code 
    ##tests 




if __name__=="__main__":
    search_dir ="/home/xxxxxxx/wj_code/dl_execute/reverse_train_data_collecting/data/valid_data_rq1_semcoder_yx_r_reconstruct_init"
    search_list = glob( os.path.join(search_dir  , "*extracted-verified.jsonl"))
    # jsonp = sys.argv[-1]
    assert len(search_list), search_list
    for jsonp in tqdm( search_list ):
        assert os.path.isfile( jsonp ) , jsonp
        ##round 
    
        prompt_list = read_jsonl( jsonp  )
    
        print ("total prompt ,", len(prompt_list) )
        msg_list = [] 
        for item in prompt_list :
            if item["extracted_code__tests__pass"]:
                continue 
            task_id = item["uuid"]
            if "###round:3" in task_id :
                assert "###round:4" not in task_id  
                task_id = "{}###round:4".format( task_id )
            elif "###round:2" in task_id :
                task_id = "{}###round:3".format( task_id )
            elif "###round:1" in task_id :
                task_id = "{}###round:2".format( task_id )
            elif "###round:" not in task_id :
                task_id = "{}###round:1".format( task_id )
    
            msg = build_fix_buggy_code( item = item )
            md5 =  md5func( item["extracted_code"]+item["tests"] )
            msg_list.append({"task_id":task_id, "prompt":msg , "md5":md5 } )  
    
        print ("total valide pmpt ", len(msg_list) )
        save_dir = "./data/"
        save_path =  os.path.join( save_dir  , "step3_official_semcoder_refinecode_regenerate_UT2Fix.jsonl" ) 
        if len(msg_list) > 0 :
            with open( save_path , "a") as fw :
                msg_str = "\n".join( [json.dumps(x) for x in msg_list ])
                fw.write( msg_str + "\n")
                
            
            
            