import json 
import os 
import re
import traceback 
from datasets import load_dataset 

import sys

sys.set_int_max_str_digits(0) 
 
CACHED_DIR= "./data"

num_workers= 16

def _filter_is_fn_name( row ):
    in_out  = row["input_output"]
    assert type(in_out) ==str 
    return "fn_name" in in_out 


def _filter_testcase( row  , min_size= 3 ):
    return True 
    in_out  = row["input_output"]
    assert type(in_out) ==str 
    
    in_out = json.loads(in_out)
    outputs = in_out["outputs"]
    outputs_len = len(outputs)
    return outputs_len >= min_size 

def filter_func( dt ,batch_size=1 ):
    
    def _filter( one  , idx  ):
        if _filter_is_fn_name(one ) and _filter_testcase(one)  :
            return one 
        return None 
        # for one in 
        # return [one  for one in batched["input_output"]  ]

    dt = dt.filter( 
        _filter,
            batched=False ,
            batch_size=batch_size,
            with_indices=True,
            num_proc=num_workers,
            load_from_cache_file=False,
        )
    
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
CACHED_FILENAME =  os.path.join(CACHED_DIR, "apps_withtest_full_solutions_v2.jsonl") 
def get_apps_data_from_jsonl(cached_filename = CACHED_FILENAME ):
    def short_inx_outx ( inx_outx ,max_len=20):
        fn_name = inx_outx.get("fn_name",None )
        inx = inx_outx.pop("inputs")
        inx = inx[:max_len]
        outx  = inx_outx.pop("outputs")
        outx =  outx[:max_len]
        return {"fn_name":fn_name, "inputs":inx, "outputs":outx } 

    if not os.path.isfile( cached_filename ):
        dataset = load_dataset("codeparrot/apps", split="train")
        dataset  = filter_func( dt =dataset )
        item_list = []
        ut_list = []

        for one in dataset :
            sol = json.loads( one["solutions"] )
            first_solution = sol[-1]
            _solution_list = sol[:20]
            #_solution_list = {"canonical_solution_list":  json.dumps(_solution_list) } 
            inx_outx =json.loads( one["input_output"])
            inx_outx_shorted = short_inx_outx( inx_outx )
            
            starter_code  = one["starter_code"]
            entry_point = get_entry_point( starter_code )
            if entry_point is None :
                entry_point = inx_outx["fn_name"]
                entry_point = get_entry_point( x_start_coder=entry_point )
            if entry_point is None :
                entry_point = get_function_name( source_code =first_solution  )

            assert entry_point is not None , ( one )

            sub_solutions = {}
            ut_list.append( {"sample":one , "first_solution":first_solution , "entry_point":entry_point, "canonical_solution_list":  json.dumps(_solution_list)   })
            # for ii ,one__solution  in enumerate(_solution_list) :
                # try :
                #     info = get_unittest. assert_input_output ( sample=one  ,first_solution=one__solution ,entry_point=entry_point ,is_compare_on_str_level=False  )
                #
                #     #info_json_dumps = get_unittest. assert_input_output ( sample=one , first_solution=first_solution ,entry_point =entry_point,is_compare_on_str_level=True  )
                #     sub_solutions.update( {"canonical_solution_{}".format(ii):one__solution, "test_list_{}".format(ii):info  } )
                # except :
                #     traceback.print_exc()
                #     continue 

            item = {
                    "problem_id":one["problem_id"], 
                    "input_outputs": json.dumps(  inx_outx_shorted ),
                    "entry_point":entry_point,
                    "canonical_solution": first_solution  ,
                    **sub_solutions, 
                    "test_list": sub_solutions.get("test_list_0",None ), 
                    #"test_jlist": info_json_dumps 
                    }
            item_list.append( item )
        with open( cached_filename ,"w") as fw:
            fw.write("\n".join([json.dumps(x) for x in item_list ]))
        with open( cached_filename.replace(".jsonl","-testcases.jsonl") ,"w") as fw:
            fw.write("\n".join([json.dumps(x) for x in  ut_list  ]))
    with open(cached_filename ) as fr:
        lines = [ json.loads(x) for x in fr.readlines() ]
    return lines 





def get_function_name( source_code ):
    member_function_names = re.findall(r'class\s+solution\s*:\s+def\s+(\w+)\s*\(', source_code,  re.MULTILINE|re.IGNORECASE|re.DOTALL  )
    if len(member_function_names)>0:
        return member_function_names 
    
    function_names = re.findall(r'def\s+(\w+)\s*\(', source_code,  re.MULTILINE|re.IGNORECASE|re.DOTALL  )
    pattern = r"def\s+(\w+)\s*\(.*?\):"
    matches = re.findall(pattern, source_code, re.MULTILINE|re.IGNORECASE|re.DOTALL )
    funcs = matches+function_names 
    funcs = funcs[0] if type(funcs)==list and len(funcs)>0 else None 
    return funcs 



    
entry_pattern = r"def (\w+)\s?\("
def get_entry_point( x_start_coder):
    if x_start_coder is None or type(x_start_coder)!=str:
        return None 
    funcs = re.findall(entry_pattern, x_start_coder )
    funcs = funcs[0] if type(funcs)==list and len(funcs)>0 else None 

    return funcs 



if __name__=="__main__":
    
    get_apps_data_from_jsonl()