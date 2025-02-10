# from abc import ABC
import abc 
from collections import defaultdict 
import textwrap
import random
import traceback


def paste_code_with_commented_trace( code_raw , trace_dict, **kwargs  ):
    max_line  = max( list(trace_dict) )
    
    trace_id = kwargs.get("trace_id", None )
    code_list = code_raw.split("\n")
    
    # print ("trace_dict", type(trace_dict), )
    # print ("trace_dict.list", list(trace_dict) )
    if max_line > len(code_list ):
        return  None 
    assert max_line <= len(code_list ),  ( dict (code_len = len(code_list), max_line=max_line ,trace_dict=trace_dict, line_list= list(trace_dict) , trace_id=trace_id  ))
    for i  in range( len(code_list)  ) :
        
        line_no = i+1 
        if line_no in trace_dict :
            comments = trace_dict[  line_no ]
            # comments = "; ".join( comments )
            code_list[ i  ] = code_list[ i  ]  +" #" +  str(comments) 
        
    code_new_str = "\n".join( code_list )
    
    return code_new_str 


     
     
     
class TPL(metaclass=abc.ABCMeta):
    
    
    @abc.abstractmethod
    def format(self,code, lines ,**kwargs ):
        pass 
    
    def accumulate_line_no(self, lines ):
        
        # print ("lines", lines )
        lines = [x.__dict__() for x in lines ]
        # print ( lines , "lines")
        uniq_line_no_list = [x["line_no"] for x in lines ] 
        uniq_line_no_list = list(set( uniq_line_no_list ))
        
        
        accumulate_lines = {}
        for one_line_no in uniq_line_no_list :
            lines_same = [x  for x in lines  if x["line_no"]   ==one_line_no  ]
            lines_same = [ "({}) {}".format( x["order_id"],  x["var"]  )  for x in lines_same ] 
            accumulate_lines [ one_line_no ]= lines_same
        
        return accumulate_lines
        
    
    
            
    def align_trace(self, lines ):
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
    

map_dict_string = lambda  y:", ".join( [ "{}={}".format(k.replace("@",""),v ) for k,v in y.items() ] )


class TPL_CODEEXECUTOR( TPL ):

        
    # def format(self,code, lines ,**kwargs ):
    #     lines = self.accumulate_line_no( lines ) 
    #     lines = "\n".join(lines )
    #     return lines 
    def format(self,code, lines ,**kwargs ):
        trace_dict = self.accumulate_line_no( lines ) 
        assert type(trace_dict)== dict, ( type(trace_dict), trace_dict )

        code_str = paste_code_with_commented_trace( code_raw=code, trace_dict= trace_dict )        
        return code_str 


    def init(self, code, lines=None, meta_info=None ):
        self.buggy_code = code 
    
    

    def accumulate_format(self, trace_grp ):

        meta_list = []
        trace_list = []
        code_str = self.buggy_code 

        for i,(_, trace) in enumerate(trace_grp.items() ):
            if i > MAX_LEN : 
                continue 
            meta_list.append( trace._meta_info )
            lines = trace._states 
            trace_list.extend(  self.accumulate_line_no( lines ) )
            # trace_list_str = "\n".join( trace_list )
            #trace_list.append( trace_dict )
            # code_str = paste_code_with_commented_trace( code_raw=code_str, trace_dict= trace_dict )


        template_stringi_testcase="""
**TEST{{idx}}**

input{{idx}}='{{input1}}'

expect_output{{idx}}='{{output1}}'

"""
        str_testcase_list,str_trace_list = [],[]
        for idx , meta_info in enumerate( meta_list ):

            tpl_inx_out =  Template( template_stringi_testcase )
            #wrap_func( extract_inx_oux
            str_case = tpl_inx_out.render( idx=idx+1,
                    input1=wrap_func( extract_inx_oux( meta_info["true_input"])),
                    output1=wrap_func( extract_inx_oux( meta_info["expect_output"] )), 
            )
            str_testcase_list += [str_case]


        template_stringi_buggy="""
## Trace 

**BUGGY_PROGRAM**

```python
{{buggy_code}}
```

## TESTCASES 

{{TESTCASES}}

## EXPLANATION 

{{TRACE_STR}}
"""

        render_info  = {
                "buggy_code":code_str ,
                "TESTCASES":"\n".join( str_testcase_list[:MAX_LEN ]),
                "TRACE_STR":"\n".join( trace_list ),
                }
        template = Template( template_stringi_buggy )
        rendered_string = template.render( **render_info )

        return rendered_string #code_str #format_str 


    def accumulate_line_no(self, lines ):
        
        lines = [x.__dict__() for x in lines ]

        lines_output = [( x["line_no"], x["var"]["@exception"] ) for x in lines if "var" in x and  "@exception" in x["var"] ]
        lines_output += [ ( x["line_no"], x["var"]["@return"] ) for x in lines if "var" in x and  "@return" in x["var"] ]

        lines_output = [ {"lo":x, "xstr": "<output>{}".format( y  ) }  for x,y in lines_output ] 

        
        lines_same = [{"line_no":x["line_no"], "var": "<dictsep>".join(x["var"]["locals"] ) }  for x in lines   if "locals" in x["var"] ] 
        lines_same = [{"line_no":x["line_no"], "var": "<dictsep>".join(x["var"]["locals"] ) }  for x in lines   if "locals" in x["var"] ] 
        # lines_same = [(x["line_no"],  "<line> <{}> <state>{}</state>".format( x["line_no"],  x["var"]  ) )  for x in lines_same ] 

        lines_same = [ {"lo": x["line_no"], "xstr": "<line> <{}> <state>{}</state>".format( x["line_no"],  x["var"]  ) }  for x in lines_same ] 
        lines_same+=lines_output
        
        
        
        lines_same_list = [ x["xstr"] for x in lines_same ]
        # final_lines = defaultdict(list)
        # for line_item   in lines_same :
        #     # print ( line_item , "line_item..." )#, "....xpp...", type(lineno) )
        #     lineno,line_str  = line_item["lo"], line_item["xstr"]
        #     # print ( lineno , "....xpp...", type(lineno) )
        #     # lineno,line_str
        #     assert type(lineno) == int , (type(lineno), lineno,  lines_same)
        #     final_lines[lineno ].append( line_str )
        #
        # final_ret = {}
        # for k,v in final_lines.items():
        #     vstr = " ".join(v)
        #     final_ret[ k ] = vstr 
            
        return lines_same_list
        
        
                
class TPL_CONCISETRACE( TPL ):
    
    # def format(self,code, lines ,**kwargs ):
    #     lines = self.accumulate_line_no( lines ) 
    #
    #     lines = "\n".join( lines )
    #     return lines 
    def format(self,code, lines ,**kwargs ):
        trace_dict = self.accumulate_line_no( lines ) 
        assert type(trace_dict)== dict, ( type(trace_dict), trace_dict )

        code_str = paste_code_with_commented_trace( code_raw=code, trace_dict= trace_dict )        
        return code_str 

    
    def init(self, code, lines=None, meta_info=None ):
        self.buggy_code = code 
        
        
    def accumulate_line_no(self, lines ):
        #
        lines = [x.__dict__() for x in lines ]
        # print ( lines )
        # exit()
        lines_input = [( x["line_no"], x["var"]["@init"] ) for x in lines if "var" in x and  "@init" in x["var"]  ]
        lines_input = [ {"lo":x , "xstr":"[L{}] [INPUT] {} [/INPUT] [/L{}]".format( x,y,x  ) }  for x,y in lines_input ] 

        lines_output = [( x["line_no"], x["var"]["@exception"] ) for x in lines if "var" in x and  "@exception" in x["var"] ]
        lines_output += [( x["line_no"], x["var"]["@return"] ) for x in lines if "var" in x and  "@return" in x["var"] ]

        lines_output = [{"lo":x, "xstr":"[L{}] [OUTPUT] {} [/OUTPUT] [/L{}]".format( x,y,x  ) }  for x,y in lines_output ] 

        
        lines_same = [{"line_no":x["line_no"], "var": ",".join(x["var"]["locals"] ) }  for x in lines   if "locals" in x["var"] ] 
        lines_same = [{"lo":x["line_no"],"xstr": "[L{}] {} [/L{}]".format( x["line_no"],  x["var"], x["line_no"]  ) }  for x in lines_same ] 
        
        lines_same =lines_input+lines_same+lines_output
        
        # final_lines = defaultdict(list)
        # for line_item   in lines_same :
        #     # print ( line_item , "line_item..." )#, "....xpp...", type(lineno) )
        #     lineno,line_str  = line_item["lo"], line_item["xstr"]
        #     # print ( lineno , "....xpp...", type(lineno) )
        #     # lineno,line_str
        #     assert type(lineno) == int , (type(lineno), lineno,  lines_same)
        #     final_lines[lineno ].append( line_str )
        #
        # final_ret = {}
        # for k,v in final_lines.items():
        #     vstr = " ".join(v)
        #     final_ret[ k ] = vstr 
        lines_same = [ x["xstr"] for x in lines_same ]
            
        return lines_same
        
    def accumulate_format(self, trace_grp ):

        meta_list = []
        trace_list = []
        code_str = self.buggy_code 

        for i,(_, trace) in enumerate(trace_grp.items() ):
            if i > MAX_LEN : 
                continue 
            meta_list.append( trace._meta_info )
            lines = trace._states 
            trace_list.extend(   self.accumulate_line_no( lines ) )
            #trace_list.append( trace_dict )
            # code_str = paste_code_with_commented_trace( code_raw=code_str, trace_dict= trace_dict )


        template_stringi_testcase="""
**TEST{{idx}}**

input{{idx}}='{{input1}}'

expect_output{{idx}}='{{output1}}'

"""
        str_testcase_list,str_trace_list = [],[]
        for idx , meta_info in enumerate( meta_list ):

            tpl_inx_out =  Template( template_stringi_testcase )
            #wrap_func( extract_inx_oux
            str_case = tpl_inx_out.render( idx=idx+1,
                    input1=wrap_func( extract_inx_oux( meta_info["true_input"])),
                    output1=wrap_func( extract_inx_oux( meta_info["expect_output"] )), 
            )
            str_testcase_list += [str_case]


        template_stringi_buggy="""
## Trace 

**BUGGY_PROGRAM**

```python
{{buggy_code}}
```

## TESTCASES 

{{TESTCASES}}

## EXPLANATION

{{TRACE_STR}}
"""

        render_info  = {
                "buggy_code":code_str ,
                "TESTCASES":"\n".join( str_testcase_list[:MAX_LEN ]),
                "TRACE_STR":"\n".join( trace_list ),
                }
        template = Template( template_stringi_buggy )
        rendered_string = template.render( **render_info )

        return rendered_string #code_str #format_str 





class TPL_NEXT( TPL ):
    def format(self,code, lines ,**kwargs ):
        trace_dict = self.accumulate_line_no( lines ) 
        assert type(trace_dict)== dict, ( type(trace_dict), trace_dict )

        code_str = paste_code_with_commented_trace( code_raw=code, trace_dict= trace_dict )        
        return code_str 
    

    def init(self, code, lines=None, meta_info=None ):
        self.buggy_code = code 

    def accumulate_format(self, trace_grp ):

        meta_list = []
        trace_list = []
        code_str = self.buggy_code 

        for i,(_, trace) in enumerate(trace_grp.items() ):
            if i > MAX_LEN : 
                continue 
            meta_list.append( trace._meta_info )
            lines = trace._states 
            trace_dict = self.accumulate_line_no( lines )
            #trace_list.append( trace_dict )
            code_str = paste_code_with_commented_trace( code_raw=code_str, trace_dict= trace_dict )


        template_stringi_testcase="""
**TEST{{idx}}**

input{{idx}}='{{input1}}'

expect_output{{idx}}='{{output1}}'

"""
        str_testcase_list,str_trace_list = [],[]
        for idx , meta_info in enumerate( meta_list ):

            tpl_inx_out =  Template( template_stringi_testcase )
            #wrap_func( extract_inx_oux
            str_case = tpl_inx_out.render( idx=idx+1,
                    input1=wrap_func( extract_inx_oux( meta_info["true_input"])),
                    output1=wrap_func( extract_inx_oux( meta_info["expect_output"] )), 
            )
            str_testcase_list += [str_case]


        template_stringi_buggy="""
## Trace 

**BUGGY_PROGRAM**

```python
{{buggy_code}}
```

## TESTCASES 

{{TESTCASES}}

"""

        render_info  = {
                "buggy_code":code_str ,
                "TESTCASES":"\n".join( str_testcase_list[:MAX_LEN ]),
                }
        template = Template( template_stringi_buggy )
        rendered_string = template.render( **render_info )

        return rendered_string #code_str #format_str 




    
    def accumulate_line_no(self, lines ):
        
        def clip_long_list( trace_list: defaultdict ):
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


        # print ("lines", lines )
        lines = [x.__dict__() for x in lines ]
        # print ( lines , "lines")
        uniq_line_no_list = [x["line_no"] for x in lines ] 
        uniq_line_no_list = list(set( uniq_line_no_list ))
        
        
        accumulate_lines = {}
        for one_line_no in uniq_line_no_list :
            lines_same = [x  for x in lines  if x["line_no"]   ==one_line_no  ]
            lines_same = [ "({}) {}".format( x["order_id"],  x["var"]["locals"]  )  for x in lines_same  if "locals" in x["var"] ] 
            accumulate_lines [ one_line_no ]= lines_same
        
        for one_line_no in uniq_line_no_list :
            lines_same = [x  for x in lines  if x["line_no"]   ==one_line_no  ]
            lines_same = [ "({}) {}".format( x["order_id"],  x["var"]["@init"]  )  for x in lines_same  if "@init" in x["var"] ] 
            if len(lines_same)>0:
                accumulate_lines [ one_line_no ]= lines_same
        
        
        for one_line_no in uniq_line_no_list :
            lines_same = [x  for x in lines  if x["line_no"]   ==one_line_no  ]
            lines_same = [ "__return__={}".format(   x["var"]["@exception"] if "@exception" in x["var"] else x["var"]["@return"]  )  for x in lines_same  if ( "@exception" in x["var"] or  "@return" in x["var"]) ] 
            if len(lines_same)>0:
                accumulate_lines [ one_line_no ]= lines_same
        

        accumulate_lines = clip_long_list( accumulate_lines )
        accumulate_lines = {x: " ".join(y) if type(y)==list else y  for x ,y in accumulate_lines.items() }
        
        return dict(accumulate_lines)
        
        return accumulate_lines
        
      


class TPL_SCRATCHPAD( TPL ):
    def format(self,code, lines , **kwargs ):
        trace_dict = self.accumulate_line_no( lines ) 
        assert type(trace_dict)== dict 

        code_str = paste_code_with_commented_trace( code_raw=code, trace_dict= trace_dict )        
        return code_str 
        
    def accumulate_line_no(self, lines ):
        
        # print ("lines", lines )
        lines = [x.__dict__() for x in lines ]
        # print ( lines , "lines")
        uniq_line_no_list = [x["line_no"] for x in lines ] 
        uniq_line_no_list = list(set( uniq_line_no_list ))
        
        
        accumulate_lines = {}
        for one_line_no in uniq_line_no_list :
            lines_same = [x  for x in lines  if x["line_no"]   ==one_line_no  ]
            lines_same = [ "[STATE] {} [/STATE]".format(  x["var"]["locals"]  )  for x in lines_same  if "locals" in x["var"] ] 
            accumulate_lines [ one_line_no ]= " ".join( lines_same )
        
        for one_line_no in uniq_line_no_list :
            lines_same = [x  for x in lines  if x["line_no"]   ==one_line_no  ]
            lines_same = [ "[INPUT] {} [/INPUT]".format(  x["var"]["@init"]  )  for x in lines_same  if "@init" in x["var"] ] 
            if len(lines_same)>0:
                accumulate_lines [ one_line_no ]= " ".join( lines_same )
        
        
        for one_line_no in uniq_line_no_list :
            lines_same = [x  for x in lines  if x["line_no"]   ==one_line_no  ]
            lines_same = [ "[OUTPUT] {} [/OUTPUT]".format(  x["var"]["@exception"] if "@exception" in x["var"] else x["var"]["@return"]  )  for x in lines_same  if ( "@exception" in x["var"] or  "@return" in x["var"]) ] 
            if len(lines_same)>0:
                accumulate_lines [ one_line_no ]= " ".join( lines_same )
        

        
        return accumulate_lines
        
      

class TPL_SEMCODER( TPL ):
    
    pass 


MAX_LEN = 3

from jinja2 import Template

wrap_func = lambda x: "{}".format( textwrap.wrap( f"{x!r}", width=100)[0] )#, placeholder="...")
def extract_inx_oux ( inx ):
    if type( inx ) in [list,tuple ]  and len(inx)>0 :
        inx= str(inx)
        return inx[1:-1]
    if type(inx) in [str,dict,float,int]:
        return inx 
    return inx 

class TPL_OUR01( TPL ):
    def format(self,code, lines, meta_info , **kwargs  ):
        trace_dict = self.accumulate_line_no( lines ) 
        assert type(trace_dict)== dict, ( type(trace_dict), trace_dict )
        sorted_trace_dict  = dict(sorted( trace_dict.items()) )

        #code_str = paste_code_with_commented_trace( code_raw=code, trace_dict= trace_dict )        
        code_str = self._build_trace_expr( code=code, meta_info =meta_info , sorted_trace_dict = sorted_trace_dict  )
        return code_str 


    def init(self, code, lines=None, meta_info=None ):
        self.buggy_code = code 

    def accumulate_format(self, trace_grp ):

        meta_list = []
        trace_list = []
        # print ( trace_grp ,"-----"*8 )
        for _, trace in trace_grp.items() :
            meta_list.append( trace._meta_info )
            lines = trace._states 
            trace_dict = self.accumulate_line_no( lines )
            trace_list.append( trace_dict )

        format_str = self._build_trace_expr_accumulate( code=self.buggy_code  ,  meta_info_list= meta_list , trace_list = trace_list )
        return format_str 




    def _build_trace_expr_accumulate(self,code,  meta_info_list, trace_list  ):


        for i in  range(len(trace_list)):
            trace_dict = trace_list[i]
            sorted_trace_dict  = dict(sorted( trace_dict.items()) )
            trace_str =[ "line {}: {}".format( k,v if type(v)!=list else " ".join(v)  ) for k,v in sorted_trace_dict.items() ]
            trace_str = "\n* ".join( trace_str ) 
            trace_list[i] = "* "+trace_str 


        template_stringi_testcase="""
**TEST{{idx}}**

input{{idx}}={{input1}}

expect_output{{idx}}={{output1}}

"""
        template_stringi_explan="""
**TEST{{idx}}_RESULT**

{{trace1}}
  
TEST{{idx}}_BUGGY_PROGRAM_OUTPUT = execute (BUGGY_PROGRAM, input{{idx}}) = "{{output1_err}}"    

**FAILED** 

assert TEST{{idx}}_BUGGY_PROGRAM_OUTPUT == expect_output{{idx}} is False 


TEST{{idx}} failed in BUGGY_PROGRAM 
"""
        str_testcase_list,str_trace_list = [],[]
        for idx , meta_info in enumerate( meta_info_list ):
            cur_trace = trace_list[idx]

            tpl_inx_out =  Template( template_stringi_testcase )
            str_case = tpl_inx_out.render( idx=idx+1,input1=wrap_func( extract_inx_oux(meta_info["true_input"])) ,output1= wrap_func( extract_inx_oux( meta_info["expect_output"] ) ) )
            str_testcase_list += [str_case]

            tpl_trace =  Template( template_stringi_explan )
            str_trace = tpl_trace.render( idx=idx+1, trace1 =cur_trace ,output1_err=wrap_func( meta_info["true_output"] ) )
            str_trace_list += [str_trace]

        template_stringi_buggy="""
## Trace 

**BUGGY_PROGRAM**

```python
{{buggy_code}}
```

## TESTCASES 

{{TESTCASES}}

## EXPLANATION

{{EXPLANATION}}

"""
        seed=  random.randint(0,1000)
        random.seed( seed )
        random.shuffle( str_testcase_list )
        random.seed( seed )
        random.shuffle( str_trace_list )

        render_info  = {
                "buggy_code":code ,
                "TESTCASES":"\n".join( str_testcase_list[:MAX_LEN ]),
                "EXPLANATION" :"\n".join( str_trace_list[:MAX_LEN ] ) 
                }
        template = Template( template_stringi_buggy )
        rendered_string = template.render( **render_info )
        return rendered_string 

    def _build_trace_expr(self, code, meta_info , sorted_trace_dict ):
        template_string="""
#### Trace 

**BUGGY_PROGRAM**

```python
{{buggy_code}}
```

#### TESTCASES 

**TEST1** 

input1='{{input1}}'
expect_output1='{{output1}}'

	
#### EXPLANATION

**TEST1_RESULT**

{{trace1}}
  
TEST1_BUGGY_PROGRAM_OUTPUT = execute (BUGGY_PROGRAM, input1) = "{{output1_err}}"    

**FAILED** 

assert TEST1_BUGGY_PROGRAM_OUTPUT == expect_output1 is False 

TEST1 failed in BUGGY_PROGRAM 

"""
        trace_str =[ "line {}: {}".format( k,v if type(v)!=list else " ".join(v)  ) for k,v in sorted_trace_dict.items() ]
        trace_str = "\n* ".join( trace_str ) 

        render_info  = {"buggy_code":code , "input1":meta_info ["true_input"] , "output1":wrap_func(meta_info ["expect_output"]) 
                , "output1_err":wrap_func(meta_info ["true_output"]) , "trace1":trace_str } 

        template = Template(template_string)
        rendered_string = template.render( **render_info )
        return rendered_string 

    
    def accumulate_line_no(self, lines ):
        
        def clip_long_list( trace_list: defaultdict ):
            new_cliped = defaultdict(list)
            for k,v in trace_list.items ():
                assert type(v)==list 
                if len(v)>3 :
                    new_v = v[:2]+["..."]+v[-1:]
                    new_v = ["; ".join(new_v)]
                else :
                    new_v = v 
                
                new_cliped [k] =" ".join( new_v  ) if type(new_v) in [list,tuple] else str(new_v) 
            return new_cliped 


        # print ("lines", lines )
        lines = [x.__dict__() for x in lines ]
        # print ( lines , "lines")
        uniq_line_no_list = [x["line_no"] for x in lines ] 
        uniq_line_no_list = list(set( uniq_line_no_list ))
        
        def expr_str(v):
            return " ".join(v) if type(v) in [list,tuple] else str(v)
        accumulate_lines = {}
        for one_line_no in uniq_line_no_list :
            lines_same = [x  for x in lines  if x["line_no"]   ==one_line_no  ]
            lines_same = [ "({}) {}".format( x["order_id"], expr_str( x["var"]["locals"])  )  for x in lines_same  if "locals" in x["var"] ] 
            accumulate_lines [ one_line_no ]= lines_same
        
        for one_line_no in uniq_line_no_list :
            lines_same = [x  for x in lines  if x["line_no"]   ==one_line_no  ]
            lines_same = [ "({}) {}".format( x["order_id"], expr_str( x["var"]["@init"] )  )  for x in lines_same  if "@init" in x["var"] ] 
            if len(lines_same)>0:
                accumulate_lines [ one_line_no ]= lines_same
        
        
        for one_line_no in uniq_line_no_list :
            lines_same = [x  for x in lines  if x["line_no"]   ==one_line_no  ]
            lines_same = [ "__return__={}".format(   x["var"]["@exception"] if "@exception" in x["var"] else x["var"]["@return"]  )  for x in lines_same  if ( "@exception" in x["var"] or  "@return" in x["var"]) ] 
            if len(lines_same)>0:
                accumulate_lines [ one_line_no ]= lines_same
        

        accumulate_lines = clip_long_list( accumulate_lines )
        
        return dict(accumulate_lines)
        
        
      

