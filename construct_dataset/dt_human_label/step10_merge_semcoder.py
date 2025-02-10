import os 
import json 
from glob2 import glob 

def read_jsonl(jsonp ):
    with open( jsonp )as fr :
        lines = [json.loads(x) for x in fr.readlines() ]
    return lines 

import tiktoken
encoding = tiktoken.encoding_for_model("gpt-4o-mini")


def num_tokens_from_string(string: str ):
    num_tokens = len(encoding.encode(string))
    return num_tokens


if __name__=="__main__":
    
    target_dir = "/home/xxxxxxx/wj_code/dl_execute/LLaMA-Factory/data"
    target_list =[
        "rq1_tracefmt_naive_rnd.jsonl",
        "rq1_tracefmt_naive_sim0.75.jsonl",
        "rq1_tracefmt_naive_sim0.jsonl",
        ]
    
    
    search_dir = "/home/xxxxxxx/wj_code/dl_execute/reverse_train_data_collecting/data/valid_rq1_nl2code_cvt_semcoder"
    search_list = glob( os.path.join(search_dir, "step9_cvt_semcoder_task*jsonl"))
    
    print ("total find ", len(search_list) )
    
    semcoder_list_mapping  = []
    for one_tgt  in search_list :
        semcoder_list_mapping+= read_jsonl(one_tgt)
    
    print ("synthe list ", len(semcoder_list_mapping) )
    semcoder_list_mapping = {x["task_id"]:x for x in semcoder_list_mapping }
    print ("synthe list.unique ", len(semcoder_list_mapping) )
    
    
    for onef  in target_list:
        onef = os.path.join( target_dir , onef )
        tgt_lines  = read_jsonl(jsonp =  onef )
        tgt_lines_y  = read_jsonl(jsonp =  onef )
        
        for i in range( len(tgt_lines) ) :
            line = tgt_lines[i]
            line_y = tgt_lines_y[i]
            task_id = line["uuid"]
            sythsis = semcoder_list_mapping[ task_id ]["solution"]

            user_content = line["messages"][0]["content"]
            sythsis = sythsis.replace("[MONOLOGUE]","").replace("[/MONOLOGUE]","")
            user_content = user_content+"\n"+ sythsis 
            tgt_lines[i]["messages"][0]["content"] = user_content
            tk_size = num_tokens_from_string( str( tgt_lines[i]["messages"] ) )
            tgt_lines[i]["token_size"] = tk_size
            
            user_content = line_y["messages"][1]["content"]
            sythsis= sythsis.replace("[MONOLOGUE]","").replace("[/MONOLOGUE]","")
            user_content = user_content+"\n"+ sythsis 
            tgt_lines_y[i]["messages"][1]["content"] = user_content
            # tk_size = num_tokens_from_string( str( tgt_lines[i]["messages"] ) )
            tgt_lines_y[i]["token_size"] = tk_size
            

        
        onef_save=  onef.replace(".jsonl","-tmp.jsonl").replace("naive","semcoder_x")
        print ("---onef_save", onef_save )
        with open(onef_save, "w") as fw :
            fw.write( "\n".join([json.dumps(x) for x in tgt_lines ] ) )
        onef_save=  onef.replace(".jsonl","-tmp.jsonl").replace("naive","semcoder_y")
        print ("---onef_save", onef_save )
        with open(onef_save, "w") as fw :
            fw.write( "\n".join([json.dumps(x) for x in tgt_lines_y ] ) )