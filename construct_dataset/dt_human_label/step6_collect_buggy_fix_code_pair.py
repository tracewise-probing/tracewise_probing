import os 
import json 
from glob2 import glob 
import sys 

from collections import defaultdict 

from tqdm import tqdm 

def read_jsonl( jsonp ):
    
    with open( jsonp ) as fr :
        lines = [json.loads(x) for x in fr.readlines() ]
    return lines 

GT_DICT = {} 

def filter_target_buggy_code (lines ):
    '''
    err_list == []
    verify == false 
    '''
    lines = [ x for x in lines if "verify" in x and x["verify"]==False and x["err_list"] == [] ] 

    new_lines = []
    
    for one_line in lines :
        task_id =     one_line["task_id"]
        task_id = task_id.split("cvt_standard_")[-1]
        if task_id not in GT_DICT:
            print (one_line )
            continue 
        
        gt_corpus = GT_DICT[task_id]
        
        test_cases = json.loads( gt_corpus["tests"] )
        fn_name = test_cases["fn_name"]
        assert fn_name is not None and len(fn_name)>0   ,(gt_corpus,one_line )
        assert fn_name in one_line["extracted_code"] ,(gt_corpus,one_line )
        assert fn_name in gt_corpus["extracted_code"]  ,(gt_corpus,one_line )
        
        # print ( gt_corpus )
        # print ( list(gt_corpus) )
        
        new_item = {
            "common_id": task_id,
            
            "buggy_uuid":one_line["uuid"],
            "fix_uuid":gt_corpus["task_id"],

            "buggy_extracted_code":one_line["extracted_code"],
            "fix_extracted_code":gt_corpus["extracted_code"],

            "buggy_verify":one_line["verify"],
            "fix_verify":gt_corpus["verify"],

            "buggy_verify_list":one_line["verify_list"],
            
            "tests":gt_corpus["tests"],
            "source":gt_corpus["source"],
            }
        new_lines.append( new_item )
        
    return new_lines 

def load_gt_pair( gt_jsonp="data/apps_nl2code_from_apps_cross_verify.jsonl" ):
    
    gt_lines = read_jsonl( gt_jsonp ) 
    get_part_pid = lambda x: x["task_id"].split("cvt_standard_")[-1]
    
    gt_lines = { get_part_pid(x):x  for x in gt_lines }
    print ("for gt ", len(gt_lines) )
    return gt_lines 

if __name__ == "__main__":
    search_dir  =  "/home/xxxxxxx/wj_code/dl_execute/reverse_train_data_collecting/data/valid_data_rq1_corpus_nl2code_apps_HE"
    search_pattern = "*fingerprinted000-extracted-verified.jsonl"
    
    
    GT_DICT = load_gt_pair() 

    
    fl_list = glob( os.path.join(search_dir, search_pattern) )
    print ("total find ," , len(fl_list ) )
    
    final_list = [] 
    
    for one_f in tqdm( fl_list ):
        lines =  read_jsonl( one_f )
        raw_len = len(lines)
        lines = filter_target_buggy_code( lines )
        cur_len = len(lines)
        
        if cur_len==0 :
            print ( one_f )
        # print ("filter in ", len(lines ))
        final_list.extend( lines )
        
    print ("total find list , ", len( final_list ) )
    
    uniq_pid = set( [x["common_id"] for x in  final_list ] )
    print ("common id ", len(uniq_pid) )
    
    with open("./data/apps_nl2code_from_apps_buggy_fix_paired.jsonl" , "w") as fw :
        fw.write( "\n".join([json.dumps(x) for x in final_list]))
    
    
    
    
    