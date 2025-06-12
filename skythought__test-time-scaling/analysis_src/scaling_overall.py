import os 
import json 
import pandas as pd 


from itertools import product 

result="""
sec4_llmscore_parallel_sample_temp02__qwen_7b_easy_n_1__mbppannex.json:{"final_accuracy": "39.73%"}
sec4_llmscore_parallel_sample_temp02__qwen_7b_easy_n_8__mbppannex.json:{"final_accuracy": "53.97%"}
sec4_llmscore_parallel_sample_temp02_bug_trace_TPL_CODEEXECUTOR_qwen_7b_easy_n_1__mbppannex.json:{"final_accuracy": "39.18%"}
sec4_llmscore_parallel_sample_temp02_bug_trace_TPL_CODEEXECUTOR_qwen_7b_easy_n_8__mbppannex.json:{"final_accuracy": "53.42%"}
sec4_llmscore_parallel_sample_temp02_bug_trace_TPL_CONCISETRACE_qwen_7b_easy_n_1__mbppannex.json:{"final_accuracy": "41.92%"}
sec4_llmscore_parallel_sample_temp02_bug_trace_TPL_CONCISETRACE_qwen_7b_easy_n_8__mbppannex.json:{"final_accuracy": "52.60%"}
sec4_llmscore_parallel_sample_temp02_bug_trace_TPL_NEXT_qwen_7b_easy_n_1__mbppannex.json:{"final_accuracy": "38.90%"}
sec4_llmscore_parallel_sample_temp02_bug_trace_TPL_NEXT_qwen_7b_easy_n_8__mbppannex.json:{"final_accuracy": "53.70%"}
sec4_llmscore_parallel_sample_temp02_bug_trace_TPL_OUR01_qwen_7b_easy_n_1__mbppannex.json:{"final_accuracy": "42.19%"}
sec4_llmscore_parallel_sample_temp02_bug_trace_TPL_OUR01_qwen_7b_easy_n_8__mbppannex.json:{"final_accuracy": "54.52%"}
sec4_llmscore_parallel_sample_temp05__qwen_7b_easy_n_1__mbppannex.json:{"final_accuracy": "38.63%"}
sec4_llmscore_parallel_sample_temp05__qwen_7b_easy_n_1__mbppannex.json:{"final_accuracy": "39.18%"}
sec4_llmscore_parallel_sample_temp05__qwen_7b_easy_n_8__mbppannex.json:{"final_accuracy": "54.52%"}
sec4_llmscore_parallel_sample_temp05_bug_trace_TPL_CODEEXECUTOR_qwen_7b_easy_n_1__mbppannex.json:{"final_accuracy": "36.71%"}
sec4_llmscore_parallel_sample_temp05_bug_trace_TPL_CONCISETRACE_qwen_7b_easy_n_8__mbppannex.json:{"final_accuracy": "55.34%"}
sec4_llmscore_parallel_sample_temp05_bug_trace_TPL_NEXT_qwen_7b_easy_n_8__mbppannex.json:{"final_accuracy": "55.62%"}
sec4_llmscore_parallel_sample_temp05_bug_trace_TPL_OUR01_qwen_7b_easy_n_8__mbppannex.json:{"final_accuracy": "56.71%"}
sec4_llmscore_parallel_sample_temp09__qwen_7b_easy_n_1__mbppannex.json:{"final_accuracy": "40.00%"}
sec4_llmscore_parallel_sample_temp09__qwen_7b_easy_n_8__mbppannex.json:{"final_accuracy": "54.52%"}
sec4_llmscore_parallel_sample_temp09_bug_trace_TPL_CODEEXECUTOR_qwen_7b_easy_n_1__mbppannex.json:{"final_accuracy": "37.81%"}
sec4_llmscore_parallel_sample_temp09_bug_trace_TPL_CODEEXECUTOR_qwen_7b_easy_n_8__mbppannex.json:{"final_accuracy": "55.89%"}
sec4_llmscore_parallel_sample_temp09_bug_trace_TPL_CONCISETRACE_qwen_7b_easy_n_1__mbppannex.json:{"final_accuracy": "40.27%"}
sec4_llmscore_parallel_sample_temp09_bug_trace_TPL_CONCISETRACE_qwen_7b_easy_n_8__mbppannex.json:{"final_accuracy": "55.34%"}
sec4_llmscore_parallel_sample_temp09_bug_trace_TPL_NEXT_qwen_7b_easy_n_1__mbppannex.json:{"final_accuracy": "39.73%"}
sec4_llmscore_parallel_sample_temp09_bug_trace_TPL_NEXT_qwen_7b_easy_n_8__mbppannex.json:{"final_accuracy": "55.07%"}
sec4_llmscore_parallel_sample_temp09_bug_trace_TPL_OUR01_qwen_7b_easy_n_1__mbppannex.json:{"final_accuracy": "34.79%"}


sec4_llmscore_parallel_sample_temp02__qwen_7b_easy_n_16__mbppannex.json:{"final_accuracy": "53.70%"}
sec4_llmscore_parallel_sample_temp02_bug_trace_TPL_CODEEXECUTOR_qwen_7b_easy_n_16__mbppannex.json:{"final_accuracy": "55.34%"}
sec4_llmscore_parallel_sample_temp02_bug_trace_TPL_CONCISETRACE_qwen_7b_easy_n_16__mbppannex.json:{"final_accuracy": "57.81%"}
sec4_llmscore_parallel_sample_temp02_bug_trace_TPL_NEXT_qwen_7b_easy_n_16__mbppannex.json:{"final_accuracy": "56.44%"}
sec4_llmscore_parallel_sample_temp02_bug_trace_TPL_OUR01_qwen_7b_easy_n_16__mbppannex.json:{"final_accuracy": "56.44%"}

sec4_llmscore_parallel_sample_temp05__qwen_7b_easy_n_16__mbppannex.json:{"final_accuracy": "61.37%"}
sec4_llmscore_parallel_sample_temp05_bug_trace_TPL_CODEEXECUTOR_qwen_7b_easy_n_16__mbppannex.json:{"final_accuracy": "59.45%"}
sec4_llmscore_parallel_sample_temp05_bug_trace_TPL_CONCISETRACE_qwen_7b_easy_n_16__mbppannex.json:{"final_accuracy": "58.08%"}
sec4_llmscore_parallel_sample_temp05_bug_trace_TPL_NEXT_qwen_7b_easy_n_16__mbppannex.json:{"final_accuracy": "56.16%"}
sec4_llmscore_parallel_sample_temp05_bug_trace_TPL_OUR01_qwen_7b_easy_n_16__mbppannex.json:{"final_accuracy": "56.44%"}

sec4_llmscore_parallel_sample_temp09__qwen_7b_easy_n_16__mbppannex.json:{"final_accuracy": "59.73%"}
sec4_llmscore_parallel_sample_temp09_bug_trace_TPL_CODEEXECUTOR_qwen_7b_easy_n_16__mbppannex.json:{"final_accuracy": "58.08%"}
sec4_llmscore_parallel_sample_temp09_bug_trace_TPL_CONCISETRACE_qwen_7b_easy_n_16__mbppannex.json:{"final_accuracy": "58.36%"}
sec4_llmscore_parallel_sample_temp09_bug_trace_TPL_NEXT_qwen_7b_easy_n_16__mbppannex.json:{"final_accuracy": "56.71%"}
sec4_llmscore_parallel_sample_temp09_bug_trace_TPL_OUR01_qwen_7b_easy_n_16__mbppannex.json:{"final_accuracy": "60.27%"}



sec4_llmscore_parallel_sample_temp02__qwen_7b_easy_n_32__mbppannex.json:{"final_accuracy": "58.36%"}
sec4_llmscore_parallel_sample_temp02_bug_trace_TPL_CODEEXECUTOR_qwen_7b_easy_n_32__mbppannex.json:{"final_accuracy": "56.99%"}
sec4_llmscore_parallel_sample_temp02_bug_trace_TPL_CONCISETRACE_qwen_7b_easy_n_32__mbppannex.json:{"final_accuracy": "58.90%"}
sec4_llmscore_parallel_sample_temp02_bug_trace_TPL_OUR01_qwen_7b_easy_n_32__mbppannex.json:{"final_accuracy": "56.99%"}
sec4_llmscore_parallel_sample_temp05__qwen_7b_easy_n_32__mbppannex.json:{"final_accuracy": "60.82%"}
sec4_llmscore_parallel_sample_temp05_bug_trace_TPL_CONCISETRACE_qwen_7b_easy_n_32__mbppannex.json:{"final_accuracy": "63.01%"}
sec4_llmscore_parallel_sample_temp05_bug_trace_TPL_NEXT_qwen_7b_easy_n_32__mbppannex.json:{"final_accuracy": "60.55%"}
sec4_llmscore_parallel_sample_temp09__qwen_7b_easy_n_32__mbppannex.json:{"final_accuracy": "64.11%"}
sec4_llmscore_parallel_sample_temp09_bug_trace_TPL_CODEEXECUTOR_qwen_7b_easy_n_32__mbppannex.json:{"final_accuracy": "63.29%"}
sec4_llmscore_parallel_sample_temp09_bug_trace_TPL_NEXT_qwen_7b_easy_n_32__mbppannex.json:{"final_accuracy": "64.11%"}
sec4_llmscore_parallel_sample_temp09_bug_trace_TPL_OUR01_qwen_7b_easy_n_32__mbppannex.json:{"final_accuracy": "61.92%"}


sec4_llmscore_parallel_sample_vanilla__qwen_7b_easy_n_1__mbppannex.json:{"final_accuracy": "40.27%"}
sec4_llmscore_parallel_sample_vanilla__qwen_7b_easy_n_2__mbppannex.json:{"final_accuracy": "43.56%"}
sec4_llmscore_parallel_sample_vanilla__qwen_7b_easy_n_4__mbppannex.json:{"final_accuracy": "52.60%"}
sec4_llmscore_parallel_sample_vanilla__qwen_7b_easy_n_8__mbppannex.json:{"final_accuracy": "53.97%"}
sec4_llmscore_parallel_sample_vanilla__qwen_7b_easy_n_32__mbppannex.json:{"final_accuracy": "61.64%"}
sec4_llmscore_parallel_sample_vanilla__qwen_7b_easy_n_64__mbppannex.json:{"final_accuracy": "66.03%"}
sec4_llmscore_parallel_sample_vanilla__qwen_7b_easy_n_128__mbppannex.json:{"final_accuracy": "64.66%"}
sec4_llmscore_parallel_sample_vanilla_bug_trace_TPL_CODEEXECUTOR_qwen_7b_easy_n_1__mbppannex.json:{"final_accuracy": "38.08%"}
sec4_llmscore_parallel_sample_vanilla_bug_trace_TPL_CODEEXECUTOR_qwen_7b_easy_n_2__mbppannex.json:{"final_accuracy": "49.04%"}
sec4_llmscore_parallel_sample_vanilla_bug_trace_TPL_CODEEXECUTOR_qwen_7b_easy_n_4__mbppannex.json:{"final_accuracy": "49.32%"}
sec4_llmscore_parallel_sample_vanilla_bug_trace_TPL_CODEEXECUTOR_qwen_7b_easy_n_8__mbppannex.json:{"final_accuracy": "56.71%"}
sec4_llmscore_parallel_sample_vanilla_bug_trace_TPL_CODEEXECUTOR_qwen_7b_easy_n_32__mbppannex.json:{"final_accuracy": "63.01%"}
sec4_llmscore_parallel_sample_vanilla_bug_trace_TPL_CODEEXECUTOR_qwen_7b_easy_n_64__mbppannex.json:{"final_accuracy": "63.01%"}
sec4_llmscore_parallel_sample_vanilla_bug_trace_TPL_CODEEXECUTOR_qwen_7b_easy_n_128__mbppannex.json:{"final_accuracy": "65.75%"}
sec4_llmscore_parallel_sample_vanilla_bug_trace_TPL_CONCISETRACE_qwen_7b_easy_n_1__mbppannex.json:{"final_accuracy": "39.45%"}
sec4_llmscore_parallel_sample_vanilla_bug_trace_TPL_CONCISETRACE_qwen_7b_easy_n_2__mbppannex.json:{"final_accuracy": "47.12%"}
sec4_llmscore_parallel_sample_vanilla_bug_trace_TPL_CONCISETRACE_qwen_7b_easy_n_4__mbppannex.json:{"final_accuracy": "52.33%"}
sec4_llmscore_parallel_sample_vanilla_bug_trace_TPL_CONCISETRACE_qwen_7b_easy_n_8__mbppannex.json:{"final_accuracy": "57.26%"}
sec4_llmscore_parallel_sample_vanilla_bug_trace_TPL_CONCISETRACE_qwen_7b_easy_n_32__mbppannex.json:{"final_accuracy": "59.45%"}
sec4_llmscore_parallel_sample_vanilla_bug_trace_TPL_CONCISETRACE_qwen_7b_easy_n_64__mbppannex.json:{"final_accuracy": "64.38%"}
sec4_llmscore_parallel_sample_vanilla_bug_trace_TPL_CONCISETRACE_qwen_7b_easy_n_128__mbppannex.json:{"final_accuracy": "64.38%"}
sec4_llmscore_parallel_sample_vanilla_bug_trace_TPL_NEXT_qwen_7b_easy_n_1__mbppannex.json:{"final_accuracy": "39.18%"}
sec4_llmscore_parallel_sample_vanilla_bug_trace_TPL_NEXT_qwen_7b_easy_n_2__mbppannex.json:{"final_accuracy": "44.66%"}
sec4_llmscore_parallel_sample_vanilla_bug_trace_TPL_NEXT_qwen_7b_easy_n_4__mbppannex.json:{"final_accuracy": "51.78%"}
sec4_llmscore_parallel_sample_vanilla_bug_trace_TPL_NEXT_qwen_7b_easy_n_8__mbppannex.json:{"final_accuracy": "55.89%"}
sec4_llmscore_parallel_sample_vanilla_bug_trace_TPL_NEXT_qwen_7b_easy_n_32__mbppannex.json:{"final_accuracy": "61.10%"}
sec4_llmscore_parallel_sample_vanilla_bug_trace_TPL_NEXT_qwen_7b_easy_n_64__mbppannex.json:{"final_accuracy": "68.22%"}
sec4_llmscore_parallel_sample_vanilla_bug_trace_TPL_NEXT_qwen_7b_easy_n_128__mbppannex.json:{"final_accuracy": "65.48%"}
sec4_llmscore_parallel_sample_vanilla_bug_trace_TPL_OUR01_qwen_7b_easy_n_1__mbppannex.json:{"final_accuracy": "37.81%"}
sec4_llmscore_parallel_sample_vanilla_bug_trace_TPL_OUR01_qwen_7b_easy_n_2__mbppannex.json:{"final_accuracy": "46.03%"}
sec4_llmscore_parallel_sample_vanilla_bug_trace_TPL_OUR01_qwen_7b_easy_n_4__mbppannex.json:{"final_accuracy": "51.78%"}
sec4_llmscore_parallel_sample_vanilla_bug_trace_TPL_OUR01_qwen_7b_easy_n_8__mbppannex.json:{"final_accuracy": "55.34%"}
sec4_llmscore_parallel_sample_vanilla_bug_trace_TPL_OUR01_qwen_7b_easy_n_32__mbppannex.json:{"final_accuracy": "61.37%"}
sec4_llmscore_parallel_sample_vanilla_bug_trace_TPL_OUR01_qwen_7b_easy_n_64__mbppannex.json:{"final_accuracy": "63.84%"}
"""

def parse_meta (score_path ):
    with open(score_path) as fr :
        meta = fr.readlines()[0] 
    
def qwen_result_paralleling():
    temp_list = ["vanilla","temp02","temp05","temp09"]
    n_list = [ 1,2,4,8,16,32,64,128]
    product_list = list( product( temp_list , n_list) )
    
    parallel_format = f"sec4_llmscore_parallel_sample_{temp}__qwen_7b_easy_n_{n}__mbppannex.json"
    
    path_list = [ ]
    
    for line in result.split():
        path = line.split(":")[0]
        
        
if __name__=="__main__":
    pass 