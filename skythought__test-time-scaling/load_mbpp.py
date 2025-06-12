# from datasets import load_dataset
import json
import os 
import random
from tqdm import tqdm 
# import dspy
from evalplus.evaluate import (
    get_groundtruth,
)
from evalplus.eval._special_oracle import MBPP_OUTPUT_NOT_NONE_TASKS

from evalplus.data import (
    get_mbpp_plus,
    get_mbpp_plus_hash,
    load_solutions,
)

from datetime import datetime

VALID_TASK_ID_CACHE_PATH= os.path.expanduser("~/.cache/evalplus/sky_valid_task_ids.txt")

def get_accuracy(dataset, num_process_evaluate, method="selfdebug", timeout=6, valid_task_id_list= []):
    """Take in a dataset or subset of dataset, evaluate accuracy using multiprocessing"""
    total_passed = 0
    lock = None

    with tqdm(total=len(dataset), desc="Progress") as pbar:
        with ProcessPoolExecutor(max_workers=num_process_evaluate) as executor:
            futures = {
                executor.submit(
                    generate_and_evaluate,
                    (example, timeout, None, None, None)
                ): i for i, example in enumerate(dataset)
            }

            results = {}
            for future in as_completed(futures):
                idx = futures[future]
                result = future.result()
                results[idx] = result
                total_passed += int(result["passed"]) if type(result["passed"])!=list else int(all(result["passed"]))
                curr_acc = (total_passed / len(results)) * 100
                pbar.set_postfix({
                    'Accuracy': f'{curr_acc:.2f}%',
                    'Passed': f'{total_passed}/{len(results)}'
                })
                pbar.update(1)
                
                if result["passed"] and "task_id" in result :
                    valid_task_id_list.append( result["task_id"] )
                
    assert total_passed == len( valid_task_id_list ) , (valid_task_id_list, total_passed )    
    assert len(results) == len(dataset), f"results = {len(results)} inputs = {len(dataset)}"
    return total_passed / len(dataset)

# from tqdm import tqdm
#
# def get_accuracy(dataset, num_process_evaluate, method="selfdebug", timeout=6):
#     """
#     Take in a dataset or subset of dataset,
#     evaluate accuracy sequentially (no multiprocessing).
#     """
#     total_passed = 0
#     results_count = 0
#
#     with tqdm(total=len(dataset), desc="Progress") as pbar:
#         for example in dataset:
#             # Generate and evaluate for this example
#             result = generate_and_evaluate(
#                 (example,
#                 timeout,
#                 None,
#                 None , 
#                 None)
#             )
#
#             # Accumulate results
#             passed = int(result["passed"])
#             total_passed += passed
#             results_count += 1
#
#             # Compute running accuracy
#             current_accuracy = (total_passed / results_count) * 100
#
#             # Update progress bar
#             pbar.set_postfix({
#                 'Accuracy': f'{current_accuracy:.2f}%',
#                 'Passed':   f'{total_passed}/{results_count}'
#             })
#             pbar.update(1)
#
#     # Sanity check
#     assert results_count == len(dataset), (
#         f"results = {results_count} inputs = {len(dataset)}"
#     )
#
#     # Final accuracy as a fraction
#     final_accuracy = total_passed / len(dataset)
#     return final_accuracy

def generate_and_evaluate(arguments):
    example, timeout, method, result_json_path, lock = arguments
    is_stdin = False 
    task_id = example["task_id"]

    assert not is_stdin

    is_extracted = not is_stdin


    example["test"]=  example["private_test_cases"]
    private_c ={"raw_private": len(example["test"]) }
    private_test_cases = []
    
    res = check_correctness(
        example, 
        example["canonical_solution"] , 
        timeout=timeout, 
        is_extracted=is_extracted, 
        fast_check=False)

    res_pass_list = res["details"]
    for idx, (is_pass, test_item) in enumerate( zip(res_pass_list, example["test"]) ):
        if is_pass:
            private_test_cases.append(test_item )
    # assert len(private_test_cases), (task_id, "task_id")
    private_c .update({
        "new_private": len(private_test_cases), 
        "diff_private": len(example["test"])-len(private_test_cases) 
        })
        
        
    example["test"]=  example["public_test_cases"]
    public_c ={"raw_public": len(example["test"]) }
    public_test_cases = []
    
    res = check_correctness(
        example, 
        example["canonical_solution"] , 
        timeout=timeout, 
        is_extracted=is_extracted, 
        fast_check=False)

    res_pass_list = res["details"]
    for idx, (is_pass, test_item) in enumerate( zip(res_pass_list, example["test"]) ):
        if is_pass:
            public_test_cases.append(test_item )
    # assert len(public_test_cases), (task_id, "task_id")
    public_c .update({
        "new_public": len(private_test_cases), 
        "diff_public": len(example["test"])-len(public_test_cases) 
        })
        
        

        
    
    result_json = {
        'task_id': task_id,
        "passed": public_c["diff_public"]+private_c["diff_private"] == 0,
        # len(public_test_cases)>0 and len(private_test_cases)>0 , 
        **public_c,
        **private_c,
    }
    # if not result_json["passed"]:
    # print (result_json)
        
    return result_json




def get_mbpp_dataset_in_lcb():
    # 2. Generate MBPP plus problems, hash, and ground‐truth outputs
    problems = get_mbpp_plus(
        mini=False , 
        noextreme=False, 
        version="default",
    )
    expected_output = get_groundtruth(
        problems,
        get_mbpp_plus_hash(
        mini=False,
        noextreme=False,
        version="default"
        ),
        MBPP_OUTPUT_NOT_NONE_TASKS,
    )
    
    print ("problems", type(problems) )
    print ("expected_output", type(expected_output) )
    
    # 3. Filter to only tasks present in our +plus hash
    filtered_mbpp = {task_id:ex for task_id, ex in problems.items() if task_id in expected_output}
    print(f"After filtering mini/noextreme: {len(filtered_mbpp)} examples")
    
    # 4. Extract public vs. private tests
    public_test_cases = {}
    private_test_cases = {}
    
    valid_task_ids = None 
    if os.path.isfile(VALID_TASK_ID_CACHE_PATH):
        valid_task_ids = set( [x.strip() for x in open(VALID_TASK_ID_CACHE_PATH).readlines()] )
        
    
    filtered_mbpp_list= [] 
    
    for qid,ex  in tqdm( filtered_mbpp.items() ):
        if valid_task_ids and not qid in valid_task_ids:
            continue 
        # qid = ex["task_id"]
        # base → public
        # print (ex)
        base_input = ex["base_input"]
        plus_input = ex["plus_input"]
        ex_gt = expected_output[qid]
        
        base_output = ex_gt["base"]
        plus_output = ex_gt["plus"]
        # print (ex_gt)
        
        if len(plus_input)<=0 or len(plus_output)<=0 :
            continue 
        
        public_test_cases=[]
        for inx,out in zip(base_input,base_output):
            public_test_cases += [{
                "input": inx,
                "output": out,
                "testtype": "functional" if "entry_point" in ex else "stdin",
                "force_not_extracted": True ,
            }]
        # plus → private
        private_test_cases=[]
        for inx,out in zip(plus_input,plus_output):
            private_test_cases += [{
                "input": inx,
                "output": out,
                "testtype": "functional" if "entry_point" in ex else "stdin",
                "force_not_extracted": True ,
            }]
    
        # print ( ex["entry_point"] )
        row = {
            "question_content":ex["prompt"],
            "private_test_cases":private_test_cases , 
            "starter_code": ex["entry_point"],
            "canonical_solution":ex["canonical_solution"],
            "task_id": ex["task_id"],
            "question_id": ex["task_id"],
            "is_stdin": False, 
            "public_test_cases":public_test_cases , 
            }
        filtered_mbpp_list.append(row )
        

    print(f"Constructed live_code_bench_mbpp with {len(filtered_mbpp_list)} examples.")

    return filtered_mbpp_list


# def get_mbpp_dataset_in_lcb_all_buggycode():
#     dt = get_mbpp_dataset_in_lcb()
#     with open("./annex_dataset/mbpp_repair_generations.jsonl") as fr :
#         lines= [json.loads(x) for x in fr.readlines() ]
#         mbpp_all_buggycode = {x["task_id"]:x  for x in lines }
#     new_dt = []
#     for item in dt :
#         assert  item["task_id"] in mbpp_all_buggycode 
#         buggy_prompt = mbpp_all_buggycode[ item["task_id"]]["prompt"]
#         buggy_prompt = buggy_prompt.replace("Do not include any explanation.","").replace("your correct program is \n```python\n","")
#
#         item["question_content"] = "You are tasked to repair the following buggy code: {}\n {} {}\n".format(
#             "```" if "```" not in buggy_prompt else "",
#             buggy_prompt , 
#             "```" if "```" not in buggy_prompt else "",
#             )
#
#         new_dt.append( item )
#     return new_dt 


def get_mbpp_dataset_in_lcb_all_buggycode():
    dt = get_mbpp_dataset_in_lcb()
    with open("./annex_dataset/mbpp_repair_generations.jsonl") as fr :
        lines= [json.loads(x) for x in fr.readlines() ]
        mbpp_all_buggycode = {x["task_id"]:x  for x in lines }
    new_dt = []
    for item in dt :
        assert  item["task_id"] in mbpp_all_buggycode 
        buggy_prompt = mbpp_all_buggycode[ item["task_id"]]["prompt"]
        buggy_prompt = buggy_prompt.replace("Do not include any explanation.","")
        assert "explanation" not in buggy_prompt.lower(), buggy_prompt
        item["question_content"] =buggy_prompt
        
        new_dt.append( item )
    return new_dt 


if __name__=="__main__":
    import dspy 
    from live_code_bench_execute import check_correctness, check_correctness_oracle
    from tqdm import tqdm 
    from concurrent.futures import ProcessPoolExecutor, as_completed

    # if not os.path.isfile(VALID_TASK_ID_CACHE_PATH):
    if 1==1 :
        filtered_lcb = get_mbpp_dataset_in_lcb()
    
        valid_task_id_list = []
        
        acc_meta =  get_accuracy(dataset=filtered_lcb, num_process_evaluate=16, method=None, timeout=6, valid_task_id_list= valid_task_id_list)
        
        with open(VALID_TASK_ID_CACHE_PATH,"w") as fw :
            fw.write("\n".join(valid_task_id_list) )
        
        
