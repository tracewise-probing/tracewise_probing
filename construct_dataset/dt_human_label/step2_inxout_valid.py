# import json 
# import hashlib
# from glob2 import glob 
# import os 
# import sys 
#
# from collections import Counter
# from collections import defaultdict 
#
# from evalplus.eval import untrusted_check,is_floats 
#
# md5_func = lambda x: hashlib.md5( x.encode("utf-8") ).hexdigest()  
#
# import random 
#
# import re 
# import numpy as np 
#
# sys.path.append( "/home/xxxxxxx/wj_code/dl_execute/self-oss-instruct/selfcodealign/src/")
# from star_align.utils import find_code_blocks 
#
#
# def extract_content_split_function_testcase_or_jsontest( llm_rsp  ):
#
#     content_list =  find_code_blocks( llm_rsp )
#     if len(content_list)!=2 :
#         return None 
#     return {"function":content_list[0] , "testcase_str":  content_list[-1] }
#
# def evaluate_correctness(function_imp, testcase_str ):
#     def format_testcase_str  ( tinfo ):
#         try :
#             tinfo = json.loads( tinfo )
#         except :
#             pass 
#         ret_info = {}
#         if "input" in tinfo :
#             ret_info ["input"]= tinfo["input"]
#         elif "inputs" in tinfo :
#             ret_info ["input"]= tinfo["inputs"]
#
#         if "output" in tinfo :
#             ret_info ["output"]= tinfo["output"]
#         elif "outputs" in tinfo :
#             ret_info ["output"]= tinfo["outputs"]
#         elif "expect" in tinfo :
#             ret_info ["output"]= tinfo["expect"]
#         elif "expects" in tinfo :
#             ret_info ["output"]= tinfo["expects"]
#
#         if "entry_point" in tinfo :
#             ret_info ["entry_point"]= tinfo["entry_point"]
#         elif "fn_name" in tinfo :
#             ret_info ["entry_point"]= tinfo["fn_name"]
#         return ret_info 
#
#     try :
#         problem = json.loads( testcase_str )
#     except json.JSONDecodeError as ex:
#         try :
#             problem = eval( testcase_str )
#         except :
#             return None 
#
#     problem_list = [problem] if type(problem)!=list else problem 
#
#     problem_list_formated = []
#     for problem_i in range(len(problem_list )):
#         problem = problem_list [problem_i ]
#         problem = format_testcase_str( problem )
#         if "entry_point" not in problem or "output" not in problem or "input" not in problem :
#             # print ( problem ,"---> problem ")
#             continue 
#         problem_list_formated.append( problem )
#
#
#     entry_point =  [x["entry_point"] for x in problem_list_formated ]
#     if len(set(entry_point)) != 1 :
#         # print ("errr;......")
#         return None 
#
#     assert len(set(entry_point)) == 1 , (problem_list_formated,problem_list )
#     entry_point = entry_point[-1]
#
#     expected_output = [x["output"] for x in problem_list_formated ] 
#     for i in range(len(expected_output)):
#         expect = expected_output[i].strip()
#         if "\n" in expect :
#             expect = expect.split("\n")
#             try :
#                 expect = [eval(x) for x in expect ]
#             except :
#                 pass 
#         else:
#             try :
#                 expect = eval(expect)
#             except :
#                 pass 
#
#         expected_output[i] = expect 
#
#     # expected_output = [float(x) for x in expected_output if is_floats(x)]
#
#     status, ret_list   = untrusted_check(
#         dataset="None",
#         code=function_imp,
#         inputs=  [x["input"] for x in problem_list_formated ],
#         entry_point= entry_point , 
#         expected= expected_output  ,
#         atol=0, #problem["atol"],
#         ref_time=[5],
#         fast_check=False,
#     )
#     if status =="fail":
#         print (problem_list_formated, "\n","\n"+function_imp,) 
#
#     # print ( is_correct )
#     return  is_correct 
#
# def vote_json_valid( inx_out_list ):
#
#
#
#     inx_out_list_valid = []
#
#     for each_j in inx_out_list :
#         try :
#             each_j = json.loads(each_j )
#         except json.JSONDecodeError :
#             continue 
#
#         inx_out_list_valid.append( each_j )
#
#     if len(inx_out_list_valid)<=0 :
#         return -3 ,None 
#     ## 
#     ## vote from json.dump.md5 
#     inx_out_list_valid_md5 = [( md5_func( json.dumps(x) ), x ) for x in inx_out_list_valid ]
#
#     vote_counter = Counter([x for x,y in inx_out_list_valid_md5 ])
#     # Find the most common tuple(s)
#     most_common = vote_counter.most_common(1)  # Returns a list of the most common tuple(s) and their counts
#     # print ( most_common )
#     if len(most_common) <=0:
#         return -1 ,None 
#
#     most_frequent_md5value, frequency = most_common[0]
#
#     if frequency >1 :
#         inx_out_list_valid_md5 = [json_str for  md5,json_str  in  inx_out_list_valid_md5 if md5 == most_frequent_md5value]
#         assert  len(inx_out_list_valid_md5)>0 
#         ans_str = inx_out_list_valid_md5[-1]
#
#         return 1, ans_str 
#
#
#     # print (list(vote_counter), "--vote_counter") 
#     return -2 ,None 
#
#
#
# def read_jsonl( json_p ):
#     with open( json_p )as fr :
#         lines =[json.loads(x) for x in fr.readlines() ]
#     return lines 
#
# def get_pid ( uuid ):
#     #  "uuid": "cvt_standard#problem_id:645###order_id:5###llm_md5:c32ac37c0f75f4b193708ded38dcc1a7"
#     pid = uuid.split("problem_id:")[-1]
#     pid = pid.split("###")[0]
#     return pid 
#
# if __name__=="__main__":
#
#     read_dir = "/home/xxxxxxx/wj_code/dl_execute/reverse_train_data_collecting/data/valid_data_apps_cvt_standardinput"
#     read_f = glob( os.path.join( read_dir , "cvt_standard_input_function_test*fingerprinted000.jsonl") )
#
#     lines = []
#     for one_f in read_f :
#         lines += read_jsonl( one_f )
#     print ("ttoal read", len(lines) )
#
#     random.shuffle( lines )
#     ## 
#     pid_list = defaultdict( list )
#     for one_line in lines :
#         pid = get_pid( uuid = one_line["uuid"] )
#
#         if pid not in pid_list :
#             pid_list [pid] = [one_line]
#         else:
#             pid_list [pid] .append( one_line )
#
#
#
#     ## expand the pid's info     
#     status_list = []
#     err_info = {}
#
#     for pid, one_pid_list  in pid_list.items() :
#
#         one_pid_info = []
#         for one_content in one_pid_list :
#             llm_rsp = one_content["solution"]
#             uuid = one_content["uuid"]
#             content_info  = extract_content_split_function_testcase_or_jsontest( llm_rsp  =llm_rsp  )
#             if content_info is None :
#                 err_info[ uuid ] = {"status":-1,"msg":"llm_rsp block error"}
#                 continue 
#             content_info = {**content_info, "uuid":uuid, "pid":pid }
#             one_pid_info.append(  content_info )
#
#         # print (one_pid_info )
#         # vote_json_valid_list = [x["testcase_str"] for x in one_pid_info ] 
#         # status , selected_testcase = vote_json_valid( inx_out_list=vote_json_valid_list )
#         # # print( selected_testcase )
#         # # break 
#         #
#         # if status <=0 :
#         #     # print( "--len", status, len(vote_json_valid_list)  )
#         #     status_list.append( status )
#         #     continue 
#
#         for one_meta in one_pid_info:
#             is_correct = evaluate_correctness(function_imp=one_meta["function"], testcase_str=one_meta["testcase_str"] )
#
#             print ( is_correct )
#     print ( np.unique(status_list,return_counts=True ) )
#
#
#
#
