from typing import Optional, Callable, Dict
import ast
import copy
import contextlib
import faulthandler
import io
from io import StringIO
import os
import multiprocessing
import platform
import signal
import tempfile
import json
import sys
import builtins
import shutil
import subprocess
import time
# import dspy
# from util import post_process_code
import traceback 
import pysnooper
from .tpl_trace_formater import extrace_trace_accmulate
# import pprint 

    
    
def run_test_func_snoopy(completion, is_extracted, test_input, test_output):

    def format_snoopy(pysnoopy_msg,result_output):
        pysnoopy_msg = pysnoopy_msg.decode() if type(pysnoopy_msg)==bytes else pysnoopy_msg
        pysnoopy_msg = pysnoopy_msg.decode() if type(pysnoopy_msg)==bytes else pysnoopy_msg
        pysnoopy_msg ="\n".join([f"t_000001{x}" for x in pysnoopy_msg.split("\n")]) 
    
        pysnoopy_msg = extrace_trace_accmulate (
            trace_list= [pysnoopy_msg] if type(pysnoopy_msg)==str else pysnoopy_msg , 
            code_str=completion,
            meta_info={"input":test_input,"output":test_output,"true_output":result_output, "test_type" : "functional_snoopy"} 
             )
        
        return pysnoopy_msg 
    pysnoopy_msg = None 
    tmp_name = None 
    
    
    if "(" not in completion:
        return False, f"Error: your completion didnot have any function", pysnoopy_msg

    
    if not is_extracted:
        namespace = {}

        exec(completion, namespace)

        # Retrieve the function name from the completion (assuming the function name is consistent)
        func_name = completion.split("(")[0].split()[-1]

        # Ensure inputs and expected_output are correctly parsed from JSON
        if isinstance(test_input, dict):
            # If the input is a dictionary, pass it as keyword arguments
            args = []
            kwargs = test_input  # The dictionary is passed as keyword arguments
        else:
            # If the input is not a dictionary, pass it as a single argument
            args = [test_input]  # Wrap inputs in a list, keeping it as one argument
            kwargs = {}

        # Redirect stdout to capture any printed output
        output = io.StringIO()
        sys.stdout = output

        # Call the function and get the result
        try:
            os.makedirs("/tmp/snooper_dir",exist_ok=True)
            with tempfile.NamedTemporaryFile(delete=True, dir="/tmp/snooper_dir" ) as temp:
                tmp_name = temp.name 
                namespace[func_name] = pysnooper.snoop(tmp_name , normalize=True, color=False , depth=1 )(namespace[func_name])
                result_output = namespace[func_name](*args, **kwargs)

                temp.flush()
                temp.seek(0)
                pysnoopy_msg = temp.read() 

            pysnoopy_msg = format_snoopy(pysnoopy_msg,result_output=result_output)
                # print ("--->", output_trace,output_trace_formated , "<----")
            # pysnoopy_msg = output.getvalue()
            # Compare the result with expected output
            if result_output != test_output:
                return False, result_output, pysnoopy_msg

        except Exception as e:
            # traceback.print_exc()
            # Capture and return the exception if one occurs
            return False, f"Error: {str(e)}", pysnoopy_msg

        finally:
            # Reset stdout
            sys.stdout = sys.__stdout__
            # print ("------->"*8) 
            # print ("pysnoopy_msg.rype", type(pysnoopy_msg) )
            # pprint.pprint (pysnoopy_msg)
            # print ("<-------"*8) 
            if tmp_name and os.path.isfile(tmp_name):
                os.unlink (tmp_name )
            #

        return True, result_output, pysnoopy_msg
    else:
        namespace = {}

        # Execute the generated code in the namespace

        exec(completion, namespace)

        # Retrieve the function name from the completion (assuming the function name is consistent)
        func_name = completion.split("(")[0].split()[-1]

        # Redirect stdout
        output = io.StringIO()
        sys.stdout = output

        # Call the function and get the result
        try:
            os.makedirs("/tmp/snooper_dir",exist_ok=True)
            with tempfile.NamedTemporaryFile(delete=True, dir="/tmp/snooper_dir" ) as temp:
                tmp_name = temp.name 

                namespace[func_name] = pysnooper.snoop(tmp_name,  normalize=True, color=False , max_variable_length=40, depth=1  )(namespace[func_name])
                result_output = namespace[func_name](*test_input)

                temp.flush()
                temp.seek(0)
                pysnoopy_msg = temp.read() 

            pysnoopy_msg = format_snoopy(pysnoopy_msg,result_output=result_output)


            if result_output != test_output:
                return False, result_output, pysnoopy_msg 
        except Exception as e:
            # traceback.print_exc()
            return False, f"Error: {str(e)}", pysnoopy_msg

        finally:
            # Reset stdout
            sys.stdout = sys.__stdout__
            # print ("------->"*8) 
            # print ("pysnoopy_msg.rype", type(pysnoopy_msg) )
            # pprint.pprint (pysnoopy_msg)
            # print ("<-------"*8) 
            if tmp_name and os.path.isfile(tmp_name):
                os.unlink (tmp_name )

        return True, result_output , pysnoopy_msg


def build_stdin_code(test,snooper_handler):
    tmp_test = test.split("\n")

    new_test = []
    for x in tmp_test:
        if (not x.startswith("from ")) and (not x.startswith("import ")):
            new_test.append("\t" + x + "\n")
        else:
            new_test.append(x + "\n")
    tmp_test = new_test

    new_test = ""
    started = False
    for i in tmp_test:
        if i.startswith("\t") and not started:
            if snooper_handler:
                # new_test += "import os\n"
                # new_test += "import pysnooper\n"
                # new_test += f"@pysnooper.snoop('{snooper_handler}', normalize=True, color=False , max_variable_length=40 , depth=3   )\n"
                pass
            new_test += "def call_wrap_snoopy():\n"
            # new_test += "\tprint ( os.environ,'------'*8 )\n"
            new_test += i
            started = True
        elif started and ((i.startswith("from ")) or (i.startswith("import "))): 
            new_test += "\t" + i
        else:
            new_test += i
    tmp_test = new_test

    return tmp_test

# def build_stdin_code(test: str, snooper_handler: Optional[str] = None) -> str:
#     """
#     Wraps the test script into a code() function, capturing stdin/stdout
#     and applying pysnooper snoop if handler is provided.
#     """
#     lines = test.splitlines()
#     wrapped = []
#     # Base imports and I/O handles
#     wrapped.append("import sys")
#     wrapped.append("stdin = sys.stdin")
#     wrapped.append("stdout = sys.stdout")
#     # Add snooper decorator if handler path is given
#     if snooper_handler:
#         wrapped.append("import pysnooper")
#         decorator = f"@pysnooper.snoop('{snooper_handler}', normalize=True, color=False, depth=1)"
#         wrapped.append(decorator)
#     # Define the entry function
#     wrapped.append("def code():")
#     for line in lines:
#         # Preserve import statements inside the function body with proper indentation
#         if line.startswith("from ") or line.startswith("import "):
#             wrapped.append(f"    {line}")
#         else:
#             wrapped.append(f"    {line}")
#     return "\n".join(wrapped)



def run_test_std_snoopy(completion, test_input, test_output):
    def format_snoopy(pysnoopy_msg,result_output):
        pysnoopy_msg = pysnoopy_msg.decode() if type(pysnoopy_msg)==bytes else pysnoopy_msg
        pysnoopy_msg = pysnoopy_msg.decode() if type(pysnoopy_msg)==bytes else pysnoopy_msg
        pysnoopy_msg ="\n".join([f"t_000001{x}" for x in pysnoopy_msg.split("\n")]) 
    
        pysnoopy_msg = extrace_trace_accmulate (
            trace_list= [pysnoopy_msg] if type(pysnoopy_msg)==str else pysnoopy_msg , 
            code_str=completion,
            meta_info={"input":test_input,"output":test_output,"true_output":result_output, "test_type" : "stdin_snoopy"} 
             )
        
        return pysnoopy_msg 
    
    pysnoopy_msg = None 
    tmp_name = None 
    completion_wraped = ""
    output_value = None 
    
    if '__name__ == "__main__"' in completion:
        # Simulate that the code is being run as the main script
        completion = f'__name__ = "__main__"\n' + completion
    
    namespace = {}
    try:
        os.makedirs("/tmp/snooper_dir",exist_ok=True)
        with tempfile.NamedTemporaryFile(delete=True, dir="/tmp/snooper_dir" ) as temp:
            tmp_name = temp.name 


            completion_wraped = build_stdin_code(completion,tmp_name)
            func_name = "call_wrap_snoopy"

            sys.stdin = StringIO(test_input)
            output = StringIO()
            sys.stdout = output

            exec(completion_wraped, namespace)

            namespace[func_name] = pysnooper.snoop(tmp_name,  normalize=True, color=False , max_variable_length=40,depth=2  )(namespace[func_name])
            namespace[func_name]()
            # result_output = 
            output_value = output.getvalue().strip()


            
            temp.flush()
            temp.seek(0)
            pysnoopy_msg = temp.read() 

            pysnoopy_msg = format_snoopy(pysnoopy_msg,result_output=output_value)

    except Exception as e:
        # traceback.print_exc()
        return False, str(e), pysnoopy_msg

    finally:
        # Reset stdout
        sys.stdout = sys.__stdout__
        sys.stdin  = sys.__stdin__
        # print ("------->"*8) 
        # print ("pysnoopy_msg.rype", type(pysnoopy_msg) )
        # print (tmp_name,completion_wraped,"\n\n---->", pysnoopy_msg )
        # print ("<-------"*8) 
        if tmp_name and os.path.isfile(tmp_name):
            os.unlink (tmp_name )

    # output_value = output.getvalue().strip()
    return output_value == test_output, output_value, pysnoopy_msg

