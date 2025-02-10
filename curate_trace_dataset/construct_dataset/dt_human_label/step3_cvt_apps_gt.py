import json 
import os 
from glob2 import glob 

from collections import defaultdict
import numpy as np 

from tqdm import tqdm 

def read_jsonl ( jsonp ):
    
    with open( jsonp ) as fr :
        lines = [json.loads(x) for x in fr.readlines() ]
    return lines 

def get_pid( uuid ):
    pid = uuid.split("problem_id:")[-1]
    pid = pid.split("###")[0]
    return pid 

from utils.utils  import check_correctness 
TIMEOUT = 30

def evaluate_correctness(function_imp, testcase_str,     err_list = [] ,**kwargs ):
    assert "fn_name" in str(testcase_str) , testcase_str 

    sample = {
        "input_output":json.dumps( testcase_str ) if type(testcase_str)!=str else testcase_str ,
        }
    

    debug = False  
    curr_res = [-2]
    try:
        curr_res = check_correctness(sample, function_imp, timeout=TIMEOUT, debug=debug ,err_list=err_list)
        if debug:
            print(f"\nSuccessful compilation of task {index}!")
        fixed = []
        for e in curr_res:
            if isinstance(e, np.ndarray):
               e = e.item(0)
            if isinstance(e, np.bool_):
                e = bool(e)
            fixed.append(e)
        curr_res = fixed
        if not np.all(curr_res):
            if debug:
                print(f"Results were not True for all test cases")
    except Exception as e:
        if debug:
            print(f"Compilation failed, test framework exception = {repr(e)}{e}\n")
        return None 
    finally:
        assert isinstance(curr_res, list)

    if len(curr_res)>0 and all(curr_res)==True :
        return curr_res 
    
    return curr_res
    
    

def valide_cross_testcase ( v_list ):
    
    test_list = []
    
    for i in range( len( v_list ) ):
        elem = v_list[i] 
        uuid = elem["uuid"]
        testcase_str = elem["testcase_str"]
        testcase_str = json.loads(testcase_str)
        tgt_input  = testcase_str["inputs"]
        tgt_output = testcase_str["outputs"]
        
        for cross_elem  in v_list :

            uuid_cross = cross_elem["uuid"]
            if uuid_cross == uuid :
                continue 
            
            testcase_str_cross = cross_elem["testcase_str"]
            # testcase_str_cross = elem["testcase_str"]
            testcase_str_cross = json.loads(testcase_str_cross)
            
            new_test_str = {"fn_name":testcase_str_cross["fn_name"],"inputs":tgt_input, "outputs":tgt_output }
            item = {"function_imp":cross_elem["function"], "testcase_str": new_test_str ,  "uuid_cross": "{}---{}".format(uuid,uuid_cross) }
            test_list.append( item )
    
    # print ("total test_list" , len(test_list) )
    test_list_ret = []
    for one_test in test_list :
        ret = evaluate_correctness( **one_test  )
        test_list_ret.append( ret)


    test_list_ret_overall = [len(x)>0 and all([xx==True  for xx in x ])  for x in test_list_ret ] 
    test_list_ret_zip = list( zip([x["uuid_cross"] for x in test_list],  test_list_ret_overall) )
    test_list_ret_overall_score = float( np.mean(test_list_ret_overall) ) 
    # print ( "overall", np.mean(test_list_ret_overall), "--->", test_list_ret_overall[:5] )
    # print ("==="*8 )
    # print ( test_list_ret )
    return {"cross_uuid_list":test_list_ret_zip  ,"score":test_list_ret_overall_score }

from concurrent.futures import ProcessPoolExecutor as  ThreadPoolExecutor
num_workers = min(32, os.cpu_count()-1 )
    
if __name__ == "__main__":
    problem_collections = defaultdict(list )

    read_dir = "/home/xxxxxxx/wj_code/dl_execute/reverse_train_data_collecting/data/valid_data_apps_cvt_standardinput"
    read_f = glob( os.path.join( read_dir , "new_cvt_standard_input_function_t*fingerprinted000.jsonl") )
    
    lines = []
    for one_f in read_f :
        x_lines = read_jsonl( one_f )
        is_test="standard_input_function_test" in  os.path.basename(one_f )
        x_lines = [{**x, "x_uuid":x["uuid"].replace("cvt_standard#problem_id","cvt_standard_test#problem_id" if is_test else "cvt_standard_train#problem_id") } for x in x_lines ]
        lines += x_lines
        
    
    mapping_list  = [x["x_uuid"].split("###")[0] for x in lines ]
    mapping_list = {x["uuid"]:x  for x in lines }
    
    print ("ttoal read", len(mapping_list) )
    
    
    jsonp  = "data/step2_cvt_apps_valid.jsonl"
    lines = read_jsonl( jsonp )
    
    ## 
    corrected_lines = [x for x in lines  if x["flg"] is not None and len(x["flg"])>0 and  all([yy==True for yy in x["flg"] ] )  ]
    corrected_lines = [ {**x,"x_uuid":mapping_list[x["uuid"] ]["x_uuid"]  } for x in corrected_lines ]
    print ("correct : ", len(corrected_lines) , "/ ", len( lines ) )
    # incorrected_lines = [x for x in lines  if x["flg"] is not None and len(x["flg"])>0 and  all(x["flg"])!=True  ]
    # print ("in correct : ", len(incorrected_lines) , "/ ", len( lines ) )
    # 
    
    grp_list_test = [x for x in corrected_lines  if x["x_uuid"].startswith("cvt_standard_test") ]
    grp_list_train = [x for x in corrected_lines  if x["x_uuid"].startswith("cvt_standard_train") ]

    #
    # for x in grp_list_test :
    #     pid = x["x_uuid"].split("###")[0]
    #     problem_collections[pid].append( x )
        
    for x in grp_list_train :
        pid = x["x_uuid"].split("###")[0]
        problem_collections[pid].append( x )
        
    
    # for pid , v_list in tqdm( problem_collections.items() ) :
    #
    #     # print ("pid:", pid , "----", len(v_list ) )
    #     one_score = valide_cross_testcase ( v_list )
    #     one_score = json.dumps(one_score)+"\n"
    #     with open("./data/step3_cross_valid.jsonl","a") as fw :
    #         fw.write( one_score )
    problem_collections_keys= list( problem_collections )
    def process_file(i):
        if i%10==0:
            print (i,"/",len(problem_collections_keys) )
        one_key = problem_collections_keys[i]
        v_list = problem_collections[ one_key ]
        one_score = valide_cross_testcase ( v_list )
        one_score.update({"pid":one_key})
        one_score = json.dumps(one_score)+"\n"
        with open("./data/step3_cross_valid.jsonl","a") as fw :
            fw.write( one_score )
        return None

    with ThreadPoolExecutor(max_workers=num_workers) as ex:
        predictions = ex.map(process_file, range(len(problem_collections_keys)))
    predictions =  list(predictions)
            
        
    