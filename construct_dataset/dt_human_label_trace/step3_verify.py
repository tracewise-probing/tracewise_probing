import os 
from glob import glob 
import sys 
import json 
# import apps_metric.evl as xeval 

sys.path.append( "../dt_human_label")
from utils.utils import verify_unittest

from concurrent.futures import ThreadPoolExecutor
num_workers = os.cpu_count()-1

import hashlib 

md5_func = lambda x: hashlib.md5( x.encode("utf-8") ) .hexdigest() 

from redis.cluster import RedisCluster as Redis
from redis.cluster import ClusterNode
nodes = [
    ClusterNode('10.96.183.88', 6379), 
    ClusterNode('10.96.182.154', 6378),
    ClusterNode('10.96.187.173', 6378),
    ClusterNode('10.96.178.26', 6378),
    ]
redishandle = Redis(startup_nodes=nodes)



def get_cache( solution  , sample  ):

    md5_meta = {"solution":solution, **sample }
    md5_v = md5_func( json.dumps(md5_meta) )
    
    cache_v = redishandle.get( md5_v   )
    
    if cache_v is None :
        res_flag, res, err_list  =  verify_unittest( solution=solution , sample=sample ) 
        cache_v= json.dumps( {"res_flag":res_flag, "res":res, "err_list": err_list } )
        redishandle.set( md5_v, cache_v )

    v = json.loads( cache_v )
    return v["res_flag"], v["res"], v["err_list"]


def load_testcase_nl2code( load_p = "../dt_human_label/data/apps_nl2code_from_apps_cross_verify.jsonl" ):        
    lines = [json.loads(x) for x in open(load_p).readlines() ]
    lines = [x for x in lines if  "cvt_standard_" in x["problem_id"] ]
    lines = {x["task_id"].split("cvt_standard_")[-1] : x["tests"] for x in lines }
    
    return lines 

if __name__=="__main__":

    json_p = sys.argv[-1]
    assert "-extracted" in json_p , json_p 


    new_save_p = json_p.replace("-extracted.jsonl", "-extracted-verified.jsonl")
    assert new_save_p!= json_p , (json_p, new_save_p )
    #assert "sanitized-verified" not in json_p , json_p 
    #assert not os.path.isfile( new_save_p ), new_save_p 

    print ("starting read")
    with open( json_p ) as fr :
        lines=  fr.readlines() 
        lines = [json.loads(x) for x in lines ]

    print ("reading done, ", len(lines) )        

    def parse_problem_id (task_id):
        #  "task_id": "train_v1#problem_id:3203###cdb541a041fcff5357f8690262e5df14",
        task_id = task_id.split("###")[0]
        assert "problem_id:" in  task_id , task_id 
        problem_id = task_id.split("problem_id:")[-1]
        problem_id = int(problem_id)
        assert 0<= problem_id and problem_id<= 5000 , (task_id,problem_id) 
        return problem_id 

    lines = [{**x, "problem_id":parse_problem_id(task_id=x["task_id"] ) } for x in lines ]
    print ("find problem_id", len(lines) )

    global_nl2code_testcase = load_testcase_nl2code()

    def process_file( i ):
        item = lines[i]
        if i%500 == 0 :
            print (i )
        # print ( list(item), "...item")
        solution = item ["extracted_code"]
        task_id_parent = item ["task_id"]
        assert task_id_parent.count("###") ==2 , (task_id_parent, )
        task_id_parent=task_id_parent.split("cvt_standard_")[-1]
        if "tests" not in item :
            item["tests"] = global_nl2code_testcase[ task_id_parent ]
            
        try :
            testcase_str = json.loads(item["tests"])
            if type(testcase_str)!= dict :
                return None 
            assert "fn_name" in testcase_str 
            assert "inputs" in testcase_str 
            assert "outputs" in testcase_str 
        except :
            return None 
        sample = {"input_output":  item["tests"] }
        ### 
        
        # res_flag, res, err_list  =  verify_unittest( solution=solution , sample=sample ) 
        res_flag, res, err_list  = get_cache( solution=solution  , sample=sample  )
        return {**item , "verify":res_flag,"verify_list":res , "err_list":err_list } 

    with ThreadPoolExecutor(max_workers=num_workers//8) as ex:
        predictions = ex.map(process_file, range(len(lines)))
    predictions =  list(predictions)
         
    predictions =  [x for x in predictions if x is not None ]
    print ("#######\n"*8)
    print ("verify done ")
    with open( new_save_p , "w") as fw :
        fw.write( "\n".join([ json.dumps(x) for x in predictions ]))
