import os 
import json 

from evalplus.data import  get_human_eval_plus,get_human_eval_plus_hash,get_mbpp_plus_hash ,get_mbpp_plus

from evalplus.evaluate import  get_groundtruth
from evalplus.eval._special_oracle import MBPP_OUTPUT_NOT_NONE_TASKS


from .gen_unittest import assert_input_output





def get_gt (dataset,
        mini: bool = False,
        noextreme: bool = False,
        version: str = "default",
    ):
    
    if dataset == "humaneval":
        problems = get_human_eval_plus(
            mini=mini, noextreme=noextreme, version=version
        )
        dataset_hash = get_human_eval_plus_hash(
            mini=mini, noextreme=noextreme, version=version
        )
        expected_output = get_groundtruth(problems, dataset_hash, [])
    elif dataset == "mbpp":
        problems = get_mbpp_plus(mini=mini, noextreme=noextreme, version=version)
        dataset_hash = get_mbpp_plus_hash(
            mini=mini, noextreme=noextreme, version=version
        )
        expected_output = get_groundtruth(
            problems,
            dataset_hash,
            MBPP_OUTPUT_NOT_NONE_TASKS,
        )

    return expected_output 


humaneval_problems = get_human_eval_plus()
humaneval_gt  = get_gt("humaneval")

mbpp_problems = get_mbpp_plus()
mbpp_problems["Mbpp/88"]["canonical_solution"] = "from collections import Counter \n"+mbpp_problems["Mbpp/88"]["canonical_solution"]
mbpp_problems["Mbpp/137"]["canonical_solution"] = "from math import inf \n"+mbpp_problems["Mbpp/137"]["canonical_solution"]
mbpp_problems["Mbpp/300"]["canonical_solution"] = "from math import inf \n"+mbpp_problems["Mbpp/300"]["canonical_solution"]
mbpp_problems["Mbpp/404"]["canonical_solution"] = "from math import inf \n"+mbpp_problems["Mbpp/404"]["canonical_solution"]

mbpp_gt = get_gt("mbpp")




def build_testcase_with_base_plus ( task_id, is_base=True ):
    
    problem = humaneval_problems.get( task_id, None ) or  mbpp_problems.get( task_id, None )
    task_gt = humaneval_gt.get( task_id, None ) or  mbpp_gt.get( task_id, None )
    assert problem is not None , (task_id ,"not in dt ")
    assert task_gt is not None , (task_id ,"not in dt ")
    # print ( type(task), "task")
    # print ( list(task_gt) )
    # print ( list(problem) )
    
    if task_id.lower().startswith("human"):
        solution_gt = problem["prompt"] +"\n"+ problem["canonical_solution"]
    else:
        solution_gt =  problem["canonical_solution"]
        
    sample = {
        "input_output": {
            "inputs":problem["base_input" if is_base  else "plus_input"],
            "outputs":task_gt["base" if is_base else "plus"],
            },
        "task_id":task_id ,
        }
    
    assert_list_str = assert_input_output ( 
        sample, 
        first_solution=solution_gt,
        entry_point=problem["entry_point"] , 
        is_compare_on_str_level=False  )
    if assert_list_str is None :
        return None 
    assert_list = [one_assert["assert_gt"]  for one_assert in assert_list_str ] 
    
    item = {
        "task_id":task_id, 
        "assert_list": assert_list, 
        "solution_gt": solution_gt, 
        }
    return item 
    