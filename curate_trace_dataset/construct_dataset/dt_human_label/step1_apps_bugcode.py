import os 
import json 

from collections import defaultdict 

import numpy  as np 
from concurrent.futures import ThreadPoolExecutor
import traceback 


num_workers =  os.cpu_count()-1  

if __name__=="__main__":
    read_dir = "/home/xxxxxxx/wj_code/dl_execute/reverse_train_data_collecting/data"
    read_p = os.path.join( read_dir, "convers_collections_list.jsonl" )
    
    save_dir = "/home/xxxxxxx/wj_code/dl_execute/ijcai25_tracewise_data_dirs/human_label_data"
    
    
        
    
    # def process_large_jsonl(file_path, chunk_size):
    #     with open(file_path, 'r') as file:
    #         chunk = []
    #         for i, line in enumerate(file):
    #             try :
    #                 chunk.append(json.loads(line.strip()))
    #             except json.decoder.JSONDecodeError as ex :
    #                 continue 
    #             # Process the chunk if it reaches the desired size
    #             if (i + 1) % chunk_size == 0:
    #                 process_chunk(chunk)
    #                 chunk = []  # Reset chunk
    #         # Process any remaining data
    #         if chunk:
    #             process_chunk(chunk)
    # pid_collection = {}#(list )
    pid_collection = defaultdict(list )
    
    with open( read_p ) as fr :
        lines = fr.readlines() #[:10000]
    
    print ( "total.len" , len(lines) )
    total_len = len( lines )
    def process_file( i ):
        
        try :
            
            if i % 1000 == 0 :
                v_list = []
                for k,v in pid_collection.items() :
                    v_list+=[vv["score"] for vv in v ]
                     
                mean_v = np.mean( np.array(v_list).reshape(-1) )
                # Replace with your processing logic
                print(f"Processing chunk with {i} /{total_len} , current len of dict , {len(pid_collection)}, current mean score , {mean_v} ")
    
            
            one_item = lines [i] 
            try :
                one_item = json.loads( one_item )   
            except json.decoder.JSONDecodeError as ex :
                return None 
            
            def process_one ( item ):
                def get_pid ( uuid ):
                    pid = uuid.split("#problem_id:")[-1]
                    pid = pid .split("###")[0]
                    pid = int(pid )
                    return pid 
                
                pid = get_pid( item ["uuid"] )
                score = item ["verify"]
                if score is None :
                    return None 
                score = np.array( score )
                if -2 in score :
                    # print ( item["uuid"])
                    return None 
                
                score [ score==-1 ] = 1 
                assert  min( score ) in [0,1] ,( item ["verify"]  )
                score = float( np.mean( score ) )
                if score  >=1 :
                    return None 
                
                def valid_sanitized( sanitized ):
                    if sanitized is None or type(sanitized)!=str or  len(sanitized)<= 4 :
                        return False 
                    return True 
                is_valid = valid_sanitized( item ["sanitized"] )
                if not is_valid :
                    return None 
                
                set_v = {"solution": item["sanitized"] , "score": score, "uuid":item["uuid"], "pid":pid  }
                
                if pid not in pid_collection :
                    pid_collection[ pid ] .append(  set_v  )
                else:
                    exist  =  pid_collection[ pid ]
                    # exist  = exist [-1]
                    exist_score =min( [  x ["score"] for x in exist  ])
                    if score < exist_score:
                        pid_collection[ pid ] .append(  set_v  )
                    # exist  =  pid_collection[ pid ]
                    # exist = exist[:5]
                    # pid_collection[ pid ] = exist 
                    
                return None 
            
            if "rd1" in one_item :
                process_one( item = one_item ["rd1"] )
            if "rd2" in one_item :
                process_one( item = one_item ["rd2"] )
            if "rd3" in one_item :
                process_one( item = one_item ["rd3"] )
                
        except : 
            traceback.print_exc() 
    
    with ThreadPoolExecutor(max_workers=num_workers) as ex:
        predictions = ex.map(process_file, range(len(lines ) ) )
    predictions =  list(predictions)
    
    
    json_list = []
    
    v_list = []
    for k,v in pid_collection.items() :
        v_list+=[vv["score"] for vv in v ]
        json_list.extend( v[:5] )
        
    mean_v = np.mean( np.array(v_list).reshape(-1) )

    print(f"final current len of dict , {len(pid_collection)}, current mean score , {mean_v} ")
    
    with open( os.path.join( save_dir , "human_apps_repair_worst_fivecases.jsonl" ) ,"w") as fw :
        fw.write( "\n".join([json.dumps(x) for x in json_list ]))
    
    

