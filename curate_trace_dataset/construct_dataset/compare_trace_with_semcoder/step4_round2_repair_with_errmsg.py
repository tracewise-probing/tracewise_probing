import json 
import os 
import sys 
import sys 

import hashlib

from  glob2 import glob 
from concurrent.futures import ThreadPoolExecutor
import tiktoken

from tqdm import tqdm 

num_workers= os.cpu_count()-1 
md5func =lambda x: hashlib.md5(x.encode('utf-8')).hexdigest() 
encoding = tiktoken.encoding_for_model("gpt-4o-mini")


import jinja2
environment = jinja2.Environment(loader=jinja2.FileSystemLoader("./") )
template = environment.get_template("step4_official_semcoder_refinecode_regenerate_UT2Fix_recursive.tpl.jinja")


from x_utils import parse_report_to_extract_fail_c_and_pass_c

def num_tokens_from_string(string: str ) -> int:
    """Returns the number of tokens in a text string."""
    num_tokens = len(encoding.encode(string))
    return num_tokens




def read_jsonl( jsonp ):
    with open( jsonp ) as fr :
        lines = [json.loads(x) for x in fr.readlines() ]
    return lines 


def load_verifi_test( round_search_dir ):# sub_dir,  split = "init" ):
    

    
    def _load_verifi_test( sub_dir,  split = "init" ):
        pattern = "*fingerprinted000-extracted-verified.jsonl"
        verify_p_list  = glob( os.path.join( sub_dir, pattern )) 
        verify_list = []
        
        for onef in verify_p_list :
            verify_list += read_jsonl( onef )
            
        print ("in subdir ", sub_dir )
    
        ret_info = []
        for i in range( len(verify_list)):
            line = verify_list[i]
            task_id = line["task_id"]
            
            idx = task_id.split("###llm_md5")[0]
            idx = idx.split("###idx:")[-1]
            assert len(idx) == len("92d88b249426062a1eae7c670766e639"), (task_id, idx  )
            key = "{}__{}".format(split, idx) 
            ret_info.append( {"key":key , func_key:line[func_key], "tests":line["tests"],pass_key: line[pass_key], err_key : line[err_key] } )
            # md5 =  md5func( item["extracted_code"]+item["tests"] )
        return ret_info 

    big_mapping = []
    
    ## load init 
    for split, sub_tgt_dir in STEP_MAPPING_META.items():
        sub_dir = os.path.join(round_search_dir, sub_tgt_dir)
        if not  os.path.isdir( sub_dir ):
            print (" missing ", sub_dir )
            continue 
        print ("start scan ", split, "=====>", sub_tgt_dir )
        big_mapping  += _load_verifi_test( sub_dir = sub_dir , split =split ) 
        
    # print ("total ", len(big_mapping ) )
    # print ("total ", list( big_mapping )[:5] )
    ## map md5 
    def process_file(i):
        item = big_mapping[i]
        md5 =  md5func( item["extracted_code"]+item["tests"] )
        big_mapping[i]["md5" ] = md5
        return None

    with ThreadPoolExecutor(max_workers=num_workers) as ex:
        predictions = ex.map(process_file, range(len(big_mapping)))
    predictions =  list(predictions)
    
    
    return big_mapping 


from num2words import num2words



def int_to_ordinal_word(n):
    return num2words(n, to='ordinal')


def build_prompt( task_item  , max_tk_size=10000   ):
    round_cur = task_item["cur_round"]
    round_rang_list  = list( range(1, round_cur, 1 ) )
    
    idx = task_item["idx"]
    
    round_msg_list = []
    for one_round  in round_rang_list  :

        assert one_round >0 
        if one_round == 1 :
            key = "init__{}".format( idx ) 
        else :
            key = "round{}__{}".format(one_round, idx ) 
    
    
        round_item = big_mapping[ key ]
        
        # round_str= int_to_ordinal_word( one_round )
        
        round_msg = dict(
            # round_str=round_str, 
            extracted_code= round_item["extracted_code"], 
            tests= round_item["tests"], 
            extracted_code__tests__output= round_item["extracted_code__tests__output"], 
        )
        parsed_info = parse_report_to_extract_fail_c_and_pass_c( round_msg["extracted_code__tests__output"])
        if "invalid" in parsed_info :
            continue 
        round_msg["score"]= parsed_info 
        round_msg_list.append( round_msg )
    
    
    assert "extracted_code__tests__output" in task_item , task_item 
    assert "extracted_code" in task_item , task_item 
    assert "tests" in task_item , task_item 
     
    cur_item = dict(
        # round_str= int_to_ordinal_word( round_cur ),
        extracted_code= task_item["extracted_code"], 
        tests= task_item["tests"], 
        extracted_code__tests__output= task_item["extracted_code__tests__output"], 
        ) 
    parsed_info = parse_report_to_extract_fail_c_and_pass_c( cur_item["extracted_code__tests__output"])
    if "invalid" not in parsed_info :
        cur_item["score"]= parsed_info 
        round_msg_list.append( cur_item )
    
    raaw_ =[x["score"]["pass_c"] for x in round_msg_list ] 
    # assert len(round_msg_list) > 0 , task_item 
    if len( round_msg_list )== 0 :
        if "score" not  in cur_item:
            return None 
        # print ( "warning :::" , task_item["task_id"],"---> not candidate " )
        round_msg_list = [ cur_item ]
    else:
        round_msg_list = list( sorted (round_msg_list, key= lambda x: x["score"]["pass_c"],reverse=False ) )
    
    sorted_ =[x["score"]["pass_c"] for x in round_msg_list ] 
    
    
    print (raaw_, "--->",  sorted_ )
    round_msg_list = round_msg_list[-1:]

    
    msg = None 
    while True :
        
        if  len(round_msg_list)<=0:
            return None 
        
        round_next  =len(round_msg_list) +1 
        round_next_str = int_to_ordinal_word(round_next)
        ## name each with round str 
        for i in range( len(round_msg_list) ) :
            round_msg_list[i]["round_str"] = int_to_ordinal_word( i+1 )
        
        msg = template.render( 
            round_item_list=round_msg_list,
            round_next_str=round_next_str,
            
            )
        
        msg_token_size= num_tokens_from_string( msg )
        if msg_token_size> max_tk_size :
            print ("drop one ...","msg_token_size:", msg_token_size , "cur_len:" ,len(round_msg_list)  )
            round_msg_list = round_msg_list[1:]
        else :
            break 
    
    
    return {**task_item, "prompt": msg } 


pass_key= "extracted_code__tests__pass"
func_key = "extracted_code"
err_key = pass_key.replace("__pass","__output")


if __name__=="__main__":
    
    
    scan_dir="nl2code"
    # scan_dir="r"
    
    ## inference
    if scan_dir == "r":
    
        STEP_MAPPING_META= {
            "init":"valid_data_rq1_semcoder_yx_r_reconstruct_init",
            "round1":"valid_data_rq1_semcoder_yx_r_reconstruct_round1",
            "round2":"valid_data_rq1_semcoder_yx_r_reconstruct_round2",
            "round3":"valid_data_rq1_semcoder_yx_r_reconstruct_round3",
            "round4":"valid_data_rq1_semcoder_yx_r_reconstruct_round4",
            "round5":"valid_data_rq1_semcoder_yx_r_reconstruct_round5",
            "round6":"valid_data_rq1_semcoder_yx_r_reconstruct_round6",
            "round7":"valid_data_rq1_semcoder_yx_r_reconstruct_round7",
            }
        
        # target_sub_dir = "valid_data_rq1_semcoder_yx_r_reconstruct_init"
        # target_sub_dir = "valid_data_rq1_semcoder_yx_r_reconstruct_round1"
        # target_sub_dir = "valid_data_rq1_semcoder_yx_r_reconstruct_round2"
        # target_sub_dir = "valid_data_rq1_semcoder_yx_r_reconstruct_round3"
        # target_sub_dir = "valid_data_rq1_semcoder_yx_r_reconstruct_round4"
        target_sub_dir = "valid_data_rq1_semcoder_yx_r_reconstruct_round5"
        
    else:
        STEP_MAPPING_META= {
            "init":"valid_data_rq1_semcoder_yx_nl2code_reconstruct_init",
            "round1":"valid_data_rq1_semcoder_yx_nl2code_reconstruct_round1",
            "round2":"valid_data_rq1_semcoder_yx_nl2code_reconstruct_round2",
            "round3":"valid_data_rq1_semcoder_yx_nl2code_reconstruct_round3",
            "round4":"valid_data_rq1_semcoder_yx_nl2code_reconstruct_round4",
            "round5":"valid_data_rq1_semcoder_yx_nl2code_reconstruct_round5",
            "round6":"valid_data_rq1_semcoder_yx_nl2code_reconstruct_round6",
            "round7":"valid_data_rq1_semcoder_yx_nl2code_reconstruct_round7",
            }
        target_sub_dir = "valid_data_rq1_semcoder_yx_nl2code_reconstruct_init"
        target_sub_dir = "valid_data_rq1_semcoder_yx_nl2code_reconstruct_round1"

    print ( target_sub_dir )

    # assert "round" in target_sub_dir or "init" in target_sub_dir ,(target_sub_dir, )
    task= "init" if "_init" in target_sub_dir else     "round"

    
    ## load init 
    round_search_dir  =  "/home/xxxxxxx/wj_code/dl_execute/reverse_train_data_collecting/data" 
    print ("load_init")
    big_mapping = load_verifi_test( round_search_dir )
    big_mapping = {x["key"]:x for x in big_mapping }


    # ##round 
    prompt_list = []
    
    target_list = glob( os.path.join( round_search_dir ,target_sub_dir, "*fingerprinted000-extracted-verified.jsonl" ) )

    for jsonp in target_list :
        prompt_list += read_jsonl( jsonp  )
    #


    print ("total prompt ,", len(prompt_list) )
    msg_list = [] 
    round_list= []
    roundint_list= []
    skip_success = []
    for item in prompt_list :
        if item["extracted_code__tests__pass"] and len(item["tests"]):

            parsed_info = parse_report_to_extract_fail_c_and_pass_c( item["extracted_code__tests__output"])
            if "invalid" not  in parsed_info and parsed_info["pass_c"]>0 and parsed_info["fail_c"]==0 and parsed_info["error_c"] == 0   :
                skip_success.append( item )
                continue 
            
        task_id = item["uuid"]
        if "###round:6" in task_id :
            assert "###round:7" not in task_id  
            task_id = "{}###round:7".format( task_id )
            round_list.append("round7")
            roundint = 7
        elif "###round:5" in task_id :
            assert "###round:6" not in task_id  
            task_id = "{}###round:6".format( task_id )
            round_list.append("round6")
            roundint = 6
        elif "###round:4" in task_id :
            assert "###round:5" not in task_id  
            task_id = "{}###round:5".format( task_id )
            round_list.append("round5")
            roundint = 5 
        elif "###round:3" in task_id :
            assert "###round:4" not in task_id  
            task_id = "{}###round:4".format( task_id )
            round_list.append("round4")
            roundint = 4 
        elif "###round:2" in task_id :
            task_id = "{}###round:3".format( task_id )
            round_list.append("round3")
            roundint = 3 
        elif "###round:1" in task_id :
            task_id = "{}###round:2".format( task_id )
            round_list.append("round2")
            roundint = 2
        elif "###round:" not in task_id :
            task_id = "{}###round:1".format( task_id )
            round_list.append("round1")
            roundint = 1 

        idx = task_id.split("###llm_md5")[0]
        idx = idx.split("###idx:")[-1]

        roundint_list.append( roundint )
        # msg = build_fix_buggy_code( item = item )
        # md5 =  md5func( item["extracted_code"]+item["tests"] )
        
        msg_list.append({"idx":idx , 
                         "task_id":task_id, 
                         func_key:item[func_key], 
                         "tests":item["tests"], 
                         err_key:item[err_key] , 
                         "cur_round":roundint   } )  




    assert len(set(round_list)) == 1 , (set(round_list))
    assert len(set(roundint_list)) == 1 , (set(roundint_list))
    round_list_str = str(round_list[0])
    round_int  = str(roundint_list[0])
    

    print ("skip success", len(skip_success) )
    print ( round_list_str ,"round_list_str", "round.int ", round_int )
    
    msg_list_ret = []
    
    for task_item  in tqdm( msg_list ) :
        msg_item = build_prompt( task_item = task_item )
        if msg_item is None :
            continue 
        msg_list_ret.append( msg_item )
    
    
    
    
    
    print ("total valide pmpt ", len(msg_list) )
    save_dir = "./data/"
    if scan_dir!="r":
        save_path =  os.path.join( save_dir  , f"step4_semcoder_yx_nl2code_reconstruct_UT2Fix_{round_list_str}.jsonl" ) 
    else:
        save_path =  os.path.join( save_dir  , f"step4_semcoder_yx_r_reconstruct_UT2Fix_{round_list_str}.jsonl" ) 
    if len(msg_list_ret) > 0 :
        with open( save_path , "w") as fw :
            msg_str = "\n".join( [json.dumps(x) for x in msg_list_ret ])
            fw.write( msg_str + "\n")
    #

            
    
            