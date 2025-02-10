import os 
import hashlib 
import json 


def read_jsonl( jsonp ):
    with open( jsonp ) as fr :
        lines = [json.loads(x) for x in fr.readlines() ]
    return lines 


def md5func( xstr ):
    md5 = hashlib.md5(xstr.encode('utf-8')).hexdigest()

    return md5 



def get_cache_path( cache_dir , load_path ):
    with open(load_path) as fr :
        data =fr.read() 
    md5 = md5func( data )
    cache_path = "cache_{}.jsonl".format( md5 )
    return os.path.join( cache_dir , cache_path )

def write_jsonl( json_list, save_path ):
    assert type(save_path) == str 
    
    with open(save_path, "w" ) as fw :
        fw.write( "\n".join([json.dumps(x) for x in json_list ] ) )
    
    
import tiktoken
encoding = tiktoken.encoding_for_model("gpt-4o-mini")
def num_tokens_from_string(string: str ): 
    num_tokens = len(encoding.encode(string))
    return num_tokens
