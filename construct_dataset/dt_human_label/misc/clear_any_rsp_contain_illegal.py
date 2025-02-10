import os 
import json 
import re 
import sys 
pattern = r"```\s*markdown"
pattern2 = r"```\s*md"

def remove_any_rsp_contains_makrdown_implicity( jsonp ):
    with open( jsonp ) as fr :
        lines = fr.readlines()  
        raw_len = len(lines)
        json_lines = []
        for one in lines :
            try :
                json_lines.append(  json.loads(one ) )
            except json.JSONDecodeError  as ex :
                pass  

        
    count = 0 
    new_lines = [] 
    for i in range(len(json_lines)):
        line = json_lines[i]
        assert "solution" in line 
        solution = line["solution"]
        if re.findall(pattern, solution , re.IGNORECASE|re.DOTALL ):
            count+=1  
        elif re.findall(pattern2, solution , re.IGNORECASE|re.DOTALL ):
            count+=1  
        else:
            new_lines.append( line )
    if count >0 or raw_len!=len(new_lines) :
        print ("diff" , raw_len  - len(new_lines) , os.path.basename(jsonp) )
        return new_lines 
    
            
if __name__=="__main__":
    jsonp = sys.argv[-1]
    assert os.path.isfile(jsonp), jsonp 
    assert "fingerprinted000" not in os.path.basename( jsonp ), jsonp 
    
    
    newsave= remove_any_rsp_contains_makrdown_implicity( jsonp=jsonp )
    if newsave is not None :
        # print ("will save ")
        
        with open( jsonp, "w") as fw :
            fw.write( "\n".join([json.dumps(x) for x in newsave ]))            
            fw.write( "\n" )
