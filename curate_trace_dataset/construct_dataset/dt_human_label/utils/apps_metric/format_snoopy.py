import os 
import json 
import re 

import pprint 

from collections import defaultdict
import random 

from copy import deepcopy 
# def accumulate_line_no( trace_list ):
#     d2 = defaultdict(list)
#     for index,  item in enumerate(trace_list):
#         k = item ["line_no"]
#         v= item["return"] if "return" in item  else item["var"] 
#
#         d2[k] += [ "({}) {}".format(index,v)  ]
#     return d2 

def accumulate_line_no( trace_list ):
    d2 = defaultdict(list)
    for index,  item in enumerate(trace_list):
        k = item ["line_no"]
        # v= item["return"] if "return" in item  else item["var"] 
        if "var" not in item :
            # if "return" in item :
            #     d2[k]= [item["return"]]
            # if "except" in item :
            #     d2[k]= [item["except"] ]
            continue 
        v= item["var"]
        d2[k] +=[v] #[ "({}) {}".format(index,v)  ]
    return d2 


def clip_long_list(trace_list: defaultdict ):
    new_cliped = defaultdict(list)
    for k,v in trace_list.items ():
        assert type(v)==list 
        if len(v)>3 :
            new_v = v[:2]+["..."]+v[-1:]
            new_v = ["; ".join(new_v)]
        else :
            new_v = v 
        
        new_cliped [k] =new_v 
    return new_cliped 
  
        
def align_trace( lines ):
    new_lines = []
    for i in range( len(lines)):
        line_x  = lines[i  ]  
        nex_l = min( i+1 , len(lines)-1 )
        nex_line = lines[nex_l ]  
        
        # print ( "--->", any( [nex_line.startswith( x) for x in [xstart,x_var,x_var1] ] ) , line_x[len(xstart)] , nex_line[len(xstart):], "----" )
        if any( [nex_line.startswith( x) for x in [xstart,x_var,x_var1] ] ) and line_x[:len(xstart)]==nex_line[:len(xstart)]:
            lines[ nex_l  ] =   nex_line + ", " +  line_x[len(xstart):]
        else:
            new_lines.append( line_x )

    return "\n".join( new_lines )


y_list=[
    "line ",
    "return ",
    "call ",
    "exception",
    ]
xstart     = 'Starting var:.. '
x_var      = 'New var:....... ' 
x_var1     = 'Modified var:.. ' 
x_return   = 'Return value:.. '

x_nochange = 'NOCHABE:....... '

x_wated_list=[
    "Elapsed time: ",
    "Source path:...",
    "Exception:.....",
    "Call ended by",
    "NOCHABE:....... ",
    ]

def clear_any_illegal_line_from_recurisive_depth(xstr ):
    xstr_trim = xstr.strip()
    pattern = re.compile(is_testcase_prefix_start)
    
    x_list = [xstart, x_var,x_var1,x_return]+x_wated_list
    
    p_list = []
    for iiy, line in enumerate( xstr_trim.splitlines(keepends=False) ) :
        if not pattern.match( line ):
            continue
        p_list.append( line )
        
    def remove_items_by_indices(input_list, indices_to_remove):
        # Sort the indices to ensure they are in ascending order
        indices_to_remove.sort(key=lambda x: x[0])
        
        # Check if the indices are valid
        for start, end in indices_to_remove:
            if start < 0 or end >= len(input_list) or start > end:
                print("Invalid indices provided:", (start, end))
                return input_list
        
        # Initialize the result list
        result = []
        
        # Iterate over the original list and skip items within the specified ranges
        index = 0
        for start, end in indices_to_remove:
            result.extend(input_list[index:start])
            index = end + 1
        
        # Add remaining items after the last removed segment
        result.extend(input_list[index:])
        
        return result
    
    # print ( "\n\n\np_list", p_list )
    def is_external_source( p_list, span_list=[0,4,8,12,16] ):
        #"Source path:... "
        #"Source path:... <string>"
        flg = False 
        i_start = None 
        i_end = None 
        remove_list = []
        
        flg2 = False 
        flg2_2 = False 
        i2_start = None 
        i2_end = None 
        remove2_list = []
        
        
        trim_p_list = []
        for iiy, p in enumerate(p_list) :
            for one_span in span_list :
                head1 = p[len("t_000001"+(" "*one_span)):] 
                head2 = p[len("t_000001"+(" "*16+" "*one_span)):] 
                head2_2 = p[len("t_000001"+(" "*one_span)):] 
                if any( [head1.startswith(x) for x in x_list] ):
                    break 
                if any( [head2.startswith(x) for x in y_list] ) :
                    break 
                    
            trim_p_list.append(head1 ) 
            # print (head1,"???" )
            if head1.startswith("Source path:... ") and "Source path:... <string>" not in head1 :
                flg = True 
                i_start = iiy 
            p_hat = head1.strip() 
            p2_hat = head2.strip() 
            
            if p_hat.startswith("Return value:..") and flg :
                i_end = iiy
                remove_list.append( (i_start,i_end) )
                flg , i_start,i_end = False, None , None 


            if head1.startswith("Source path:... ") and "Source path:... <string>"  in head1 :
                flg2 = True 
                i2_start = iiy 
            
            if flg2 and any([p2_hat.startswith(v) for v in y_list ]) :
                if  (not p2_hat .endswith("SOURCE IS UNAVAILABLE") ):
                    flg2_2 = True 
                else:
                    flg2 = False   
                    flg2_2 = False 
                    
            if p_hat.startswith("Return value:..") and flg2 and flg2_2 :
                i2_end = iiy
                remove2_list.append( (i2_start,i2_end) )
                flg2,flg2_2 , i2_start,i2_end = False,False, None , None 
                # pprint.pprint ( p_list[i2_start:i2_end])

        # print ("======remove2_list====", remove2_list, p_list[3:9+1] )

        assert len(p_list)==len(trim_p_list), ( len(p_list),  len(trim_p_list) )
        
        # print ({"remove_list":remove_list, "remove2_list":remove2_list})
        # return remove_list+remove2_list, trim_p_list
        return remove_list+remove2_list, trim_p_list

    remove_list,trim_p_list = is_external_source( p_list )
    
    new_p_list = remove_items_by_indices( input_list=p_list, indices_to_remove=remove_list )
    trim_p_list = remove_items_by_indices( input_list=trim_p_list, indices_to_remove=remove_list )
            
    return "\n".join(new_p_list ), "\n".join(trim_p_list ) # raw clear 
    # pprint.pprint (p_list) 
    


        
is_testcase_prefix_start=r"^(?P<case_id>t_\d{6,})"


def extract_case_id( trace_str:str ):
    def match_first ( xstr ) :
        xmatch = re.search(is_testcase_prefix_start, xstr )
        if xmatch :
            xm =  xmatch.groupdict()
            return xm["case_id"]
        return None 
        
    trace_str_list = trace_str.splitlines(keepends=False)
    test_id_list = list( set( [match_first(xstr = x ) for x in trace_str_list] )) 
    # print (test_id_list,"test_id_list")
    test_id_list = [x for x in test_id_list if x is not None and x.startswith("t_") ]
    # if None in test_id_list:
    #     return None 
    assert None not in test_id_list  ,  ( test_id_list ,trace_str_list  )
    tra_info = {}
    # print ("test_id_list", test_id_list )
    
    for one_test_id in  test_id_list:
        # trace_str = [x[len(one_test_id):]  for x in trace_str_list if x.startswith(one_test_id) ]
        trace_str = [x  for x in trace_str_list if x.startswith(one_test_id) ]
        
        trace_str = "\n".join(trace_str)
        tra_info [ one_test_id ]= trace_str
        
    return tra_info

    
def paste_code_with_commented_trace( code_raw , trace_dict, **kwargs  ):
    max_line  = max( list(trace_dict) )
    
    trace_id = kwargs.get("trace_id", None )
    code_list = code_raw.split("\n")
    
    if max_line > len(code_list ):
        return  None 
    assert max_line <= len(code_list ),  ( dict (code_len = len(code_list), max_line=max_line ,trace_dict=trace_dict, line_list= list(trace_dict) , trace_id=trace_id  ))
    for i  in range( len(code_list)  ) :
        
        line_no = i+1 
        if line_no in trace_dict :
            comments = trace_dict[  line_no ]
            comments = "; ".join( comments )
            code_list[ i  ] = code_list[ i  ]  +" #" +  comments 
        
    code_new_str = "\n".join( code_list )
    
    return code_new_str 


     
     
def format_trace( trace_str:str , code_shift_size: int = 0 , **kwargs  ): 
    raw_trace_str = trace_str 
    trace_info = extract_case_id(trace_str = trace_str )
    # print (trace_info)
    trace_info_raw = {}
    for one_test_id,trace_str in trace_info.items():
        _, trace_str = clear_any_illegal_line_from_recurisive_depth(trace_str)
        
        assert  trace_str is not None and len(trace_str) > 0 , (one_test_id,  trace_str , trace_str_list )
        trace_raw_info  = _format_trace_nochange ( trace_str=trace_str,  code_shift_size=code_shift_size ,raw_trace_str=raw_trace_str , **kwargs )
        if trace_raw_info is None :
            continue 
        # print ( trace_str,"\n\n\n\n\n\n\n",trace_raw_info  )
        # exit()
        trace_info_raw [ one_test_id ]= trace_raw_info
        
    return  trace_info_raw 




def _format_trace_nochange( trace_str:str ,  code_shift_size: int = 0 , **kwargs ): 
    
    
    
    if type(trace_str)==bytes :
        trace_str = trace_str.decode("utf-8")
    
    code_shift_size = int(code_shift_size)
    
        
    assert type(trace_str) == str  and len(trace_str)>0 
    lines = trace_str.splitlines(keepends=False)

    
    aligned_trace_str = align_trace( lines =lines  )
    # print (aligned_trace_str )
    lines = aligned_trace_str.splitlines(keepends=False)
    
    # print ("_format_trace,line ", len(lines),lines[:50] )
    
    pattern_line   = r"^\s{1,}[line|call|exception|return]+\s{1,}(?P<line_no>\d+)\s{1,}\w+"
    pattern_return = r"^\s{1,}return\s{1,}(?P<line_no>\d+)\s{1,}\w+"
    
    def remove_unwated(lines):
        #  Elapsed time: 00
        #('Source path:... <string>\n' 
        lines =[line for line in lines if (not  line.startswith("Elapsed time: ") ) and ( not  line.startswith("Source path:.")  ) ]
        return lines 
    
    
    def extract_line_no(line, x_pattern = pattern_line  ):
        match = re.search(x_pattern, line )
        if match :
            xm =  match.groupdict()
            return int( xm["line_no"])
        
        return None 

    
    # trace_info = []
    
    
    # lines = remove_unwated( lines )
    ix, max_v,mix_v  =  len(lines)-1,0 ,10000000000
    is_collect = lambda x: not x.startswith("                ")
    is_start = lambda x:  x.lstrip().startswith("Starting var:")
    # or x.startswith("Elapsed time:")
    is_end_except = lambda x:  x.lower().lstrip().startswith("exception:.....")  
    is_end  = lambda x: x.lstrip().startswith("Return value:")
    is_var = lambda x:  x.lstrip().startswith("New var:") or  x.startswith("Modified var:") 
    is_nochange = lambda x:  x.lstrip().startswith("NOCHABE:....... ")
    
    lines = lines[::-1]
    stack = defaultdict(list)
    trace_info = defaultdict(list)

    exception_list = []
    flag = "starting"

    already_print = False 
    
    cur_line_no = [pre_line for pre_line in lines if not any([is_collect(pre_line) \
                   or is_collect(pre_line) or is_end_except(pre_line) or \
                   is_end(pre_line) or is_var(pre_line) or \
                   is_nochange(pre_line)  ]  ) ] 
    cur_line_no = extract_line_no(cur_line_no[-1] )
    if cur_line_no is None :
        return None 
    assert  cur_line_no is not None  
    # print ( "\n".join(cur_line_no) ,"!!!")
    # exit()
    total_line = ix -1
    
    while ix >=0:
        # flag = None 
        line = lines[ix]
        # print ("line", line, "----", flag)
        if line.startswith ("Source path:") or line.startswith ("Elapsed time:") or line.startswith("Call ended by exception"):
            ix -=1 
            continue 
        
        cur_line_no_pre = cur_line_no  
        cur_line_no =cur_line_no_pre  if  extract_line_no(line )  is None else extract_line_no(line ) 

        if is_start(line):
            flag = "starting"
            ix -=1 
            # print ("stack[flag ]", type(stack[flag ]) , type(stack), stack )
            trace_info[flag ].append( {"line_no": cur_line_no, flag:line , "order_id":total_line-ix } )
            continue

        if is_end(line):
            flag = "end"
            ix -=1 
            trace_info[flag ].append( {"line_no": cur_line_no, flag:line , "order_id":total_line-ix } )
            continue

        if is_end_except(line):
            flag = "except"
            ix -=1 
            trace_info[flag ].append( {"line_no": cur_line_no, flag:line , "order_id":total_line-ix } )
            # exception_list.append( ix  )
            continue

        if is_nochange(line):
            flag = "nochange"
            ix -=1 
            trace_info[flag ].append( {"line_no": cur_line_no, flag:line , "order_id":total_line-ix } )
            # exception_list.append( ix  )
            continue

        if is_var(line):
            flag = "var"
            ix -=1 
            trace_info[flag ].append( {"line_no": cur_line_no, flag:line , "order_id":total_line-ix } )
            continue

        ix-=1 
    
    assert len(trace_info)>0 , (trace_info, )
    # pprint.pprint  ( trace_info )
    
    
    for trace_info_sub in list( trace_info.values() ):
        assert min( [int(x["line_no"]) for x in trace_info_sub]) >=code_shift_size , (dict(code_shift_size=code_shift_size,trace_info=trace_info ))
    ##
    #calibrate the shift 
    for key in list(trace_info.keys() ) :
        trace_info_sub = trace_info[key]
        for i in range( len(trace_info_sub) ) :
            trace_info[key][i] ["line_no"] = max(0, trace_info_sub[i] ["line_no"] -code_shift_size )
    
    
    return trace_info 
    
    # trace_dict = accumulate_line_no ( trace_list = trace_info_raw )
    # trace_dict_cliped  = clip_long_list( trace_list =trace_dict  )
    #
    # return trace_dict_cliped , copy_trace_info 

    
