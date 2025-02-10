import re 
import os 
import json 




extract_no_test = r"(?P<notest>\s+no\stests\sran)\sin\s\d+\.\d+s"
extract_pattern=r"(?P<fail>(\d+)\sfailed)?,?\s?(?P<pass>(\d+)\spassed)?,?\s?(?P<error>(\d+)\s(error|errors|skipped|warnings|warning))?\sin\s(\d|\.)+s"


def parse_report_to_extract_fail_c_and_pass_c(report_str:str )->dict :
    
    if report_str == "Invalid JSON input" or report_str=="Timeout" or len(report_str.strip())<=0 :
        return {"invalid":1 }
    
    fail_c= 0 
    pass_c= 0 
    error_c=  0 
    
    invalid_match = re.search(extract_no_test, report_str)
    if invalid_match :
        return {"invalid":1 }
    
    x_match = re.search( extract_pattern, report_str, flags=re.IGNORECASE )
    if x_match :
        fail_c = x_match.group("fail")
        if not  fail_c :
            fail_c = 0 
        else :
            # print ( fail_c, type(fail_c), "fail_c" )
            fail_c = int( fail_c.replace("failed","") )
            assert fail_c >0 
        
        pass_c = x_match.group("pass")
        if not  pass_c :
            pass_c = 0 
        else :
            pass_c = int( pass_c.replace("passed","") )
            assert pass_c >0 
        
        error_c = x_match.group("error")
        if not  error_c :
            error_c = 0 
        else :
            error_c = int( error_c.replace("errors","").replace("error","").replace("warnings","").replace("warning","").replace("skipped","") )
            assert error_c >0 
        
    return {"pass_c":pass_c,"fail_c":fail_c,"error_c":error_c }
        
        
    
    
    
    
if __name__=="__main__":
    from glob2 import glob 

    import sys 
    from tqdm import tqdm 
    jsonp = sys.argv[-1]
    jsonp_list = []
    
    search_dir = "/mnt/local/home_dir/wj_code/dl_execute/reverse_train_data_collecting/data/valid_data_rq1_semcoder_yx_r_reconstruct_round1/"
    jsonp_list += glob ( os.path.join(search_dir, "*fingerprinted000-extracted-verified.jsonl") )
    search_dir = "/mnt/local/home_dir/wj_code/dl_execute/reverse_train_data_collecting/data/valid_data_rq1_semcoder_yx_r_reconstruct_round2/"
    jsonp_list += glob ( os.path.join(search_dir, "*fingerprinted000-extracted-verified.jsonl") )
    search_dir = "/mnt/local/home_dir/wj_code/dl_execute/reverse_train_data_collecting/data/valid_data_rq1_semcoder_yx_r_reconstruct_round3/"
    jsonp_list += glob ( os.path.join(search_dir, "*fingerprinted000-extracted-verified.jsonl") )
    search_dir = "/mnt/local/home_dir/wj_code/dl_execute/reverse_train_data_collecting/data/valid_data_rq1_semcoder_yx_r_reconstruct_round4/"
    jsonp_list += glob ( os.path.join(search_dir, "*fingerprinted000-extracted-verified.jsonl") )

    assert len(jsonp_list) 
    
    total_ =0 
    total_invalid =0 
     
    for jsonp in tqdm( jsonp_list ) :
        assert jsonp.endswith(".jsonl")
        with open(jsonp) as fr :
            lines = [json.loads(x) for x in fr.readlines() ]
        
        
        for  i in range( len(lines) ):
            
            line = lines[i]
            total_ +=1 
            report_str = line["extracted_code__tests__output"]
            info = parse_report_to_extract_fail_c_and_pass_c(report_str=report_str  )

            if "invalid" in info :
                # print ( line["uuid"])
                total_invalid+=1 
                continue 
            
            # if not any( [ info["pass_c"]>0 , info["fail_c"]>0, info["error_c"]>0 ]):
            #     with open("/tmp/rep.txt","a") as fw:
            #         fw.write( report_str )

            assert any( [ info["pass_c"]>0 , info["fail_c"]>0, info["error_c"]>0 ]), (info , line )
            # print ( info ) 
    
    print ("total--->",                  total_invalid, "/",                 total_ )