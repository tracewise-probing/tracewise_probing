import json 
import os 
import sys 
import tiktoken
encoding = tiktoken.encoding_for_model("gpt-4o-mini")



def read_jsonl(jsonp ):
    
    with open( jsonp ) as fr :
        
        lines = [json.loads(x) for x in fr.readlines() ]
        
    return lines 


def num_tokens_from_string(string: str ): 
    num_tokens = len(encoding.encode(string))
    return num_tokens


if __name__ == "__main__":
    jsonp = sys.argv[-1]
    assert os.path.isfile( jsonp )
    assert jsonp.endswith(".jsonl")
    
    
    lines = read_jsonl(jsonp)
    
    for i in range( len(lines) ) :
        pmpt = lines[i]["prompt"]
        tk_size = num_tokens_from_string( pmpt )
        lines[i]["token_size"] = tk_size
        
    with open( jsonp , "w" ) as fw :
        fw.write( "\n".join( [json.dumps(x) for x in lines ] ) )
        
        