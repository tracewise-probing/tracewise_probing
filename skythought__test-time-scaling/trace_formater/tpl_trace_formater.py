import json 
import os 
from tqdm import tqdm 
import sys 
import random 
import argparse 

from .select_dynamic  import convert_tracestr_to_sandbox
from .tpl_format import TPL_NEXT, TPL_SCRATCHPAD, TPL_CONCISETRACE , TPL_CODEEXECUTOR, TPL_SEMCODER, TPL_OUR01 

from .format_snoopy import  format_trace  
from .format_snoopy import  xstart as XSTART ,  x_var as X_VAR ,x_var1 as X_VAR1 ,x_return as X_RETURN 
from .format_snoopy import  x_nochange as XNOCHANGE

import warnings 

from concurrent.futures import ThreadPoolExecutor
import tiktoken 

num_workers=  os.cpu_count()-1 
# encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")


encoding = tiktoken.get_encoding("cl100k_base")

def truncate_str(
    req_str: str,
    max_token_size: int = 2048,
    # encoding_name: str = "cl100k_base"
) -> str:
    """
    Truncate the input string so that its token count (by tiktoken) 
    does not exceed max_token_size. Uses the given encoding.
    """
    # get the tokenizer for your model (e.g. gpt-4 uses "cl100k_base")
    if req_str is None:
        return ""
    if not isinstance(req_str, str):
        return ""
    if not req_str.strip():
        return ""
        # encode returns a list of token IDs
    tokens = encoding.encode(req_str)
    
    # if we're already within limits, return original
    if len(tokens) <= max_token_size:
        return req_str
    
    # otherwise cut and decode back to text
    truncated_tokens = tokens[:max_token_size]
    return encoding.decode(truncated_tokens)



def  extrace_trace_accmulate ( trace_list, code_str,  meta_info={}  ):
    ret_item = {}



    # trace_list=[]
    out_list=[]
    err_list_out=[]
    
    

    print ("sandbox_grp_new 000 ", trace_list )
    sandbox_grp_new=  convert_tracestr_to_sandbox( trace_list,code=code_str , meta_info=meta_info  )
    print ("sandbox_grp_new", sandbox_grp_new )
    if sandbox_grp_new is None or len(sandbox_grp_new) <=0 :
        warnings.warn( "empty trace ..... ")
        #print ( code_str )
        return None
    # sandbox_grp_new = {key_str:sandbox for key_str, sandbox  in sandbox_grp.items()  if key_str  in err_index_list } 
    
    # print ("----"*8, sandbox_grp_new, list(sandbox_grp),"--->",err_index_list  ) 
    
    formater_TPL_NEXT = TPL_NEXT()
    formater_TPL_NEXT.init( code= code_str )
    trace_str_formated_next = formater_TPL_NEXT.accumulate_format(  sandbox_grp_new ) 
    ret_item["bug_trace_TPL_NEXT"]  = truncate_str( trace_str_formated_next )
    #
    #
    formater_TPL_OUR01  = TPL_OUR01()
    formater_TPL_OUR01.init( code= code_str )
    trace_str_formated_our01 = formater_TPL_OUR01.accumulate_format(  sandbox_grp_new ) 
    ret_item["bug_trace_TPL_OUR01"] = truncate_str( trace_str_formated_our01  )
    #
    #
    #
    formater_TPL_concise  = TPL_CONCISETRACE()
    formater_TPL_concise.init( code= code_str )
    trace_str_formated_concise = formater_TPL_concise.accumulate_format(  sandbox_grp_new ) 
    ret_item["bug_trace_TPL_CONCISETRACE"]  = truncate_str( trace_str_formated_concise )



    formater_TPL_exe = TPL_CODEEXECUTOR()
    formater_TPL_exe.init( code= code_str )
    trace_str_formated_exe = formater_TPL_exe.accumulate_format(  sandbox_grp_new ) 
    ret_item["bug_trace_TPL_CODEEXECUTOR"] = truncate_str( trace_str_formated_exe )



    return ret_item






