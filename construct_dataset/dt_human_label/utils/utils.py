from datasets import load_dataset
from tqdm import tqdm 
from typing import Dict
import contextlib
import io
import itertools
import json
import multiprocessing
import numpy as np
import os ,sys 
import random

from .testing_util import run_test

DATASET = "codeparrot/apps"
TIMEOUT = 30


sys.set_int_max_str_digits(0)
num_workers=16#os.cpu_count()/2-1


#
def check_correctness(sample, generation, timeout, debug=True,err_list=[]):
    """Check correctness of code generation with a global timeout.
    The global timeout is to catch some extreme/rare cases not handled by the timeouts
    inside `run_test`"""
    def _temp_run(sample, generation, debug, result):
        _err_list = []
        result.append(run_test(sample, test=generation, debug=debug,err_list=_err_list ))
        g_err_list.extend( _err_list )

    manager = multiprocessing.Manager()
    result = manager.list()
    g_err_list = manager.list()
    p = multiprocessing.Process(target=_temp_run, args=(sample, generation, debug, result))
    p.start()
    p.join(timeout=timeout + 1)
    if p.is_alive():
        p.kill()
    if not result:
        in_outs = json.loads(sample["input_output"])
        # consider that all tests failed
        result = [[-1 for i in range(len(in_outs["inputs"]))]]
        if debug:
            print(f"global timeout")
        g_err_list = ["Timeout"]

    err_list.extend( g_err_list )

    return result[0]




def run_test_wrapper(args):
    sample, generation, debug ,err_list= args
    return run_test(sample, test=generation, debug=debug,err_list=err_list)

# def check_correctness(sample, generation, timeout, debug=True,err_list=[]):
#     # Initialize pool with one worker (or adjust as needed)
#     with multiprocessing.Pool(1) as pool:
#         # Apply async with timeout to run the test
#         result = pool.apply_async(run_test_wrapper, ((sample, generation, debug,err_list),))
#         try:
#             result = result.get(timeout=timeout + 1)
#         except multiprocessing.TimeoutError:
#             in_outs = json.loads(sample["input_output"]) if type( sample["input_output"] ) ==str else sample["input_output"] 
#             # Consider that all tests failed in case of timeout
#             result = [-1 for _ in range(len(in_outs["inputs"]))]
#             err_list = ["timeout "]*len(result )
#             if debug:
#                 print("global timeout")
#     return result


def verify_unittest( solution, sample ,debug=False ):


    err_list = []
    curr_res = check_correctness(sample, solution   , timeout=TIMEOUT, debug=debug ,err_list=err_list )        
    if len(curr_res)<=0:
        return None,None ,None 
    
    try :
        fixed = []
        for e in curr_res:
            if isinstance(e, np.ndarray):
               e = e.item(0)
            if isinstance(e, np.bool_):
                e = bool(e)
            fixed.append(e)
        curr_res = fixed
    except KeyboardInterrupt:
        raise 
    except Exception as e:
        if debug:
            print(f"Compilation failed, test framework exception = {repr(e)}{e}\n")
        return  -1  ,None, []
    finally:
        assert isinstance(curr_res, list)
    
    return bool(np.all( np.asarray(curr_res )>0 ) ) ,  curr_res , err_list

