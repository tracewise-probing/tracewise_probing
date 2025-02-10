import json 
import os 
from tqdm import tqdm 
import sys 
import random 
import argparse 

from .apps_metric.select_dynamic  import convert_tracestr_to_sandbox
from .apps_metric.tpl_format import TPL_NEXT, TPL_SCRATCHPAD, TPL_CONCISETRACE , TPL_CODEEXECUTOR, TPL_SEMCODER, TPL_OUR01 


import warnings 

from concurrent.futures import ThreadPoolExecutor
import tiktoken 

num_workers=  os.cpu_count()-1 
encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")


#"TPL_CODEEXECUTOR",
#"TPL_NEXT",


def  extrace_trace_accmulate ( code_str ,  sample , err_index_list=None ):
    ret_item = {}


    if err_index_list is None :
        inx_out= json.loads( sample["input_output"] )
        err_index_list = list( range( len(inx_out["inputs"])))

        warnings.warn("using all input as error index  ")

    assert  all( [str(x).isdigit() for x in err_index_list ] )
    if  len( err_index_list ) <=0  :
        return  None

    err_index_list = ["t_{}".format(str(x).zfill(6)) for x in err_index_list ]

    trace_list=[]
    out_list=[]
    err_list_out=[]

    sandbox_grp=  convert_tracestr_to_sandbox( code= code_str, sample = sample  )
    if sandbox_grp is None or len(sandbox_grp) <=0 :
        warnings.warn( "empty trace ..... ")
        #print ( code_str )
        return None
    sandbox_grp_new = {key_str:sandbox for key_str, sandbox  in sandbox_grp.items()  if key_str  in err_index_list } 
    
    # print ("----"*8, sandbox_grp_new, list(sandbox_grp),"--->",err_index_list  ) 
    
    formater_TPL_NEXT = TPL_NEXT()
    formater_TPL_NEXT.init( code= code_str )
    trace_str_formated_next = formater_TPL_NEXT.accumulate_format(  sandbox_grp_new ) 
    ret_item["bug_trace_TPL_NEXT"]  = trace_str_formated_next
    #
    #
    formater_TPL_OUR01  = TPL_OUR01()
    formater_TPL_OUR01.init( code= code_str )
    trace_str_formated_our01 = formater_TPL_OUR01.accumulate_format(  sandbox_grp_new ) 
    ret_item["bug_trace_TPL_OUR01"] = trace_str_formated_our01 
    #
    #
    #
    formater_TPL_concise  = TPL_CONCISETRACE()
    formater_TPL_concise.init( code= code_str )
    trace_str_formated_concise = formater_TPL_concise.accumulate_format(  sandbox_grp_new ) 
    ret_item["bug_trace_TPL_CONCISETRACE"]  = trace_str_formated_concise



    formater_TPL_exe = TPL_CODEEXECUTOR()
    formater_TPL_exe.init( code= code_str )
    trace_str_formated_exe = formater_TPL_exe.accumulate_format(  sandbox_grp_new ) 
    ret_item["bug_trace_TPL_CODEEXECUTOR"] = trace_str_formated_exe 



    return ret_item




def  extrace_trace ( code_str ,  sample , err_index_list=None ):
    ret_item = {}

    formater_TPL_CODEEXECUTOR = TPL_CODEEXECUTOR()
    formater_TPL_NEXT = TPL_NEXT()
    formater_TPL_OUR01  = TPL_OUR01()

    if err_index_list is None :
        inx_out= json.loads( sample["input_output"] ) 
        err_index_list = list( range( len(inx_out["inputs"])))

        warnings.warn("using all input as error index  ")

    assert  all( [str(x).isdigit() for x in err_index_list ] ) 
    if  len( err_index_list ) <=0  :
        return  None  

    err_index_list = ["t_{}".format(str(x).zfill(6)) for x in err_index_list ]

    trace_list=[]
    out_list=[]
    err_list_out=[]

    sandbox_grp=  convert_tracestr_to_sandbox( code= code_str, sample = sample  )
    if sandbox_grp is None or len(sandbox_grp) <=0 :
        warnings.warn( "empty trace ..... ")
        #print ( code_str )
        return None 

    for key_str, sandbox  in sandbox_grp.items() : 

        #sandbox  = sandbox_grp["t_000000"]#.raw_trace
        if key_str not in err_index_list :
            continue 
     
        lines = sandbox._states
        meta_info = sandbox._meta_info
        
        #trace_info  = formater_TPL_CODEEXECUTOR.format( code= code_str,  lines=  lines , meta_info = meta_info )
        #ret_item["{}__bug_trace_TPL_CODEEXECUTOR".format( key_str )]= trace_info 
        
        trace_info  = formater_TPL_OUR01.format( code= code_str,  lines=  lines , meta_info = meta_info )
        ret_item["{}__bug_trace_TPL_OUR01".format( key_str )]= trace_info 
    
        trace_info  = formater_TPL_NEXT.format( code= code_str,  lines=  lines , meta_info =meta_info )
        ret_item["{}__bug_trace_TPL_NEXT".format( key_str )]= trace_info 

    if len( ret_item ) <=0 :
        return None 

    return ret_item 
        



