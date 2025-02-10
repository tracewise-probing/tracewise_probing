import json 
import os ,sys
from  tqdm import tqdm 

import numpy as np 
import traceback 
import random 

from glob import glob 

sys.path.append("../dt_human_label/")

# import apps_metric.evl as xeval 

import utils.tpl_trace_formater as tpl_trace 
from concurrent.futures import ThreadPoolExecutor


num_workers = min(64, os.cpu_count()-1 )

#./apps_v1/meta-llama-3.1-70b-instruct_openai_temp_0.8-fingerprinted010-sanitized-verified.jsonl 

TPL_LIST=["TPL_CODEEXECUTOR","TPL_SEMCODER"]






if __name__=="__main__":

    print ("start ... ")
    json_p_verified = sys.argv[-1]
    assert "extracted-verified" in json_p_verified , json_p_verified 

    new_save_p =  json_p_verified.replace("extracted-verified.jsonl", "extracted-verified-accutraced.jsonl") 
    assert new_save_p != json_p_verified 
    assert  not os.path.isfile( new_save_p ), new_save_p 

    with open( json_p_verified ) as fr :
        lines = fr.readlines() 
        #lines = lines [:200]
        lines = [ json.loads(x) for x in lines ]
    
    # retrieve_raw_llm_rsp ( json_p_verified=json_p_verified  , lines= lines  )
    assert "extracted_code" in lines[0] ,lines[0]
    assert len( lines )>0 
    print ("total reading " , len(lines) ) 

    ##### filter the failure  solutions 
    lines = [x for x in lines if not x["verify"] ]
    random.shuffle(lines)
    # lines = lines[:200]

    print ("total failure " , len(lines) ) 

    item_list = []

    def rebuild_testcase( testcase_str , verify_list ):
        testcase_str = json.loads(testcase_str)
        
        fn_name = testcase_str["fn_name"]
        inputs = testcase_str["inputs"]
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
        return  json.dumps(new_inx_out )
    
    #for one_item in tqdm( lines ) :
    def process_file(  i):
        if i% 100 ==0 :
            print (i)
        one_item = lines[i]


        
        
        verify_list = one_item["verify_list"]
        ## in case all -1 
        if np.all( np.asarray(verify_list)==1 ):
            return None, -1 ### all test cases are correct 

        if np.all( np.asarray(verify_list)==-1 ):
            one_item["verify_msg"] = "syntax error in the code "
            return None,  -2 #"syntax error in the code "
        elif np.all( np.asarray(verify_list)==-2 ):
            one_item["verify_msg"] = "compile error in the code "
            return None , -3 
        elif np.all( np.asarray(verify_list)!=0 ):
            one_item["verify_msg"] = "testcase is pass or timeout, none of fail"
            return None , -4
        elif all(isinstance(x, bool) for x in verify_list):
            one_item["verify_msg"] = "there are failed test cases in the code "

        assert type( one_item["extracted_code"]  ) == str , one_item 
        if one_item["extracted_code"]  is None or len( one_item["extracted_code"] .strip() )<=0 :
            return None ,-5

        testcase_str = rebuild_testcase(testcase_str= one_item["tests"], verify_list=one_item["verify_list"] )
        verify_list = [0]
        # = [i for i,x in enumerate(verify_list) if  x==False  ]
        # verify_list = verify_list[:1]
        #

        sample  = {"input_output":testcase_str , "solution":one_item["extracted_code"], "uuid":one_item["uuid"] }
        assert type(sample) == dict , sample 
        
        try :
            trace_item =tpl_trace.extrace_trace_accmulate (code_str=sample["solution"], sample = sample , err_index_list=verify_list )
            # print (trace_item,"--trace_item")
        except KeyboardInterrupt :
            raise 
        except Exception as ex :
            traceback.print_exc()
            return None ,-6

        if trace_item is None :
            return None  ,-7
        #extrace_trace ( code_str ,  sample , err_index_list=None ):
        # print ( list(trace_item) )
        one_item = {**one_item, **trace_item }
        return one_item ,1 

        #item_list.append( one_item )
    with ThreadPoolExecutor(max_workers=num_workers) as ex:
        predictions = ex.map(process_file, range(len(lines)))
    
    predictions = list( predictions )
    item_list = [x for x,y in predictions if y==1  ]
    
    # for ii in range(len(lines)):
    #     ret_obj = process_file( ii )
    #     assert ret_obj is not None 
    #     ret_item,  status  = ret_obj
    #     assert type(status) == int , ( ret_obj )
    #
    #     print (lines[ii]["uuid"],"status", status, "---", len(lines[ii]["err_list"])  )
    #     if status >0 and len(lines[ii]["err_list"]) >0 :
    #         for one_err in lines[ii]["err_list"]:
    #             print (one_err )
    #         # print ("----",  lines[ii]["err_list"] )
    #     if ii >30 :
    #         break 


    with open( new_save_p , "w") as fw :
        fw.write( "\n".join( [json.dumps(x) for x in item_list ]))

