# import json 
# import hashlib
# from glob2 import glob 
# import os 
# import sys 
#
# from collections import Counter
# from collections import defaultdict 
#
# # from evalplus.eval import untrusted_check,is_floats 
#
# md5_func = lambda x: hashlib.md5( x.encode("utf-8") ).hexdigest()  
#
# import random 
# # random.seed(10)
#
# import re 
# from tqdm import tqdm 
# import numpy as np 
#
# sys.path.append( "/home/xxxxxxx/wj_code/dl_execute/self-oss-instruct/selfcodealign/src/")
# from star_align.utils import find_code_blocks 
#
# from utils.utils  import check_correctness 
#
#
# def extract_content_split_function_testcase_or_jsontest( llm_rsp  ):
#
#     content_list =  find_code_blocks( llm_rsp )
#     if len(content_list)!=2 :
#         return None 
#     testcase_str = content_list[-1]
#     try :
#         testcase_str = json.loads( testcase_str )
#         testcase_str = json.dumps( testcase_str )
#     except  json.JSONDecodeError  as ex :
#         try :
#             testcase_str = eval( testcase_str )
#             testcase_str = json.dumps( testcase_str )
#         except Exception  as ex :
#             return None 
#
#     return {"function":content_list[0] , "testcase_str":  testcase_str }
#
#
#
# TIMEOUT = 30
#
# def evaluate_correctness(function_imp, testcase_str,     err_list = [] ):
#     assert "fn_name" in str(testcase_str) , testcase_str 
#
#     sample = {
#         "input_output":json.dumps( testcase_str ) if type(testcase_str)!=str else testcase_str ,
#         }
#
#
#     debug = False  
#     curr_res = [-2]
#     try:
#         curr_res = check_correctness(sample, function_imp, timeout=TIMEOUT, debug=debug ,err_list=err_list)
#         if debug:
#             print(f"\nSuccessful compilation of task {index}!")
#         fixed = []
#         for e in curr_res:
#             if isinstance(e, np.ndarray):
#                e = e.item(0)
#             if isinstance(e, np.bool_):
#                 e = bool(e)
#             fixed.append(e)
#         curr_res = fixed
#         if not np.all(curr_res):
#             if debug:
#                 print(f"Results were not True for all test cases")
#     except Exception as e:
#         if debug:
#             print(f"Compilation failed, test framework exception = {repr(e)}{e}\n")
#         return None 
#     finally:
#         assert isinstance(curr_res, list)
#
#     # if len(curr_res)>0 and all(curr_res)==True :
#     return curr_res 
#
#     # return curr_res
#
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
#             if "fn_name" in each_j :
#                 each_j.pop("fn_name")
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
#     read_f = glob( os.path.join( read_dir , "new_cvt_standard_input_function_t*fingerprinted000.jsonl") )
#
#     lines = []
#     for one_f in read_f :
#         x_lines = read_jsonl( one_f )
#         is_test="standard_input_function_test" in  os.path.basename(one_f )
#         x_lines = [{**x, "x_uuid":x["uuid"].replace("cvt_standard#problem_id","cvt_standard_test#problem_id" if is_test else "cvt_standard_train#problem_id") } for x in x_lines ]
#         lines += x_lines
#
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
#     one_pid_info = []
#
#     for pid, one_pid_list  in pid_list.items() :
#
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
#     if len(one_pid_info)<=0:
#         exit()
#
#
#     ### filter exist 
#     exist_list = []
#     if os.path.isfile("./data/step2_cvt_apps_valid.jsonl" ):
#         with open("./data/step2_cvt_apps_valid.jsonl") as fr :
#             exist_lines = [json.loads(x) for x in fr.readlines() ]
#             exist_lines_uuid =set(  [x["uuid"] for x in exist_lines ] )
#
#         one_pid_info_filter = [x for x in one_pid_info if x["uuid"] not in exist_lines_uuid ]
#
#     print ("exist removed-->",len(one_pid_info_filter)," / ",len(one_pid_info) )
#
#     one_pid_info  = one_pid_info_filter 
#
#     # exit()
#
#     def chunks(lst, n):
#         """Yield successive n-sized chunks from lst."""
#         for i in range(0, len(lst), n):
#             yield lst[i:i + n]
#
#     random.shuffle( one_pid_info )
#
#
#     for one_pid_info_sub in chunks( one_pid_info, 500 ):
#         total_eval= []
#         total_correct  = [] 
#         sub_list = []
#         for ii, one_meta in tqdm( enumerate( one_pid_info_sub ) ):
#             err_list = []
#             is_correct = evaluate_correctness(function_imp=one_meta["function"], testcase_str=one_meta["testcase_str"] ,err_list=err_list )
#             if is_correct is None :
#                 sub_list.append( {**one_meta, "flg":is_correct, "err_list":err_list })
#                 continue
#             if len(is_correct)>0 and all([xx==True for xx in is_correct ]) :
#                 total_correct.append( is_correct )
#
#             total_eval.append( is_correct )
#
#             sub_list.append( {**one_meta, "flg":is_correct, "err_list":err_list })
#         passrate = len(total_correct)/len(total_eval)
#         print (passrate, "--->", "pass rate correct ", len(total_correct), "total", len(total_eval ), "" )
#         # print ( np.unique(status_list,return_counts=True ) )
#
#         with open("./data/step2_cvt_apps_valid.jsonl","a") as fw :
#             info_list ="\n".join( [json.dumps(x) for x in sub_list ] )
#             fw.write( info_list + "\n" )
#
#
#
