import json 
import openai 
import sys 


import multiprocessing
import os
import pickle
import threading
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from warnings import warn

import numpy as np
from termcolor import cprint
from tqdm import tqdm

from evalplus.codegen import run_codegen
from evalplus.config import *
from evalplus.data import (
    get_human_eval_plus,
    get_human_eval_plus_hash,
    get_mbpp_plus,
    get_mbpp_plus_hash,
    load_solutions,
)
from evalplus.data.mbpp import mbpp_serialize_inputs
from evalplus.data.utils import CACHE_DIR
from evalplus.evaluate import check_correctness 

from evalplus.eval import (
    PASS,
    compatible_eval_result,
    estimate_pass_at_k,
    untrusted_check,
)
from evalplus.eval._special_oracle import MBPP_OUTPUT_NOT_NONE_TASKS
from evalplus.gen.util import trusted_exec

from evalplus.evaluate import get_groundtruth 


cur_dir = os.path.dirname( os.path.abspath(__file__) )
sys.path.append( os.path.join(cur_dir, "./construct_dataset") )
import dt_human_label.utils.tpl_trace_formater as tpl_trace 


parallel= None 
n_workers = parallel or max(1, multiprocessing.cpu_count() // 2)

# 1st item: the status
# 2nd item (optional): the detailed pass/fail boolean for each input
Result = Tuple[str, List[bool]]




def partial_evaluate(dataset,
                samples={},
                base_only=False,
    test_details: bool = False,
    min_time_limit: float = DEFAULT_MIN_TIME_LIMIT,
    gt_time_limit_factor: float = DEFAULT_GT_TIME_LIMIT_FACTOR,
          ):

    if dataset == "humaneval":
        problems = get_human_eval_plus(
            mini=False, noextreme=False, version="default"
        )
        dataset_hash = get_human_eval_plus_hash(
            mini=False, noextreme=False, version="default"
        )
        expected_output = get_groundtruth(problems, dataset_hash, [])
    elif dataset == "mbpp":
        problems = get_mbpp_plus(mini=False, noextreme=False, version="default")
        dataset_hash = get_mbpp_plus_hash(
            mini=False, noextreme=False, version="default"
        )
        expected_output = get_groundtruth(
            problems,
            dataset_hash,
            MBPP_OUTPUT_NOT_NONE_TASKS,
        )

    results = []
    # {
    #     # "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    #     # "hash": dataset_hash,
    #     # "eval": {},
    # }
    # # problems = {k:v for k,v in problems.items() if k in samples }
    # print ("problems", len(problems) )
    
    assert len(problems) , (list(problems), list(samples) )

    with ProcessPoolExecutor(max_workers=n_workers) as executor:
        futures = []
        completion_id = Counter()
        n_samples = 0
        eval_results = defaultdict(list)  # task_id ->
        remainings = set()

        print("Reading samples...")
        for sample in tqdm( samples ):
            task_id = sample["task_id"]
            if task_id not in problems:
                warn(
                    f"Task {task_id} is found in the samples but not found in the dataset"
                )
                continue
            solution = (
                sample["solution"]
                if "solution" in sample
                else problems[task_id]["prompt"] + sample["completion"]
            )
            remainings.add(sample["_identifier"])
            args = (
                dataset,
                completion_id[task_id],
                problems[task_id],
                solution,
                expected_output[task_id],
                base_only,
                not test_details,  # fast_check
                sample["_identifier"],
                min_time_limit,
                gt_time_limit_factor,
            )
            futures.append(executor.submit(check_correctness_with_trace, *args))
            completion_id[task_id] += 1
            n_samples += 1

        assert n_samples == len(remainings), "Missing problems in unfinished"
        # assert len(completion_id) == len(problems), "Missing problems in samples"

        def stucking_checker():
            while remainings:
                last_size = len(remainings)
                time.sleep(20)
                if last_size != len(remainings) or len(remainings) == 0:
                    continue
                # Potential stucking
                warn("No samples had finished testing in the last 20s")
                warn(f"{len(remainings)} samples to be tested: {remainings}")

        threading.Thread(target=stucking_checker).start()

        for future in tqdm(as_completed(futures), total=n_samples):
            result_raw = future.result()
            print ( type(result_raw) )
            result , trace_status = result_raw 
            print ("trace_status" , trace_status,  "result", list(result))
            remainings.remove(result["_identifier"])
            eval_results[result["task_id"]].append(result)

        for task_id,task_results in eval_results.items():
            task_results.sort(key=lambda x: x["completion_id"])
            # results ["eval"][task_id] = []
            
            for res in task_results:
                print ( list(res), "list.res" )
                base_stat, base_details = res["base"]
                plus_stat, plus_details = res["plus"]
                #["eval"][task_id] .append(
                results.append(  {
                    "task_id":task_id , 
                    "_identifier":res["_identifier"],
                    "base_pass":base_stat=="pass",
                    "base_error_index":len(base_details)-1,
                    "base_trace":res["base_trace"],
                    "plus_pass":plus_stat=="pass",
                    "plus_error_index":len(plus_details)-1,
                    # "plus_trace":res.get("plus_trace",None),
                    } )
            
            

    return results 



import random 
import traceback 

def rebuild_testcase( testcase_str , verify_list ):
    is_json = False 
    if type( testcase_str )== str :
        is_json = True 
        testcase_str = json.loads(testcase_str)
        
    fn_name = testcase_str["fn_name"]
    inputs  = testcase_str["inputs"]
    outputs = testcase_str["outputs"]
    
    inputs_new = []
    outputs_new = []
    zip_list = list( zip(inputs,outputs,verify_list) )
    random.shuffle( zip_list )
    
    for i,(x,y,z) in enumerate( zip_list ) :
        if z==False :
            inputs_new.append( x )
            outputs_new.append( y )
            break 
    
    assert len(inputs_new)==1 ,  (testcase_str,verify_list)
    assert len(outputs_new)==1 ,  (testcase_str,verify_list)
    # assert len(inputs)== len(verify_list), (testcase_str,verify_list, len(verify_list), "-->", len(inputs), "!--->", len(outputs) )
    # assert len(outputs)== len(verify_list), (testcase_str,verify_list, len(verify_list), "-->", len(inputs), "!--->", len(outputs) ) 
    
    assert len(inputs_new), (testcase_str,verify_list, len(verify_list), "-->", len(inputs), "!--->", len(outputs) )
    assert len(outputs_new), (testcase_str,verify_list, len(verify_list), "-->", len(inputs), "!--->", len(outputs) )
    
    new_inx_out = {"fn_name":fn_name , "inputs":inputs_new , "outputs":outputs_new }
    if is_json :
        return  json.dumps(new_inx_out )
    return new_inx_out 



#for one_item in tqdm( lines ) :
def check_correctness_with_trace( 
            dataset: str,
            completion_id: int,
            problem: Dict[str, Any],
            solution: str,
            expected_output: Dict[str, List],
            base_only=False,
            fast_check=False,
            identifier=None,
            min_time_limit: float = DEFAULT_MIN_TIME_LIMIT,
            gt_time_limit_factor: float = DEFAULT_GT_TIME_LIMIT_FACTOR,
         ):
    
    ret = check_correctness(
        dataset=dataset,
        completion_id= completion_id,
        problem= problem,
        solution= solution,
        expected_output= expected_output,
        base_only= base_only,
        fast_check= fast_check,
        identifier=identifier,
        min_time_limit=min_time_limit,
        gt_time_limit_factor=gt_time_limit_factor,
        )
    
    verify , verify_list = ret["base"]
    ret["base_trace"] = {"bug_notrace": "## Trace \n**BUGGY_PROGRAM**\n```python\n{}\n```".format( solution ) } 
    one_item ={}
    one_item["base_tests"]= {"fn_name":problem["entry_point"],"inputs":problem["base_input"],"outputs":expected_output["base"] }
    one_item["verify_list"] = verify_list 
    
    ## in case all -1 
    if np.all( np.asarray(verify_list)==1 ):
        return ret, -1 ### all test cases are correct 

    if np.all( np.asarray(verify_list)==-1 ):
        one_item["verify_msg"] = "syntax error in the code "
        return ret,  -2 #"syntax error in the code "
    elif np.all( np.asarray(verify_list)==-2 ):
        one_item["verify_msg"] = "compile error in the code "
        return ret , -3 
    elif np.all( np.asarray(verify_list)!=0 ):
        one_item["verify_msg"] = "testcase is pass or timeout, none of fail"
        return ret , -4
    elif all(isinstance(x, bool) for x in verify_list):
        one_item["verify_msg"] = "there are failed test cases in the code "

    assert type( solution  ) == str , one_item 
    if solution  is None or len( solution .strip() )<=0 :
        return ret ,-5

    testcase_str = rebuild_testcase(testcase_str= one_item["base_tests"], verify_list=one_item["verify_list"] )
    verify_list = [0]

    sample  = {"input_output":testcase_str , "solution":solution, "_identifier":identifier }
    assert type(sample) == dict , sample 
    
    try :
        trace_item =tpl_trace.extrace_trace_accmulate (code_str=sample["solution"], sample = sample , err_index_list=verify_list )
        # print (trace_item,"--trace_item")
    except KeyboardInterrupt :
        raise 
    except Exception as ex :
        traceback.print_exc()
        return ret ,-6

    if trace_item is None :
        return ret  ,-7
    ret ["base_trace"] = {**ret ["base_trace"],**trace_item} 
    return ret ,1 



