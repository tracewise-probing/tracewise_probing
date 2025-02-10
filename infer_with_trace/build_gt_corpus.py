import os 
from utils import verify_call 
from utils import oai_evaluation 
import json 
from tqdm import tqdm 

from glob2 import glob 

if __name__=="__main__":
    save_dir = "./data"
    
    item_list = []
    problem_list = {}
    
    mbpp_list=[json.loads(x) for x in  open("/mnt/local/cache_dir/evalplus/MbppPlus-v0.2.0.jsonl").readlines() ] 
    mbpp_list = [x["task_id"] for x in mbpp_list ]

    # mbpp_list=[json.loads(x) for x in  open("/mnt/local/cache_dir/evalplus/HumanEvalPlus-v0.1.10.jsonl").readlines() ] 
    # mbpp_list = [x["task_id"] for x in mbpp_list ]

    for task_id in tqdm( mbpp_list ) :
        # task_id = f"Mbpp/{i}"
        
        item = verify_call.build_testcase_with_base_plus( task_id = task_id ,is_base=False)
        
        assert item is not None or (item is None and task_id == "Mbpp/793" )
        if item is None :
            continue 
        with open(os.path.join(save_dir, task_id.replace("/","--")+".py") ,"w") as fw:
            fw.write( item["solution_gt"] ) 
            fw.write("\n" )
            fw.write( "\n".join ( item["assert_list"]) ) 

    # task_list = glob("./data/HumanEval*.py")
    # for one_task in task_list:
        
        item_list.append(  {
            "task_id": task_id, #os.path.basename(one_task),
            "completion": item["solution_gt"], 
            #open(one_task).read(),
        } )
        problem_list[task_id] = {
            "task_id": task_id, #os.path.basename(one_task),
            "test":  "\n".join ( item["assert_list"]), 
            }
            
        
    pass_info = oai_evaluation.evaluate_functional_correctness(
            samples= item_list , 
            problems= problem_list, 
            timeout=20,
            )
    pass_info = list(pass_info.values() )
    pass_info = [x[-1][-1] for x in pass_info ]
    
    pass_info_passed= [x  for x in pass_info if x["passed"] ]
    print ( len(pass_info_passed),"/",len(pass_info) )
    with open("./data/t.jsonl","w") as fw:
        fw.write( "\n".join([json.dumps(x) for x in pass_info]))