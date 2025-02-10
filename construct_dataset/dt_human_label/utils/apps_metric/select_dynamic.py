import json 

from .format_snoopy import  format_trace  

from .next_testing_util import  check_correctness , compress_json 

from .format_snoopy import  xstart as XSTART ,  x_var as X_VAR ,x_var1 as X_VAR1 ,x_return as X_RETURN 

from .format_snoopy import  x_nochange as XNOCHANGE

X_EXCEPTION= "Exception:....."

import pprint 

import re

def parse_code_v2(text):
    pattern = r'(\w[\w\d]*)\s*=\s*([^,\n]+)'
    matches = re.findall(pattern, text)
    variables = {}
    for var, value in matches:
        try:
            import ast
            evaluated_value = ast.literal_eval(value.strip())
        except (ValueError, SyntaxError):
            # If evaluation fails, keep it as a string
            evaluated_value = value.strip()
        variables[var] = evaluated_value
    return variables

def parse_code_v1( snoopy_code ):
    pattern = re.compile(r'(\w+)\s*=\s*((?:\[[^\]]*\]|\{[^\}]*\}|\([^\)]*\)|\'[^\']*\'|\"[^\"]*\"|[^,])+)(?:,|$)')
    matches = pattern.findall(snoopy_code)
    variable = {}
    for var, value in matches:
        variable[ var ] = value.strip()
    assert len(variable) > 0 ,( snoopy_code ,"...???")
    return variable

class _XNoneype:
    '''
    replace the None, to avoid deserilize
    '''
    def __new__(cls):
        return XNone
    def __reduce__(self):
        return (_XNoneype, ())
    def __copy__(self):
        return XNone
    def __deepcopy__(self, _):
        return XNone
    def __call__(self, _):
        pass
    def __repr__(self):
        return 'XNone'
    def __dict__(self):
        return {'XNone':'XNone'}

try:
    XNone # type: ignore
except NameError:
    XNone = object.__new__(_XNoneype)


map_dict_string = lambda  y:", ".join( [ "{}={}".format(k.replace("@",""),v ) for k,v in y.items() ] )

class DynState:
    def __init__(self, line_no: int, code: str):
        self.line_no = line_no
        self.code = code
        self.locals = []
        self.locals_init = []
        self.return_ = XNone
        self.exception = XNone
        self.nonchange = XNone
        self.order_id  =-1 
        
    def __getitem__(self, key: str):
        if key == '@return':
            return self.return_
        elif key == '@init':
            return self.locals_init
        elif key == '@exception':
            return self.exception
        elif key == "@nonchange":
            return self.nonchange 
        return self.locals#[ key] 

    def __setitem__(self, key: str, value):
        if type(value)==str :
            value = value.strip()
        if key == '@init':
            assert type(value)== str  or value is None , (key,value,"expect init with dict")
            self.locals_init .append(value)
        elif key == '@return':
            self.return_ = value
        elif key == '@exception':
            self.exception = value
        elif key == '@nonchange':
            self.nonchange = value
        else:
            # self.locals[key]=value 
            self.locals .append(value)

    def __dict__(self):
        _state = {}
        if not isinstance( self.return_ , _XNoneype ):
             _state["@return"]  = self.return_ 
        if not isinstance( self.exception , _XNoneype ):
             _state["@exception"]  = self.exception 
             # _state.pop("@exception") 
        # if isinstance( _state["@nonchange"] , _XNoneype ):
        #      _state.pop("@nonchange") 
        if isinstance( self.locals_init , list ) and len( self.locals_init )>0:
             _state["@init"]  =self.locals_init # {"__exception__":self.exception } 
             # _state.pop("@init") 
        if  len( self.locals   )>0:
             _state["locals"]=  self.locals  

        # map_list =  [ map_dict_string(y) for x,y in _state.items() ]
        return {"line_no":self.line_no , 
                "order_id":self.order_id , 
                "var":_state } 
    # self.locals ,"@return":self.return_,"@exception":self.exception,"@init":self.locals_init, "@nonchange":self.nonchange }

    def __str__(self) -> str:
        _state = {
            'line_no': self.line_no,
            'code': self.code,
            'order_id': self.order_id,
            'locals': self.locals,
            '@return': self.return_,
            '@init': self.locals_init,
            '@exception': self.exception,
            "@nonchange":self.nonchange,
        }
        if isinstance( _state["@return"] , _XNoneype ):
             _state.pop("@return") 
        if isinstance( _state["@exception"] , _XNoneype ):
             _state.pop("@exception") 
        if isinstance( _state["@nonchange"] , _XNoneype ):
             _state.pop("@nonchange") 
        if isinstance( _state["@init"] , list ) and len(_state["@init"])==0:
             _state.pop("@init") 
        if  len(_state["locals"])==0:
             _state.pop("locals") 
        return f"{_state}"

    def __repr__(self) -> str:
        return str(self)

    # def get_local(self, var: str):
    #     if var not in self.locals:
    #         return XNone
    #     return self.locals[var]

    def to_json(self):
        keys = ['line_no', 'locals']
        if self.return_ is not XNone:
            keys.append('@return')
        if type(self.locals_init)== list and len(self.locals_init)>0 :
            keys.append('@init')
        if self.exception is not XNone:
            keys.append('@exception')
        if self.nonchange is not XNone:
            keys.append('@nonchange')
        d = {k: self[k] for k in keys}
        # convert special types to serializable types
        # for k, v in d['locals'].items():
        #     if isinstance(v, set):
        #         d['locals'][k] = list(v)
        # convert exception to its class name
        if '@exception' in d:
            d['@exception'] = d['@exception'].__class__.__name__
        # if '@return' in d:
        #     d['@return'] = d['@return']
        # if '@init' in d:
        #     d['@init'] = d['@return']
        return d

class DynStates:
    def __init__(self,caseid=None, meta_info={}  ):
        self.caseid  = caseid
        self._states: list[DynState] = []
        self._global_index = 0 
        self._meta_info = meta_info 
    def __getitem__(self, key: int):
        return self._states[key]

    def __len__(self):
        return len(self._states)

    def __str__(self) -> str:
        return str(self._states)

    def __repr__(self) -> str:
        return str(self)

    def append(self, state: DynState):
        self._global_index +=1 
        state.order_id = self._global_index 
        # print ( state )
        self._states.append(state)

    @property
    def trace(self):
        return [state.line_no for state in self._states]

    def get_coverage(self, line_no: int):
        return line_no in self.trace

    def get_next_line(self, line_no: int) -> set[int]:
        if not self.get_coverage(line_no):
            return {-1}
        lines = []
        state_idxs = [i for i, state in enumerate(self._states) if state.line_no == line_no]
        for idx in state_idxs:
            if idx + 1 < len(self._states):
                lines.append(self._states[idx + 1].line_no)
            else:
                lines.append(-1)
        return set(lines)

    def interpret_var(self, line_no , var_name ):
        if not self.get_coverage(line_no):
            return None 
        lines = []
        state_selected = [state for  state in self._states if state.line_no == line_no]
        for one_state in state_selected :
            if var_name in one_state.locals :
                lines.append( {"var":var_name, "v": one_state.locals[var_name]} )
                
        if len( lines )>0:
            return lines[-1]
        return None 

    def get_local(self, line_no: int, var: str):
        '''
        For lines that are not executed, this function returns `XNone`,
        although `var` may be valid. This rule also applies to
        `get_attr` and `get_subscript`.
        '''
        vars = []
        for state in self.get_states_after(line_no):
            v = state.get_local(var)
            if v is not XNone:
                vars.append(v)
        if len(vars) == 0:
            return XNone
        return vars

    def get_return(self, line_no: int):
        l = [state.return_ for state in self._states if state.line_no == line_no and state.return_ != XNone]
        assert len(l) <= 1, f"Multiple return values found for line {line_no}: {l}"
        return l[0] if len(l) == 1 else XNone

    def get_exception(self, line_no: int):
        l = [state.exception for state in self._states if state.line_no == line_no and state.exception != XNone]
        assert len(l) <= 1, f"Multiple exceptions found for line {line_no}: {l}"
        return l[0] if len(l) == 1 else XNone

    def to_json(self):
        return [state.to_json() for state in self._states]



def convert_tracestr_to_sandbox (code, sample ,only_true=True  ):
    
    assert "input_output" in sample 
    # print ( code ,"=========\n\n"*8 )
    
    in_out =json.loads( sample["input_output"] ) if type(sample["input_output"] ) == str else sample["input_output"]  
    if  code is None or len(code.strip())<=0:
        print ("code is null", sample.get("task_id",None), "---",sample.get("problem_id",None))
        return None 
    # assert "fn_name" in in_out , ( sample )
    
    # max_try = 4 
    # for retry_i in range(max_try ):
    trace_list = []
    output_list_out = [] 
    err_list_out = []
    
    check_status = check_correctness(
        sample = sample ,
        
        test = code,
        use_snooper = True ,
        trace_list_out=trace_list,
        output_list_out = output_list_out , 
        err_list_out= err_list_out,
        )
    sandbox_list_inf = {}

    if len(trace_list) <=0 :
        print ("trace is null ","uuid--->",sample.get("uuid",None))
        sandbox_list_inf ["err_msg"] = compress_json( err_list_out  )
        return None 
        
    
    assert len(trace_list ) == 1 

    trace_str = trace_list[0]
    trace_str = trace_str.decode("utf-8") if type(trace_str)==bytes else trace_str 
    
    trace_raw_list = format_trace (trace_str=trace_str ,code_shift_size =18 if "fn_name" in in_out else 21 )

    # print ( trace_str )
    assert len( trace_raw_list ) == len( output_list_out ) , (output_list_out, trace_raw_list, trace_list , check_status  )
    assert len( trace_raw_list ) == len(check_status) , (check_status, trace_raw_list  , trace_list , check_status )

    _codelines = code.split("\n")
    for  test_case_id , trace_info_dict  in  trace_raw_list.items():# , check_status , output_list_out ):
        int_index  =  int(  test_case_id.replace("t_", "") )

        if only_true :
            if check_status[int_index ] ==True :
                continue 

        cur_in_out_expect = output_list_out[int_index ]
        cur_in_out_expect = json.loads(cur_in_out_expect) if len(cur_in_out_expect)>0 else {}

        cur_err_info  = err_list_out[int_index] if len(err_list_out)>int_index+1 else err_list_out[0] if len(err_list_out)>0 else None 
        meta_info ={**cur_in_out_expect, "err": cur_err_info }  

        
        obj_sta_grp = DynStates( meta_info = meta_info )

        setattr(obj_sta_grp, "raw_trace",trace_info_dict )


        for key ,trace_info_list in trace_info_dict.items() :
            # exit()
    
            for one_trace_info  in trace_info_list :
                
                if "except" in one_trace_info :
                    line_no = one_trace_info["line_no"] 
                    state_str_raw  = one_trace_info["except"] 
                    if state_str_raw.startswith(X_EXCEPTION) :
                        key = "@exception"
                        state_str = state_str_raw[ len("Starting var:.."):]
                        obj_state =  DynState( 
                            line_no = line_no,
                            code = _codelines[  line_no-1  ],
                            )
                        obj_state.__setitem__(key= key ,value =state_str )
                        obj_sta_grp.append ( obj_state )
                    continue 
                if "starting" in one_trace_info :
                    line_no = one_trace_info["line_no"] 
                    state_str_raw  = one_trace_info["starting"] 
                    if state_str_raw.startswith(XSTART) :
                        key = "@init"
                        state_str = state_str_raw[ len("Starting var:.."):]
                        obj_state =  DynState( 
                            line_no = line_no,
                            code = _codelines[  line_no-1  ],
                            )
                        obj_state.__setitem__(key= key ,value =state_str )
                        obj_sta_grp.append ( obj_state )
                    # print ( "state_str_raw" , state_str_raw, obj_state )
                    # exit()
                    continue 
                #     continue 
                if "end" in  one_trace_info :
                    line_no = one_trace_info["line_no"] 
                    # print ("TPL_CODEEXECUTOR.len",len(_codelines),  "line_no", line_no ,"one_trace_info", one_trace_info )
                    state_str_raw  = one_trace_info["end"] 
                    if state_str_raw.startswith(X_RETURN) :
                        key = "@return"
                        state_str = state_str_raw[ len("Starting var:.."):]
                        obj_state =  DynState( 
                            line_no = line_no,
                            code = _codelines[  line_no-1  ],
                            )
                        obj_state.__setitem__(key= key ,value =state_str )
                        obj_sta_grp.append ( obj_state )
                    continue 
                # print ("#######3"*20, one_trace_info)
                line_no = one_trace_info["line_no"]
                # assert "var" in one_trace_info , (one_trace_info ) 
                if "var" not in one_trace_info :
                    continue 
                state_str_raw  = one_trace_info["var"] 
                if state_str_raw.startswith(XSTART):
                    key = "@init"
                    
                    state_str = state_str_raw[ len("Starting var:.."):]
                    if line_no < len(_codelines):
                        obj_state =  DynState( 
                            line_no = line_no,
                            code = _codelines[  line_no ],
                            )
                        obj_state.__setitem__(key= key ,value =state_str )
                        # print ( "---", obj_state )
                        obj_sta_grp.append ( obj_state )
                    continue 
                
    
                if  state_str_raw.startswith(X_VAR) or  state_str_raw.startswith(X_VAR1) :
                    key = "locals"
                    state_str = state_str_raw[ len("Starting var:.."):]
    
                    obj_state =  DynState( 
                        line_no = line_no,
                        code = _codelines[  line_no-1  ],
                        )
                    # for key,value in state_dict.items():
                    #     obj_state.__setitem__(key= key ,value =value )
                    obj_state.__setitem__(key= key ,value =state_str.strip() )
    
                    obj_sta_grp.append ( obj_state )
    
                elif state_str_raw.startswith(X_RETURN):
                    key = "@return"
                    state_str = state_str_raw[ len("Starting var:.."):]
                    obj_state =  DynState( 
                        line_no = line_no,
                        code = _codelines[  line_no-1  ],
                        )
                    obj_state.__setitem__(key= key ,value =state_str )
                    obj_sta_grp.append ( obj_state )
                
        # exit()
        sandbox_list_inf[test_case_id]=obj_sta_grp
    return sandbox_list_inf 


