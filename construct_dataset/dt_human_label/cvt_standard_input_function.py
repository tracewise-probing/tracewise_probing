import json 
import os 
import re
import traceback 
from datasets import load_dataset 

import sys
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm 

import tiktoken

encoding = tiktoken.encoding_for_model("gpt-4o-mini")

# sys.set_int_max_str_digits(0) 
 
CACHED_DIR= "./data"

num_workers= os.cpu_count()-1 



def num_tokens_from_string(string: str ) -> int:
    """Returns the number of tokens in a text string."""
    num_tokens = len(encoding.encode(string))
    return num_tokens


def _filter_is_fn_name( row ):
    in_out  = row["input_output"]
    assert type(in_out) ==str 
    return "fn_name" not in in_out 



def filter_func( dt ,batch_size=1 ):
    
    # def _filter( one  , idx  ):
    #     if _filter_is_fn_name(one ) :
    #         return one 
    #     return None 
    #
    # dt = dt.filter( 
    #     _filter,
    #         batched=False ,
    #         batch_size=batch_size,
    #         with_indices=True,
    #         num_proc=num_workers,
    #         load_from_cache_file=False,
    #     )
    
    dt = dt.map(
        count_solution_size,
            batched=True ,
            batch_size=batch_size,
            with_indices=True,
            num_proc=num_workers,
            load_from_cache_file=False,
        )
    return dt 


def count_solution_size( batched, idx  ):
    batched_sol = batched["solutions"]
    batched["solutions_size"] = [0]* len(batched_sol)
    for ii  in  range( len(batched_sol) ):
        batched["solutions_size"][ii] = len( batched_sol[ii] )
        
    return batched 




import jinja2
environment = jinja2.Environment(loader=jinja2.FileSystemLoader("./") )

template = environment.get_template("cvt_standard_input_function.jinja")


def read_instruction( item ):
    return msg 

def get_apps_data_from_jsonl( split="train" ):
    CACHED_FILENAME =  os.path.join(CACHED_DIR, f"cvt_standard_input_function_{split}.jsonl") 

    dataset = load_dataset("codeparrot/apps", split=split )
    dataset  = filter_func( dt =dataset )
    item_list = []
    ut_list = []

    for one in tqdm(dataset ) :
        if "solutions" not in one:
            continue 
        pid = "cvt_standard_{}#problem_id:{}".format(split,  one["problem_id"]  )
        
        if DEMAND_LIST is not None and pid not in DEMAND_LIST:
            continue 
        
        if type( one["solutions"] ) != list :
            try :
                sol = json.loads( one["solutions"] )
            except :
                continue 
        else:
            sol =  one["solutions"] 
            
        _solution_list = sol[:20]
        #_solution_list = {"canonical_solution_list":  json.dumps(_solution_list) } 
        try :
            inx_outx =json.loads( one["input_output"])
        except :
            continue 




        for ii,_solution in enumerate(_solution_list):
            task_id = "cvt_standard_{}#problem_id:{}###order_id:{}".format(split,  one["problem_id"] , ii )
        
            item = {
                "task_id":task_id, 
                    "problem_id":one["problem_id"],
                    "pid":pid, 
                    # "input_outputs": json.dumps( json.loads( one["input_output"]) ), 
                    "input_output": json.dumps( inx_outx ), 
                    "code": _solution  ,
                    }
            item_list.append( item   )

    print ("total item.list ", len(item_list) )
    
    def process_file( i ):
        item = item_list[i]

        if i%1000 == 0 :
            print ( i , "/",len(item_list ) )

        if len(item["input_output"]) >100000:
            return None 
        
        tk_size = 1000000
        try :
            inx_outx =json.loads( item["input_output"])
            tk_size = num_tokens_from_string( item["input_output"] )
        except Exception as ex :
            traceback.print_exc() 
            return None  
            
        
        if tk_size >1000 :
            fn_name = inx_outx.get("fn_name",None)
            inputs = inx_outx["inputs"]
            outputs = inx_outx["outputs"]
            
            inputs = inputs[:10]
            outputs = outputs[:10]
            inx_outx = {"fn_name":fn_name, "inputs":inputs, "outputs":outputs }
            if fn_name is None :
                inx_outx.pop("fn_name")

        item ["input_output"]= json.dumps( inx_outx, indent=4 )
        
        try :
            prompt  = template.render( **item )
            tk_size = num_tokens_from_string( prompt )
            if tk_size> 10000:
                return None 
        except :
            return None 
        return {**item, "prompt": prompt , "tk_size":tk_size } 

    with ThreadPoolExecutor(max_workers=num_workers) as ex:
        predictions = ex.map(process_file, range(len(item_list)))
    predictions = list(predictions )
    print ("total msg.list ", len(predictions) )
    predictions = [x for x in predictions if x is not None ]
    print ("total msg.list.filter ", len(predictions) )
    
    with open(CACHED_FILENAME,"w" ) as fw:
        fw.write( "\n".join( [ json.dumps(x) for x in predictions ]))
    
    return item_list 



if __name__=="__main__":
    DEMAND_LIST = None
    if os.path.isfile("data/demand_apps_pid.jsonl"):
        with open("data/demand_apps_pid.jsonl") as fr :
            lines = [ x.strip() for x in fr.readlines()   ]
            DEMAND_LIST = set(lines )
        
    get_apps_data_from_jsonl()
    get_apps_data_from_jsonl("test")


