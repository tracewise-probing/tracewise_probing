import ast 
import re 
import json 
import os 

entry_pattern = r"def (\w+)\s?\("

def get_entry_point( x_start_coder):
    if x_start_coder is None or type(x_start_coder)!=str:
        return None 
    funcs = re.findall(entry_pattern, x_start_coder )
    funcs = funcs[0] if type(funcs)==list and len(funcs)>0 else None 
    return funcs 

# def split_input( sample ):
#     def _build_input(idx, inputx ):
#         if type(inputx)==list:
#             inputx = json.dumps(inputx)
#             inputx = inputx[1:-1]
#         else:
#             inputx = json.dumps( inputx )
#         valu = tpl_input.format( idx,inputx, idx  )
#         return valu 
#
#
#     assert "input_output" in sample 
#     try :
#         in_outs = json.loads(sample["input_output"])
#     except ValueError:
#         return None 
#
#     tpl_list = [] 
#
#     for index, inputs in enumerate(in_outs["inputs"][:20]):
#         try:
#             if isinstance(inputs[0], dict):
#                 inputs = [{int(k): v for k,v in inputs[0].items()}]
#         except:
#             True
#         try:
#             if isinstance(in_outs["outputs"][index], dict):
#                 in_outs["outputs"][index] = [{int(k): v for k,v in in_outs["outputs"][index].items()}]
#         except:
#             True
#         try:
#             if isinstance(in_outs["outputs"][index][0], dict):
#                 in_outs["outputs"][index] = [{int(k): v for k,v in in_outs["outputs"][index][0].items()}]
#         except:
#             True
#
#         tpl_list.append( _build_input(idx=index, inputx=inputs ))
#
#     return tpl_str 





class FunctionCallGenerator(ast.NodeVisitor):
    def __init__(self, target_func_name):
        self.class_name = None
        self.target_func_name = target_func_name
        self.arg_names = []
        self.func_found = False

    def visit_ClassDef(self, node):
        self.class_name = node.name
        self.generic_visit(node)  # Continue visiting inside the class

    def visit_FunctionDef(self, node):
        if node.name == self.target_func_name:
            self.func_found = True
            if self.class_name:
                # Exclude 'self' from the arguments
                self.arg_names = [arg.arg for arg in node.args.args if arg.arg != 'self']
            else:
                self.arg_names = [arg.arg for arg in node.args.args]

def express(func_name,arg_list):
    if type(arg_list) in [float,int,dict,str ]:
        arg_list = [ arg_list ]
    else:
        assert type(arg_list) in [tuple,list], type(arg_list)
        arg_list = [ x if type(x)!=str else repr(x)  for x in arg_list]

    arg_format = "{},"*len(arg_list)
    arg_format = arg_format.rstrip(",")
    final_format = "{} ("+arg_format+")"

    func_call = final_format.format( func_name ,  * arg_list   )
    return func_call 



def _generate_function_call(func_def, func_name, arg_list):
    # Parse the function definition to get the class name, function name, and argument names
    tree = ast.parse(func_def)
    generator = FunctionCallGenerator(func_name)
    generator.visit(tree)

    func_call = None 
    if  generator.func_found:
        #raise ValueError(f"Function {func_name} not found in the provided definition. ---:::: {func_def},------------>{arg_list}")
        # Generate the function call with the provided arguments
        class_name = generator.class_name
        arg_names = generator.arg_names
        arg_str_list = [f'{name}={value!r}' for name, value in zip(arg_names, arg_list)]

        if func_name is None and class_name:
            func_call = f'{class_name}().{func_name}({", ".join(arg_str_list)})'
        elif arg_str_list is not None and len(arg_str_list)>0 :
            func_call = f'{func_name}({", ".join(arg_str_list)})'

    if func_call is None :
        assert "*" in func_def or "lambda" in func_def, (func_def, func_name ) 
        func_call =express( func_name=func_name, arg_list=arg_list)# '{} ({}) '.format( func_name ,  args = ",".join(list(map(repr, rparg_list ) ) ) )

    return func_call

def _generate_assert_statement(func_def, func_name, arg_list, expected_output, is_compare_on_str_level=False ):
    func_call = _generate_function_call(func_def, func_name, arg_list)
    if type(expected_output)==bool :
        expected_output_str = "not" if not expected_output else " "
        return {"assert_gt": f"assert {expected_output_str} {func_call} "}
    if  is_compare_on_str_level :
        return  {"assert_gt":f"assert json.dumps( ({func_call}) )== json.dumps(({expected_output!r} ))"}
    else:
        return  {"assert_gt":f"assert {func_call} == {expected_output!r}" }


def _generate_masked_assert_statement(func_def, func_name, expected_output, arg_list = None, is_compare_on_str_level=False  ):
    # Parse the function definition to get the class name, function name, and argument names
    tree = ast.parse(func_def)
    generator = FunctionCallGenerator(func_name)
    generator.visit(tree)


    func_call = None 
    if  generator.func_found:
        #raise ValueError(f"Function {func_name} not found in the provided definition. ---:::: {func_def},------------>{arg_list}")
        # Generate the function call with the provided arguments
        class_name = generator.class_name
        arg_names = generator.arg_names
        arg_str_list = [f'{name}={value!r}' for name, value in zip(arg_names, arg_list)]

        if func_name is None and class_name:
            func_call = f'{class_name}().{func_name}(??)'
        elif arg_str_list is not None and len(arg_str_list)>0 :
            func_call = f'{func_name}(??)'

    if func_call is None :
        assert "*" in func_def or "lambda" in func_def, (func_def, func_name ) 
        func_call  =  f'{func_name}(??)' 


    if type(expected_output)==bool :
        expected_output_str = "not" if not expected_output else " "
        masked_input =  f"assert {expected_output_str} {func_call} "
    else:
        if is_compare_on_str_level :
            masked_input = f"assert json.dumps(({func_call})) == json.dumps(({expected_output!r}))"
        else:
            masked_input = f"assert {func_call} == {expected_output!r}"

    # Generate the function call with the provided arguments
    class_name = generator.class_name
    arg_names = generator.arg_names
    arg_str_list = [f'{name}={value!r}' for name, value in zip(arg_names, arg_list)]

    func_call = None 
    if  generator.func_found:
        #raise ValueError(f"Function {func_name} not found in the provided definition. ---:::: {func_def},------------>{arg_list}")
        # Generate the function call with the provided arguments
        class_name = generator.class_name
        arg_names = generator.arg_names
        arg_str_list = [f'{name}={value!r}' for name, value in zip(arg_names, arg_list)]

        if func_name is None and class_name:
            func_call = f'{class_name}().{func_name}({", ".join(arg_str_list)})'
        elif arg_str_list is not None and len(arg_str_list)>0 :
            func_call = f'{func_name}({", ".join(arg_str_list)})'

    if func_call is None :
        assert "*" in func_def or "lambda" in func_def, (func_def, func_name ) 
        func_call =express( func_name=func_name, arg_list=arg_list)# '{} ({}) '.format( func_name ,  args = ",".join(list(map(repr, rparg_list ) ) ) )

#    if class_name:
#        func_call = f'{class_name}().{func_name}({", ".join(arg_str_list)})'
#    else:
#        func_call = f'{func_name}({", ".join(arg_str_list)})'

    if type(expected_output)==bool :
        expected_output_str = "not" if not expected_output else " "
        masked_output = f"assert {expected_output_str} {func_call} "
    else:
        if is_compare_on_str_level :
            masked_output  = f"assert json.dumps(({func_call})) == json.dumps(( ?? )) " 
        else:
            masked_output  = f"assert {func_call} ==  ?? " 

    return {"masked_input":masked_input, "masked_output":masked_output}


def assert_input_output ( sample, first_solution,entry_point , is_compare_on_str_level=False  ):
    assert "input_output" in sample
    try :
        in_outs = json.loads(sample["input_output"])
    except ValueError:
        return None
    except TypeError:
        in_outs=  sample["input_output"]
        pass #return None
    except Exception as ex:
        raise 

    try  :
        xx = in_outs["inputs"][:20]
    except TypeError :
        assert sample["task_id"] == "Mbpp/793"
        return None 
        
    tpl_list = []

    # try :
    #     in_outs["inputs"] [:20]
    # except TypeError :
    #     print ( sample )
    #     print (type( in_outs["inputs"] ), "--->", in_outs["inputs"] )
    #     print ( in_outs )
    # for index, inputs in enumerate(in_outs["inputs"] [:20]) :
    for index, inputs in enumerate(in_outs["inputs"] ) :
        # try:
        #     if isinstance(inputs[0], dict):
        #         inputs = [{int(k): v for k,v in inputs[0].items()}]
        #         in_outs["inputs"][index] = inputs 
        #         #print ("333"*8 )
        # except:
        #     True
        # try:
        #     if isinstance(in_outs["outputs"][index], dict):
        #         in_outs["outputs"][index] = [{int(k): v for k,v in in_outs["outputs"][index].items()}]
        #         #print ("1111"*8 )
        # except:
        #     True
        # try:
        #     if isinstance(in_outs["outputs"][index][0], dict):
        #         in_outs["outputs"][index] = [{int(k): v for k,v in in_outs["outputs"][index][0].items()}]
        #         #print ("222"*8 )
        # except:
        #     True

        # if isinstance(in_outs["outputs"][index], list) and in_outs["outputs"][index]:
        #     # expect_output = in_outs["outputs"][index][0]
        #     #print ("444"*8 )
        # else:
        expect_output = in_outs["outputs"][index]
            #print ("555"*8 )
        #expect_output = in_outs["outputs"][index]


        ass_truth_info =_generate_assert_statement(func_def=first_solution, func_name=entry_point, arg_list=inputs, expected_output=expect_output, is_compare_on_str_level =is_compare_on_str_level )
        ass_info =_generate_masked_assert_statement(func_def=first_solution, func_name=entry_point, arg_list=inputs, expected_output=expect_output , is_compare_on_str_level= is_compare_on_str_level )
        ass_truth_info.update( ass_info )
        tpl_list.append( ass_truth_info )# {**ass_info, "assert_truth":ass_truth } )#"assert1":ass_1, "assert2":ass_2} )


    return tpl_list 


