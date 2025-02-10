import json 
import os 

from datasets import load_dataset , concatenate_datasets , Dataset 
import sys 
sys.set_int_max_str_digits(0) 

from tqdm import tqdm 
import hashlib

from collections import defaultdict 
from glob2 import glob 

md5_func = lambda x: hashlib.md5(x.encode('utf-8')).hexdigest()

num_workers= os.cpu_count()-1 
batch_size = 16 

import random 

import re
from io import StringIO
import  tokenize
def remove_comments_and_docstrings(source,lang):
    if lang in ['python']:
        """
        Returns 'source' minus comments and docstrings.
        """
        io_obj = StringIO(source)
        out = ""
        prev_toktype = tokenize.INDENT
        last_lineno = -1
        last_col = 0
        for tok in tokenize.generate_tokens(io_obj.readline):
            token_type = tok[0]
            token_string = tok[1]
            start_line, start_col = tok[2]
            end_line, end_col = tok[3]
            ltext = tok[4]
            if start_line > last_lineno:
                last_col = 0
            if start_col > last_col:
                out += (" " * (start_col - last_col))
            # Remove comments:
            if token_type == tokenize.COMMENT:
                pass
            # This series of conditionals removes docstrings:
            elif token_type == tokenize.STRING:
                if prev_toktype != tokenize.INDENT:
            # This is likely a docstring; double-check we're not inside an operator:
                    if prev_toktype != tokenize.NEWLINE:
                        if start_col > 0:
                            out += token_string
            else:
                out += token_string
            prev_toktype = token_type
            last_col = end_col
            last_lineno = end_line
        temp=[]
        for x in out.split('\n'):
            if x.strip()!="":
                temp.append(x)
        return '\n'.join(temp)
    elif lang in ['ruby']:
        return source
    else:
        def replacer(match):
            s = match.group(0)
            if s.startswith('/'):
                return " " # note: a space and not an empty string
            else:
                return s
        pattern = re.compile(
            r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
            re.DOTALL | re.MULTILINE
        )
        temp=[]
        for x in re.sub(pattern, replacer, source).split('\n'):
            if x.strip()!="":
                temp.append(x)
        return '\n'.join(temp)


def step1_get_fn_name_set_from_apps( split="train"):
    
    def _filter_is_fn_name( row, idx  ):
        in_out  = row["input_output"]
        assert type(in_out) ==str 
        try :
            in_out = json.loads(in_out)
        except json.JSONDecodeError as ex :
            return False 
        # if "fn_name"  not in in_out  :
        #     print ( list(in_out)  )
            
        return "fn_name"  in in_out 
    
    def _filter_has_solutions( row, idx  ):
        if "solutions" not in row :
            return False 
        return True 
    
    
    def filter_func( dt ,batch_size=1 ):
        
        dt = dt.filter( 
            _filter_is_fn_name,
                batched=False ,
                batch_size=batch_size,
                with_indices=True,
                num_proc=num_workers,
                load_from_cache_file=True,
            )
        dt = dt.filter( 
            _filter_has_solutions,
                batched=False ,
                batch_size=batch_size,
                with_indices=True,
                num_proc=num_workers,
                load_from_cache_file=True,
            )

        
        dt = dt.map(
            count_solution_size,
                batched=True ,
                batch_size=batch_size,
                with_indices=True,
                num_proc=num_workers,
                load_from_cache_file=True,
            )
        return dt 
    
    
    def count_solution_size( batched, idx  ):
        batched_sol = batched["solutions"]

        def foramt_sol ( one_solution ):
            if type( one_solution ) != list :
                try :
                    sol = json.loads( one_solution  )
                    sol = [sol] if type(sol) == str else sol 
                except :
                    pass  
            else:
                sol =  [one_solution]
            return sol 
        
        batched["solutions"] = [foramt_sol(x) for x in batched_sol ]
        assert type( batched_sol ) == list 
        batched["solutions_size"] = [0]* len(batched_sol)
        batched["md5"] = [0]* len(batched_sol)
        
        for ii  in  range( len(batched_sol) ):
            xx = batched["solutions"][ii]
            
            batched["md5"][ii] = [0]* len( xx )
            batched["md5"][ii] = [md5_func( yy ) for yy in batched["solutions"][ii] ] 
            batched["solutions_size"][ii] = len( batched_sol[ii] )
            
        return batched 


    dataset = load_dataset("codeparrot/apps", split=split )
    dataset  = filter_func( dt =dataset )

    item_list = [] 
    for one in tqdm(dataset ) :
        # print ( list(one), "items of one ")
        sol = one ["solutions"]
        assert type( sol ) == list  
        sol_md5 = one ["md5"]
        assert type( sol_md5 ) == list  ,(sol_md5 )
        
        sol_with_md5 = list( zip (sol, sol_md5) )
        
        # print ( list(one), "list.of one", "len.ssol", len(sol), "sol_md5",len(sol_md5) )
        
        _solution_list = sol_with_md5[:20]
        #_solution_list = {"canonical_solution_list":  json.dumps(_solution_list) } 
        try :
            inx_outx =json.loads( one["input_output"])
        except :
            continue 


        for ii,(_solution,_md5) in enumerate(_solution_list):
            task_id = "cvt_standard_{}#problem_id:{}###order_id:{}###sol_md5:{}".format(split, one["problem_id"] , ii,_md5 )
        
            item = {
                    "task_id":task_id, 
                    "problem_id": task_id.split("###")[0], 
                    "tests": json.dumps( json.loads( one["input_output"]) ), 
                    "extracted_code": _solution  ,
                    "source":"apps",
                    }
            item_list.append( item   )

    print ("total item.list ", len(item_list) )
    return item_list 


def read_jsonl ( jsonp ):
    with open( jsonp ) as fr :
        lines = [json.loads(x) for x in fr.readlines() ]
    return lines 

# def get_full_convert_corpus(   ):
#
#     problem_collections_test = defaultdict(list )
#     problem_collections_train = defaultdict(list )
#
#
#     read_dir = "/home/xxxxxxx/wj_code/dl_execute/reverse_train_data_collecting/data/valid_data_apps_cvt_standardinput"
#     read_f = glob( os.path.join( read_dir , "new_cvt_standard_input_function_t*fingerprinted000.jsonl") )
#
#     lines = []
#     for one_f in read_f :
#         x_lines = read_jsonl( one_f )
#         is_test="standard_input_function_test" in  os.path.basename(one_f )
#         x_lines = [{**x, "x_uuid":x["uuid"].replace("cvt_standard#problem_id","cvt_standard_test#problem_id" if is_test else "cvt_standard_train#problem_id") } for x in x_lines ]
#         lines += x_lines
#     mapping_list  = [x["x_uuid"].split("###")[0] for x in lines ]
#     mapping_list = {x["uuid"]:x  for x in lines }
#
#     print ("ttoal read", len(mapping_list) )
#
#     jsonp_split  = "data/step2_cvt_apps_valid_splited.jsonl"
#
#     if not  os.path.isfile( jsonp_split ):
#         jsonp  = "data/step2_cvt_apps_valid.jsonl"
#         lines = read_jsonl( jsonp )
#
#         for i in range( len(lines ) ):
#             line = lines[i ]
#             x_uuid = mapping_list [ line ["uuid"] ]["x_uuid"]
#             lines[i ]["x_uuid"] = x_uuid
#         with open( jsonp_split ,"w") as fw:
#             fw.write( "\n".join([json.dumps(x) for x in lines ]))
#     else:
#         lines = read_jsonl( jsonp_split )
#
#     total_pid = [x["x_uuid"].split("###")[0] for x in  lines ]
#     total_pid = set(total_pid)
#     ## 
#     corrected_lines = [x for x in lines  if x["flg"] is not None and len(x["flg"])>0 and  all([yy==True for yy in x["flg"] ] )  ]
#     corrected_lines = [ {**x,"x_uuid":mapping_list[x["uuid"] ]["x_uuid"]  } for x in corrected_lines ]
#     print ("correct : ", len(corrected_lines) , "/ ", len( lines ) ,"uniqu proble for all"   , len(total_pid ) )
#     grp_list_test = [x for x in corrected_lines  if x["x_uuid"].startswith("cvt_standard_test") ]
#     grp_list_train = [x for x in corrected_lines  if x["x_uuid"].startswith("cvt_standard_train") ]
#     for x in grp_list_test :
#         pid = x["x_uuid"].split("###")[0]
#         problem_collections_test[pid].append( x )
#     for x in grp_list_train :
#         pid = x["x_uuid"].split("###")[0]
#         problem_collections_train[pid].append( x )
#     print ("test , ", len(problem_collections_test ) )
#     print ("train , ", len(problem_collections_train ) )
#
#
#     print ("=======incorrect ==========="*2 )
#
#     problem_collections_test= defaultdict( list )
#     problem_collections_train= defaultdict( list )
#     ## 
#     corrected_lines = [x for x in lines  if x["flg"] is not None and len(x["flg"])>0 and  any([yy!=True for yy in x["flg"] ] )  ]
#     corrected_lines = [ {**x,"x_uuid":mapping_list[x["uuid"] ]["x_uuid"]  } for x in corrected_lines ]
#     print ("correct : ", len(corrected_lines) , "/ ", len( lines ) )
#     grp_list_test = [x for x in corrected_lines  if x["x_uuid"].startswith("cvt_standard_test") ]
#     grp_list_train = [x for x in corrected_lines  if x["x_uuid"].startswith("cvt_standard_train") ]
#     for x in grp_list_test :
#         pid = x["x_uuid"].split("###")[0]
#         problem_collections_test[pid].append( x )
#     for x in grp_list_train :
#         pid = x["x_uuid"].split("###")[0]
#         problem_collections_train[pid].append( x )
#     print ("test , ", len(problem_collections_test ) )
#     print ("train , ", len(problem_collections_train ) )
    
def step2_get_cross_valid_pass( read_p = "data/step3_cross_valid.jsonl" , read_corpus_p = "./data/step2_cvt_apps_valid_splited.jsonl"):
    
    x_corpus_lines = read_jsonl( read_corpus_p )
    x_corpus_lines = { x["x_uuid"]:x  for x in x_corpus_lines }
    x_corpus_lines_pid_list= defaultdict(list)
    for k,v in x_corpus_lines.items():
        uuid = k 
        if "x_uuid" in v:
            uuid = v["x_uuid"]
            
        pid = uuid.split("###")[0]
        x_corpus_lines_pid_list[pid].append( v )
    
        


    x_lines = read_jsonl( read_p )
    valid_cross_lines_train_pid_list = [ x["pid"]  for x in x_lines if "cvt_standard_train" in x["pid"] ]
    print ("total find train.pid ", len(valid_cross_lines_train_pid_list) )

    valid_cross_lines = [x  for x in x_lines  if x["score"]>=1 ]

    valid_cross_lines_empty = [x  for x in x_lines  if len(x["cross_uuid_list"])==0 ]
    print ("valid_cross_lines_empty", len(valid_cross_lines_empty) )
    
    valid_cross_lines_test_pid_list = [ x["pid"]  for x in valid_cross_lines if "cvt_standard_test" in x["pid"] ]
    valid_cross_lines_test_pid_list = set( valid_cross_lines_test_pid_list )
    
    valid_cross_lines_train_pid_list = [ x["pid"]  for x in valid_cross_lines if "cvt_standard_train" in x["pid"] ]
    valid_cross_lines_train_pid_list = set( valid_cross_lines_train_pid_list )
    
    print ("total find test.pid ", len(valid_cross_lines_test_pid_list) )
    print ("total find train.pid ", len(valid_cross_lines_train_pid_list) )
    
    build_list = {}
    build_item = {"task_id":None, "problem_id":None, "tests":None, "extracted_code":None }
    
    
    item_list = []
    
    for one_pid_line in x_lines :
        selected_pid = one_pid_line["pid"]
        corpus_list = x_corpus_lines_pid_list[ selected_pid ]
        
        for one_line in corpus_list :
            # print ( list(one_line), "--->", one_line )
            if "x_uuid" in one_line :
                uuid = one_line["x_uuid"] 
            else:
                uuid = one_line["uuid"]
            assert ("cvt_standard_test" in uuid  or  "cvt_standard_train" in uuid )
            
            corpus = x_corpus_lines[uuid ]
            
            pid = uuid.split("###")[0]
            x_item = {
                "task_id":uuid,
                "problem_id":pid ,
                # "tests": corpus["testcase_str"] ,
            "tests": json.dumps( corpus["testcase_str"] ) if type(corpus["testcase_str"])==dict else corpus["testcase_str"] ,
                "extracted_code": corpus["function"] ,
                "source":"cross_1",
                 }
            item_list.append( x_item )
        
    return item_list 
    
    
import ast
def get_function_list(code):
    # Parse the code into an AST
    try :
        tree = ast.parse(code)
    except :
        return None 
    # Function to recursively extract function names
    def extract_functions(node):
        functions = []
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.FunctionDef):
                functions.append(child.name)  # Add function name
            # Recursively check for functions in classes or nested scopes
            functions.extend(extract_functions(child))
        return functions

    # Get all functions from the parsed tree
    function_list = extract_functions(tree)
    return function_list

def clean_human_labeled_with_ast( dt_path ):

    def _filter( item, idx  ):


        
        code = item["code"]
        input_output =  item ["input_outputs"] 
        try :
            input_output =json.loads( input_output )
        except json.JSONDecodeError  as ex :
            try:
                input_output = eval(input_output)
            except  Exception  as ex :
                return False 
        
        if type(input_output) !=dict :
            return False 
        
        fn_name = input_output["fn_name"]
        
        func_list = get_function_list( code = code )
        if func_list is None :
            return False 
        func_list = [x.strip() for x in func_list ]
        if fn_name.strip() in func_list :
            return True 
        return False 
        
    
    data_set = load_dataset("json",data_files= dt_path ,split="train" )
    raw_len = len( data_set )
    data_set = data_set.filter( 
        _filter,
            batched=False ,
            batch_size=batch_size,
            with_indices=True,
            num_proc=num_workers,
            load_from_cache_file=True,
        )
    print ("raw.len=",raw_len , "--->filter", len(data_set) )
    
    data_set.to_json( dt_path )##f"squad-{split}.jsonl")

    
def step0_extract_valid_from_apps():
    split = "train"
    dataset_problem_train = load_dataset("codeparrot/apps", split=split  )
    dataset_problem_train = dataset_problem_train.add_column("split",  [split] * len(dataset_problem_train) )
    print ( dataset_problem_train , dataset_problem_train.column_names  )

    split = "test"
    dataset_problem_test = load_dataset("codeparrot/apps", split=split  )
    dataset_problem_test = dataset_problem_test.add_column("split",  [split] * len(dataset_problem_test) )
    print ( dataset_problem_test, dataset_problem_test.column_names  )

    # dataset_problem_train = dataset_problem_train.cast(dataset_problem_test.features)
    dataset_problem = concatenate_datasets( [dataset_problem_test , dataset_problem_train] )

    print ( "fianl", dataset_problem )
    
    
    
    def get_problem_id( item, idx  ):
        pid = item["problem_id"]
        split = item["split"]
        fmt = "cvt_standard_{}#problem_id:{}".format( split , pid )
        item["pid"] = fmt 
        # item["x_fn_name"] = None 
        item["fn_name"] = None 

        inx_out = json.loads( item["input_output"])
        fn_name= None 
        fn_name = inx_out.get("fn_name",None) 
        fn_name = fn_name if fn_name is not None and not fn_name.startswith("__")  else None 
        item["fn_name"]  = fn_name 
        # item["x_fn_name"] = fn_name 
        
        starter_code = item.get("starter_code", None )
        item["x_starter_code"] =  None 

        if starter_code is not None  and len(starter_code)>0 :
            try:
                starter_code = remove_comments_and_docstrings(starter_code,  lang="python")
            except tokenize.TokenError as ex :
                pass 
            if starter_code  is not None and fn_name is not None and fn_name  in starter_code :
                # item ["x_starter_code"]= {"fname": json.dumps(fn_name) , "starter_code_fun_list":json.dumps(starter_code_fun_list) } 
                item ["x_starter_code"]=starter_code 
            else:
                item ["x_starter_code"]= None #json.dumps( {"fname": json.dumps(fn_name) , "starter_code_fun_list":json.dumps(starter_code) }  )
                
        return item 

    remove_columns =[x for x in dataset_problem.column_names  if x not in ["problem_id","question","input_output","split" ,"starter_code" ] ] 
    dataset_problem = dataset_problem.remove_columns(remove_columns )
    raw_len= len( dataset_problem )
    def filter_inxout( item, idx ):
        inx_out = item.get("input_output", None )
        try :
            inx_out = json.loads( inx_out )
        except Exception  as ex :
            return False 
        if type( inx_out) != dict :
            return False 
        return True 
    dataset_problem = dataset_problem.filter(
        filter_inxout,
            batched=False ,
            batch_size=batch_size,
            with_indices=True,
            num_proc=num_workers,
            load_from_cache_file=True,
        )
    print ("filter.step1" , len(dataset_problem) )

        
    dataset_problem = dataset_problem.map(
        get_problem_id,
            batched=False ,
            batch_size=batch_size,
            with_indices=True,
            num_proc=num_workers,
            load_from_cache_file=True,
        )
    # dataset_problem = dataset_problem.remove_columns(["input_output"] )

    
    def _filter_fn_name_not_null(item, idx):
        if "fn_name" not in item or item["fn_name"] is None :
            return False 
        return True 
    dataset_problem_with_fn_name = dataset_problem.filter(
        _filter_fn_name_not_null ,  
                batched=False ,
                batch_size=batch_size,
                with_indices=True,
                num_proc=num_workers,
                load_from_cache_file=True,
        )
    
    def _filter_fn_name_is_null(item, idx):
        if "fn_name" not in item or item["fn_name"] is None :
            return True 
        return False 
    dataset_problem_with_fn_name_error = dataset_problem.filter(
        _filter_fn_name_is_null ,  
                batched=False ,
                batch_size=batch_size,
                with_indices=True,
                num_proc=num_workers,
                load_from_cache_file=True,
        )


    print ( "raw.len", len(dataset_problem), "fn_name is not null", len(dataset_problem_with_fn_name), "fn_name is null ", len(dataset_problem_with_fn_name_error) )

    dataset_problem.to_json( "./data/apps_problem.jsonl" )
    dataset_problem_with_fn_name.to_json( "./data/apps_problem_fnname.jsonl" )
    dataset_problem_with_fn_name_error.to_json( "./data/apps_problem_fnname_error.jsonl" )
   
   
   
def extract_verify_from_generation(ref_json_p =  "./data/step_final_build_HE_for_apps_step1.jsonl" ):
    ref_dt = load_dataset("json", data_files =ref_json_p, split="train" )
    exist_pid = set(ref_dt["problem_id"])

    f_list = []
    search_dir = "/home/xxxxxxx/wj_code/dl_execute/reverse_train_data_collecting/data/valid_data_apps_cvt_standardinput"
    f_list += glob( os.path.join(search_dir , "*extracted-verified.jsonl") )
    search_dir = "/home/xxxxxxx/wj_code/dl_execute/reverse_train_data_collecting/data/valid_data_apps_cvt_standardinput_tmp1"
    f_list += glob( os.path.join(search_dir , "*extracted-verified.jsonl") )
    search_dir = "/home/xxxxxxx/wj_code/dl_execute/reverse_train_data_collecting/data/valid_data_apps_cvt_standardinput_tmp1_002"
    f_list += glob( os.path.join(search_dir , "*extracted-verified.jsonl") )
    print ("total find ", len (f_list) )
    
    random.shuffle( f_list )
    
    line_list = []
    for one_f in f_list :
        one_lines = read_jsonl( one_f )
        one_lines = [x for x in one_lines if x["pid"] not in exist_pid ]
        for i in range(len(one_lines)):
            one_lines[i]["verify_list"] = [int(x) for x in one_lines[i]["verify_list"] ] if one_lines[i]["verify_list"] is not None else []
        line_list+= one_lines 
    
    print ("line list" , len(line_list) )
    random.shuffle( line_list )
    

    dt_verify = [x  for x in line_list  if x["verify"]==True  and  "problem_id"  in  x["pid"] ]
    

    
    # dt_verify = Dataset.from_list( line_list )
    # raw_len = len(dt_verify )
    # def filter_only_verify( item_list, idx_list   ):
    #     return item_list["verify"] 
    # dt_verify = dt_verify.filter(
    #     filter_only_verify ,  
    #             batched=True ,
    #             batch_size=batch_size,
    #             with_indices=True,
    #             num_proc=num_workers,
    #             load_from_cache_file=True,
    #     )
    #

    print ("after only verify ", len( dt_verify ) )
    total_pid = set( [x["pid"] for x in dt_verify]) 
    print ("after only verify. unique.pid = ", len( total_pid ) )
    
    diff_pid = total_pid - exist_pid 
    print ("after only verify. contribute new pid = ", len( diff_pid ) )

    # def filter_is_in_diff_pid( item_list, idx_list   ):
    #     return [xxx in diff_pid  for xxx in item_list["pid"]  ]
    #
    # dt_verify = dt_verify.filter ( 
    #     filter_is_in_diff_pid,
    #             batched=True ,
    #             batch_size=batch_size,
    #             with_indices=True,
    #             num_proc=num_workers,
    #             load_from_cache_file=True,
    #     )
    dt_verify = [x  for x in dt_verify  if x["pid"] in diff_pid   ]
    
    print ("after only verify. contribute new pid(dt_verify) = ", len( dt_verify ) )
    item_list= [] 
    for item in dt_verify:
        
        item_list.append({
            "task_id":item["uuid"],
            "problem_id":item["pid"],
            "tests": json.dumps( item["tests"] ) if type(item["tests"])==dict else item["tests"] ,
            "extracted_code":item["extracted_code"],
            "source":"verify",
             }  )
        
    return item_list 
    
# def extract_verify_from_generation(ref_json_p =  "./data/step_final_build_HE_for_apps_step1.jsonl" ):
#     ref_dt = load_dataset("json", data_files =ref_json_p, split="train" )
#     exist_pid = set(ref_dt["problem_id"])
#
#     f_list = []
#     search_dir = "/home/xxxxxxx/wj_code/dl_execute/reverse_train_data_collecting/data/valid_data_apps_cvt_standardinput"
#     f_list += glob( os.path.join(search_dir , "*extracted-verified.jsonl") )
#     search_dir = "/home/xxxxxxx/wj_code/dl_execute/reverse_train_data_collecting/data/valid_data_apps_cvt_standardinput_tmp1"
#     f_list += glob( os.path.join(search_dir , "*extracted-verified.jsonl") )
#     print ("total find ", len (f_list) )
#
#     random.shuffle( f_list )
#
#     line_list = []
#     for one_f in f_list :
#         one_lines = read_jsonl( one_f )
#         one_lines = [x for x in one_lines if x["pid"] not in exist_pid ]
#         for i in range(len(one_lines)):
#             one_lines[i]["verify_list"] = [int(x) for x in one_lines[i]["verify_list"] ] if one_lines[i]["verify_list"] is not None else []
#         line_list+= one_lines 
#
#     print ("line list" , len(line_list) )
#     random.shuffle( line_list )
#
#
#     dt_verify = Dataset.from_list( line_list )
#     raw_len = len(dt_verify )
#     def filter_only_verify( item_list, idx_list   ):
#         return item_list["verify"] 
#     dt_verify = dt_verify.filter(
#         filter_only_verify ,  
#                 batched=True ,
#                 batch_size=batch_size,
#                 with_indices=True,
#                 num_proc=num_workers,
#                 load_from_cache_file=True,
#         )
#
#     print ("after only verify ", len( dt_verify ) )
#     total_pid = set( dt_verify["pid"]) 
#     print ("after only verify. unique.pid = ", len( total_pid ) )
#
#     diff_pid = total_pid - exist_pid 
#     print ("after only verify. contribute new pid = ", len( diff_pid ) )
#
#     def filter_is_in_diff_pid( item_list, idx_list   ):
#         return [xxx in diff_pid  for xxx in item_list["pid"]  ]
#
#     dt_verify = dt_verify.filter ( 
#         filter_is_in_diff_pid,
#                 batched=True ,
#                 batch_size=batch_size,
#                 with_indices=True,
#                 num_proc=num_workers,
#                 load_from_cache_file=True,
#         )
#     print ("after only verify. contribute new pid(dt_verify) = ", len( dt_verify ) )
#     item_list= [] 
#     for item in dt_verify:
#         item_list.append( item )
#
#     return item_list 
#

     
if __name__=="__main__":
    
    task_list = [] 
    
    ### split fn_name valid and invalid 
    print ("step0 , split fn_name corpus from apps ")
    if not os.path.isfile( "./data/apps_problem.jsonl" ):
        step0_extract_valid_from_apps()
    
    # # ## 
    print ("step1 , get fn_name corpus from apps ")
    solution_list = step1_get_fn_name_set_from_apps() 
    task_list.extend( solution_list )
    
    print ("step1 , ", len(task_list) )
    with open( "./data/step_final_build_HE_for_apps_step1.jsonl" ,"w") as fw :
        xline = "\n".join([json.dumps(x) for x in solution_list ])
        fw.write( xline+"\n")
    
    print ("step1 , get fn_name corpus from apps [test]")
    solution_list = step1_get_fn_name_set_from_apps("test") 
    task_list.extend( solution_list )
    
    print ("total for step1 [test] ", len(solution_list) )
    with open( "./data/step_final_build_HE_for_apps_step1.jsonl" ,"a") as fw :
        xline = "\n".join([json.dumps(x) for x in solution_list ])
        fw.write( xline+"\n")
        # fw.write( "\n".join([json.dumps(x) for x in task_list ]))
    
    
    # get_full_convert_corpus() 
    
    print ("step2 , get get_cross_valid_pass")
    
    solution_list = step2_get_cross_valid_pass() 
    task_list.extend( solution_list )
    
    print ("total for step2 ", len(task_list) )
    with open( "./data/step_final_build_HE_for_apps_step1.jsonl" ,"a") as fw :
        xline = "\n".join([json.dumps(x) for x in solution_list ])
        fw.write( xline+"\n")
    
    #

    
    print ("step3 , get verify list ")
    solution_list =  extract_verify_from_generation()
    print ("total for step1 [test] ", len(solution_list) )
    xline = "\n".join([json.dumps(x) for x in solution_list ])
    with open( "./data/step_final_build_HE_for_apps_step1.jsonl" ,"a") as fw :
        fw.write( xline+"\n")
        # fw.write( "\n".join([json.dumps(x) for x in task_list ]))
    
    
    
    
    print ("final step, combine ")
    # clean_human_labeled_with_ast( dt_path="data/step_final_build_HE_for_apps_step1.jsonl" )
    
    exist_dt = "./data/step_final_build_HE_for_apps_step1.jsonl"
    dt_exist_fn_name = load_dataset("json",data_files=exist_dt, split="train" )
    def filter_source_not_apps( item, idx ):
        return item["source"]!="apps"
    dt_makeup_fn_name =  dt_exist_fn_name.filter( 
        filter_source_not_apps, 
                    batched=False ,
                    batch_size=batch_size,
                    with_indices=True,
                    num_proc=num_workers,
                    load_from_cache_file=True,
        )
    print ( "total raw" , len(dt_exist_fn_name) , "when make up it ", len(dt_makeup_fn_name) )
    
    makeup_pid = dt_makeup_fn_name["problem_id"]
    makeup_pid = set(makeup_pid )
    
    
    exist_dt = "./data/apps_problem_fnname_error.jsonl"
    err_dt  = load_dataset("json",data_files=exist_dt, split="train" )
    error_pid = err_dt["pid"]
    error_pid = set(error_pid )
    assert len(error_pid)> len(makeup_pid)
    common_set = makeup_pid.intersection( error_pid )
    
    print ("common set , " , len(common_set) , "make up ", len( makeup_pid) , "but total ", len(error_pid) )
    diff_set = error_pid - common_set 
    
    with open("./data/demand_apps_pid.jsonl","w") as fw :
        fw.write( "\n".join(list(diff_set)))
    #

    