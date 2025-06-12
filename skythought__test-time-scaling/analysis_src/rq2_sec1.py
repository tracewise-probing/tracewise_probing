## get baseline for all 
import os 
import json 
import numpy as np 

search_dir =os.path.join( os.path.dirname(__file__), "..","results_sky_v2" )

print ("search_dir", search_dir )


model_list = [    "dk7b", "llama8b","marcon-o1","phi4","qwen7b" ]
trace_list = ["trace_TPL_CONCISETRACE","trace_TPL_NEXT","trace_TPL_OUR01"]


def read_file( fpath  ):
    with open(fpath) as fr :
        item_list = [ json.loads( x  ) for x in  fr.readlines() ]
    
    pred_list= {}
    acc = None 
    meta = {}
    for item in item_list :
        if  "final_accuracy" in item and type(item) == dict :
            acc = item["final_accuracy"] 

        try :
            meta = json.loads(item )
            meta = meta if type(meta) == dict and  "difficulty" in meta  else {} 
            continue 
        except json.JSONDecodeError :
            pass 
        except TypeError:
            pass 
    
        def check_empty(variable):
            return bool(variable and any(variable))
        if 'task_id' in item and (
           ('code' in item and check_empty(item["code"])) or
           ('codes' in item and check_empty(item["codes"]))
        ):
            if "passed" not in item and "completion_and_pass" in item:
                item["passed"] = item["completion_and_pass"]
                
            pred_list[item["task_id"]]= item
            
    pred_list = list(pred_list.values() )
    return  {"acc": acc , "meta":meta, "predictions":pred_list,  }

    
def overall_zeroshot( search_dir, prefix="" ):
    meta_info_list = []
    
    for model in model_list:
        meta_info_list_macro = []
        
        for  diff in  ["easy","medium","hard"]:
            zero_shot_baseline = f"baselines_{model}_{diff}{prefix}.json"
            meta = read_file(  os.path.join(search_dir , zero_shot_baseline) ) 
            meta_info_list_macro .append( {"name":"zeroshot", "diff":diff, "m":model , **meta } )

        meta_info_list.extend( meta_info_list_macro )                  
        ## group model 
        all_pred = {}
        all_pred_list = []
        for onemeta in meta_info_list_macro  :
            for pred in onemeta["predictions"] :
                all_pred[pred["task_id"]] = pred["passed"]
                all_pred_list.append(  pred["passed"] )
        
        acc_macro = np.mean( list(all_pred.values() ) )
        acc_macro = acc_macro*100 

        acc_macro_v2 = np.mean( all_pred_list)
        acc_macro_v2 = acc_macro_v2*100 

        str2float = lambda arr : float( np.char.rstrip(arr, '%').astype(float) )

        avg_acc = [str2float(x["acc"]) if x["acc"] else 0  for x in meta_info_list_macro ]
        # print ("avg_acc" , avg_acc)
        assert len(avg_acc) ==3 
        avg_acc = np.mean(avg_acc) 
        print ("model",model , "avg.acc", acc_macro, "sample_size", len(all_pred)  )
    ##
    
def overall_seq_vanilla( search_dir, prefix="" ):
    meta_info_list = []

    trace_list = ["bug_trace_TPL_CONCISETRACE","bug_trace_TPL_NEXT","bug_trace_TPL_OUR01","bug_trace_TPL_CODEEXECUTOR"]
    
    for trace in ["no_trace"]+trace_list:
        for model in model_list:
            meta_info_list_macro = []
            
            for  diff in  ["easy","medium","hard"]:
                #final_bug_trace_TPL_CONCISETRACE_phi4_n_1_debug_public3_select_random_easy
                zero_shot_baseline = f"final_{trace}_{model}_n_1_debug_public3_select_random_{diff}{prefix}.json"
                zero_shot_baseline_bak = f"final_{trace}_{model}_n1_debug_public3_select_random_{diff}{prefix}.json"
                xpath = os.path.join(search_dir , zero_shot_baseline)
                if not  os.path.isfile(xpath):
                    xpath = os.path.join(search_dir , zero_shot_baseline_bak)
                meta = read_file(   xpath ) 
                meta_info_list_macro .append( {"name":"seq_vanilla", "trace":trace,"diff":diff, "m":model , **meta } )
    
            meta_info_list.extend( meta_info_list_macro )                  
            ## group model 
            all_pred = {}
            all_pred_list = []
            for onemeta in meta_info_list_macro  :
                for pred in onemeta["predictions"] :
                    all_pred[pred["task_id"]] = pred["passed"]
                    all_pred_list.append(  pred["passed"] )
            
            acc_macro = np.mean( list(all_pred.values() ) )
            acc_macro = acc_macro*100 
    
            acc_macro_v2 = np.mean( all_pred_list)
            acc_macro_v2 = acc_macro_v2*100 
    
            str2float = lambda arr : float( np.char.rstrip(arr, '%').astype(float) )
    
            avg_acc = [str2float(x["acc"]) if x["acc"] else 0  for x in meta_info_list_macro ]
            # print ("avg_acc" , avg_acc)
            assert len(avg_acc) ==3 
            avg_acc = np.mean(avg_acc) 
            print ("model",trace+"__"+model , "avg.acc", acc_macro, "sample_size", len(all_pred)  )
    ##
def overall_voting( search_dir,prefix="" ):
    meta_info_list = []
    x_model_list =model_list = [     "llama8b","marcon-o1","phi4","qwen7b" ]
    #["dk7b","marcon-o1" ]

    trace_list = ["bug_trace_TPL_CONCISETRACE","bug_trace_TPL_NEXT","bug_trace_TPL_OUR01","bug_trace_TPL_CODEEXECUTOR"]

    for trace in [""]+trace_list:
        for model in x_model_list:
            meta_info_list_macro = []
            
            for  diff in  ["easy" ]:#,"medium","hard"]:
                zero_shot_baseline = f"majority{trace}_{model}_n_16_{diff}{prefix}.json"
                meta = read_file(  os.path.join(search_dir , zero_shot_baseline) ) 
                meta_info_list_macro .append( {"name":f"voting_{trace}", "diff":diff, "m":model , **meta } )
    
            meta_info_list.extend( meta_info_list_macro )                  
            ## group model 
            all_pred = {}
            all_pred_list = []
            for onemeta in meta_info_list_macro  :
                for pred in onemeta["predictions"] :
                    all_pred[pred["task_id"]] = pred["passed"]
                    all_pred_list.append(  pred["passed"] )
            
            acc_macro = np.mean( list(all_pred.values() ) )
            acc_macro = acc_macro*100 
    
            acc_macro_v2 = np.mean( all_pred_list)
            acc_macro_v2 = acc_macro_v2*100 
    
            str2float = lambda arr : float( np.char.rstrip(arr, '%').astype(float) )
    
            avg_acc = [str2float(x["acc"]) if x["acc"] else 0  for x in meta_info_list_macro ]
            # print ("avg_acc" , avg_acc)
            # assert len(avg_acc) ==3 
            avg_acc = np.mean(avg_acc) 
            print ("model",trace+"__"+model , "avg.acc", acc_macro, "sample_size", len(all_pred)  )
                    
    

def sec5_lcb(search_dir , mode="easy",flist=[] , is_force_show=True ):
    
    def read_load_lcb( name_path ):
        # if "easy" in name_path :
        #     mode="easy" 
        # elif "medium" in name_path :
        #     mode="medium" 
        # elif "hard" in name_path :
        #     mode="hard" 
        # else :
        #     assert 1==2     
        name_path = name_path.replace("easy",mode)
        
        name_path = os.path.join(search_dir, name_path )
        with open(name_path) as fr :
            lines = []
            for x in fr.readlines():
                try  :
                    x = json.loads(x)
                except json.decoder.JSONDecodeError :
                    # print (x)
                    continue 
                lines.append( x )
            # lines = [for x in fr.readline() ]
            if not is_force_show :
                lines = [x for x in lines if type(x)==dict and "task_id" in x and ( ("codes" in x and x["codes"] ) or  ("code" in x and x["code"] ) ) ]
            else:
                lines = [x for x in lines if type(x)==dict and "task_id" in x ] 
            lines = {x["task_id"]:x  for x in lines }
            
        return list(lines.values()) 
    
    def canculate_passed( item_list ):
        axis = None  # 0> mean , 1 -> mean,axis1 
        pass_list =[]
        for item in item_list :
            if "task_id" not in item :
                continue 
            if "passed" not in item :
                continue 
            p_list = item["passed"]
            # print ( "-->",p_list )
            if axis is None :
                if type(p_list) in [ list , tuple] :
                    axis= 1
                else:
                    axis= 0 
            pass_list.append( p_list )
        
        if len(pass_list) <=0 :
            return None 
        # assert len(pass_list) >0 
        # print ( pass_list, "axis", axis )
        # acc = np.mean(pass_list,axis= 0  )
        acc = np.mean(pass_list)#,axis= 0  )
        if type(acc) == float:
            return acc 
        return acc.tolist() 
    
    if not flist:
        trace_list = ["bug_trace_TPL_CONCISETRACE","bug_trace_TPL_NEXT","bug_trace_TPL_OUR01","bug_trace_TPL_CODEEXECUTOR"]
        for trace_name in   trace_list:  
            t1  = f"sec5_{trace_name}revision_vanilla_qwen_7b_easy_max_round_5.json"
            xlist = read_load_lcb(t1)
            t1_acc = canculate_passed(xlist)
            print (t1, t1_acc , len(xlist), "x1")
            
            
            t2  = f"sec5_{trace_name}_revision_refine_qwen_7b_easy_max_round_5.json"
            xlist = read_load_lcb(t2)
            t2_acc = canculate_passed(xlist)
            print (t2  , t2_acc, len(xlist))
            
        print ("vanilla")
        t2="sec5_revision_vanilla_qwen_7b_easy_max_round_5.json"    
        xlist = read_load_lcb(t2)
        t2_acc = canculate_passed(xlist)
        print (t2  , t2_acc, len(xlist), "x1")
        
        t2="sec5__revision_refine_qwen_7b_easy_max_round_5.json"
        xlist = read_load_lcb(t2)
        t2_acc = canculate_passed(xlist)
        print (t2  , t2_acc, len(xlist))
    else:
        for tttt in flist :
            xlist = read_load_lcb(tttt)
            t2_acc = canculate_passed(xlist)
            if t2_acc is None :
                continue 
            xlist_c = len(xlist)
            
            # print( type(t2_acc), "t2_acc.", tttt ) 
            t2_acc =t2_acc[:4] if type(t2_acc) != float  else t2_acc 
            if mode =="easy" :#and xlist_c ==26 :
                print (tttt  , "->", t2_acc, len(xlist), "x1")
        
    
    
flist="""
majority_dk7b_n_16_easy.json
majority_llama8b_n_16_easy.json
majority_llmjudge__qwen7b_n_16_easy.json
majority_llmscore__qwen7b_n_16_easy.json
majority_llmtool__qwen7b_n_16_easy.json
majority_marcon-o1_n_16_easy.json
majority_phi4_n_16_easy.json
majority_qwen7b_n_16_easy.json
majoritybug_trace_TPL_CODEEXECUTOR_dk7b_n_16_easy.json
majoritybug_trace_TPL_CODEEXECUTOR_llama8b_n_16_easy.json
majoritybug_trace_TPL_CODEEXECUTOR_marcon-o1_n_16_easy.json
majoritybug_trace_TPL_CODEEXECUTOR_phi4_n_16_easy.json
majoritybug_trace_TPL_CODEEXECUTOR_qwen7b_n_16_easy.json
majoritybug_trace_TPL_CONCISETRACE_dk7b_n_16_easy.json
majoritybug_trace_TPL_CONCISETRACE_llama8b_n_16_easy.json
majoritybug_trace_TPL_CONCISETRACE_marcon-o1_n_16_easy.json
majoritybug_trace_TPL_CONCISETRACE_phi4_n_16_easy.json
majoritybug_trace_TPL_CONCISETRACE_qwen7b_n_16_easy.json
majoritybug_trace_TPL_NEXT_dk7b_n_16_easy.json
majoritybug_trace_TPL_NEXT_llama8b_n_16_easy.json
majoritybug_trace_TPL_NEXT_marcon-o1_n_16_easy.json
majoritybug_trace_TPL_NEXT_phi4_n_16_easy.json
majoritybug_trace_TPL_NEXT_qwen7b_n_16_easy.json
majoritybug_trace_TPL_OUR01_dk7b_n_16_easy.json
majoritybug_trace_TPL_OUR01_llama8b_n_16_easy.json
majoritybug_trace_TPL_OUR01_marcon-o1_n_16_easy.json
majoritybug_trace_TPL_OUR01_phi4_n_16_easy.json
majoritybug_trace_TPL_OUR01_qwen7b_n_16_easy.json
"""

flist="""
majority_4omini_n_16_easy.json
majority_dk7b_n_16_easy.json
majority_dkv3_n_16_easy.json
majority_llama8b_n_16_easy.json
majority_llmjudge__qwen7b_n_16_easy.json
majority_llmscore__qwen7b_n_16_easy.json
majority_llmtool__qwen7b_n_16_easy.json
majority_marcon-o1_n_16_easy.json
majority_phi4_n_16_easy.json
majority_qwen7b_n_16_easy.json
majoritybug_trace_TPL_CODEEXECUTOR_4omini_n_16_easy.json
majoritybug_trace_TPL_CODEEXECUTOR_dk7b_n_16_easy.json
majoritybug_trace_TPL_CODEEXECUTOR_dkv3_n_16_easy.json
majoritybug_trace_TPL_CODEEXECUTOR_llama8b_n_16_easy.json
majoritybug_trace_TPL_CODEEXECUTOR_marcon-o1_n_16_easy.json
majoritybug_trace_TPL_CODEEXECUTOR_phi4_n_16_easy.json
majoritybug_trace_TPL_CODEEXECUTOR_qwen7b_n_16_easy.json
majoritybug_trace_TPL_CONCISETRACE_4omini_n_16_easy.json
majoritybug_trace_TPL_CONCISETRACE_dk7b_n_16_easy.json
majoritybug_trace_TPL_CONCISETRACE_dkv3_n_16_easy.json
majoritybug_trace_TPL_CONCISETRACE_llama8b_n_16_easy.json
majoritybug_trace_TPL_CONCISETRACE_marcon-o1_n_16_easy.json
majoritybug_trace_TPL_CONCISETRACE_phi4_n_16_easy.json
majoritybug_trace_TPL_CONCISETRACE_qwen7b_n_16_easy.json
majoritybug_trace_TPL_NEXT_4omini_n_16_easy.json
majoritybug_trace_TPL_NEXT_dk7b_n_16_easy.json
majoritybug_trace_TPL_NEXT_dkv3_n_16_easy.json
majoritybug_trace_TPL_NEXT_llama8b_n_16_easy.json
majoritybug_trace_TPL_NEXT_marcon-o1_n_16_easy.json
majoritybug_trace_TPL_NEXT_phi4_n_16_easy.json
majoritybug_trace_TPL_NEXT_qwen7b_n_16_easy.json
majoritybug_trace_TPL_OUR01_4omini_n_16_easy.json
majoritybug_trace_TPL_OUR01_dk7b_n_16_easy.json
majoritybug_trace_TPL_OUR01_dkv3_n_16_easy.json
majoritybug_trace_TPL_OUR01_llama8b_n_16_easy.json
majoritybug_trace_TPL_OUR01_marcon-o1_n_16_easy.json
majoritybug_trace_TPL_OUR01_phi4_n_16_easy.json
majoritybug_trace_TPL_OUR01_qwen7b_n_16_easy.json
"""

flist="""
sec5__revision_refine_dk7b_easy_max_round_5.json
sec5__revision_refine_llama8b_easy_max_round_5.json
sec5__revision_refine_marcon-o1_easy_max_round_5.json
sec5__revision_refine_phi4_easy_max_round_5.json
sec5__revision_refine_qwen_7b_easy_max_round_5.json
sec5_bug_trace_TPL_CODEEXECUTOR_revision_bug_trace_TPL_CODEEXECUTOR_last_qwen_7b_easy_max_round_5.json
sec5_bug_trace_TPL_CODEEXECUTOR_revision_refine_dk7b_easy_max_round_5.json
sec5_bug_trace_TPL_CODEEXECUTOR_revision_refine_llama8b_easy_max_round_5.json
sec5_bug_trace_TPL_CODEEXECUTOR_revision_refine_marcon-o1_easy_max_round_5.json
sec5_bug_trace_TPL_CODEEXECUTOR_revision_refine_phi4_easy_max_round_5.json
sec5_bug_trace_TPL_CODEEXECUTOR_revision_refine_qwen_7b_easy_max_round_5.json
sec5_bug_trace_TPL_CODEEXECUTORrevision_vanilla_4omini_easy_max_round_5.json
sec5_bug_trace_TPL_CODEEXECUTORrevision_vanilla_dk7b_easy_max_round_5.json
sec5_bug_trace_TPL_CODEEXECUTORrevision_vanilla_dkv3_easy_max_round_5.json
sec5_bug_trace_TPL_CODEEXECUTORrevision_vanilla_llama8b_easy_max_round_5.json
sec5_bug_trace_TPL_CODEEXECUTORrevision_vanilla_marcon-o1_easy_max_round_5.json
sec5_bug_trace_TPL_CODEEXECUTORrevision_vanilla_phi4_easy_max_round_5.json
sec5_bug_trace_TPL_CODEEXECUTORrevision_vanilla_qwen_7b_easy_max_round_5.json
sec5_bug_trace_TPL_CONCISETRACE_revision_bug_trace_TPL_CONCISETRACE_last_qwen_7b_easy_max_round_5.json
sec5_bug_trace_TPL_CONCISETRACE_revision_refine_dk7b_easy_max_round_5.json
sec5_bug_trace_TPL_CONCISETRACE_revision_refine_llama8b_easy_max_round_5.json
sec5_bug_trace_TPL_CONCISETRACE_revision_refine_marcon-o1_easy_max_round_5.json
sec5_bug_trace_TPL_CONCISETRACE_revision_refine_phi4_easy_max_round_5.json
sec5_bug_trace_TPL_CONCISETRACE_revision_refine_qwen_7b_easy_max_round_5.json
sec5_bug_trace_TPL_CONCISETRACErevision_vanilla_4omini_easy_max_round_5.json
sec5_bug_trace_TPL_CONCISETRACErevision_vanilla_dk7b_easy_max_round_5.json
sec5_bug_trace_TPL_CONCISETRACErevision_vanilla_dkv3_easy_max_round_5.json
sec5_bug_trace_TPL_CONCISETRACErevision_vanilla_llama8b_easy_max_round_5.json
sec5_bug_trace_TPL_CONCISETRACErevision_vanilla_marcon-o1_easy_max_round_5.json
sec5_bug_trace_TPL_CONCISETRACErevision_vanilla_phi4_easy_max_round_5.json
sec5_bug_trace_TPL_CONCISETRACErevision_vanilla_qwen_7b_easy_max_round_5.json
sec5_bug_trace_TPL_NEXT_revision_bug_trace_TPL_NEXT_last_qwen_7b_easy_max_round_5.json
sec5_bug_trace_TPL_NEXT_revision_refine_dk7b_easy_max_round_5.json
sec5_bug_trace_TPL_NEXT_revision_refine_llama8b_easy_max_round_5.json
sec5_bug_trace_TPL_NEXT_revision_refine_marcon-o1_easy_max_round_5.json
sec5_bug_trace_TPL_NEXT_revision_refine_phi4_easy_max_round_5.json
sec5_bug_trace_TPL_NEXT_revision_refine_qwen_7b_easy_max_round_5.json
sec5_bug_trace_TPL_NEXTrevision_last_qwen_7b_easy_max_round_5_with_4o_debug.json
sec5_bug_trace_TPL_NEXTrevision_vanilla_4omini_easy_max_round_5.json
sec5_bug_trace_TPL_NEXTrevision_vanilla_dk7b_easy_max_round_5.json
sec5_bug_trace_TPL_NEXTrevision_vanilla_dkv3_easy_max_round_5.json
sec5_bug_trace_TPL_NEXTrevision_vanilla_llama8b_easy_max_round_5.json
sec5_bug_trace_TPL_NEXTrevision_vanilla_marcon-o1_easy_max_round_5.json
sec5_bug_trace_TPL_NEXTrevision_vanilla_phi4_easy_max_round_5.json
sec5_bug_trace_TPL_NEXTrevision_vanilla_qwen_7b_easy_max_round_5.json
sec5_bug_trace_TPL_OUR01_revision_bug_trace_TPL_OUR01_last_qwen_7b_easy_max_round_5.json
sec5_bug_trace_TPL_OUR01_revision_refine_dk7b_easy_max_round_5.json
sec5_bug_trace_TPL_OUR01_revision_refine_llama8b_easy_max_round_5.json
sec5_bug_trace_TPL_OUR01_revision_refine_marcon-o1_easy_max_round_5.json
sec5_bug_trace_TPL_OUR01_revision_refine_phi4_easy_max_round_5.json
sec5_bug_trace_TPL_OUR01_revision_refine_qwen_7b_easy_max_round_5.json
sec5_bug_trace_TPL_OUR01revision_last_qwen_7b_easy_max_round_5_with_4o_debug.json
sec5_bug_trace_TPL_OUR01revision_vanilla_4omini_easy_max_round_5.json
sec5_bug_trace_TPL_OUR01revision_vanilla_dk7b_easy_max_round_5.json
sec5_bug_trace_TPL_OUR01revision_vanilla_dkv3_easy_max_round_5.json
sec5_bug_trace_TPL_OUR01revision_vanilla_llama8b_easy_max_round_5.json
sec5_bug_trace_TPL_OUR01revision_vanilla_marcon-o1_easy_max_round_5.json
sec5_bug_trace_TPL_OUR01revision_vanilla_phi4_easy_max_round_5.json
sec5_bug_trace_TPL_OUR01revision_vanilla_qwen_7b_easy_max_round_5.json
sec5_revision_vanilla_4omini_easy_max_round_5.json
sec5_revision_vanilla_dk7b_easy_max_round_5.json
sec5_revision_vanilla_dkv3_easy_max_round_5.json
sec5_revision_vanilla_llama8b_easy_max_round_5.json
sec5_revision_vanilla_marcon-o1_easy_max_round_5.json
sec5_revision_vanilla_phi4_easy_max_round_5.json
sec5_revision_vanilla_qwen_7b_easy_max_round_5.json
"""


flist="""
baselines_4omini_easy.json
baselines_cot_4omini_easy.json
baselines_cot_dk7b_easy.json
baselines_cot_dkv3_easy.json
baselines_cot_llama8b_easy.json
baselines_cot_macro1_easy.json
baselines_cot_phi4_easy.json
baselines_cot_qwen7b_easy.json
baselines_cot_qwen7b_hard.json
baselines_cot_qwen7b_medium.json
baselines_dk7b_easy.json
baselines_dk7b_hard.json
baselines_dk7b_medium.json
baselines_dkv3_easy.json
baselines_greedy_4omini_easy.json
baselines_greedy_dk7b_easy.json
baselines_greedy_dkv3_easy.json
baselines_greedy_llama8b_easy.json
baselines_greedy_macro1_easy.json
baselines_greedy_phi4_easy.json
baselines_greedy_qwen7b_easy.json
baselines_greedy_qwen7b_hard.json
baselines_greedy_qwen7b_medium.json
baselines_llama8b_easy.json
baselines_llama8b_hard.json
baselines_llama8b_medium.json
baselines_marcon-o1_easy.json
baselines_marcon-o1_hard.json
baselines_marcon-o1_medium.json
baselines_phi4_easy.json
baselines_phi4_hard.json
baselines_phi4_medium.json
baselines_qwen7b_easy.json
baselines_qwen7b_hard.json
baselines_qwen7b_medium.json
"""





flist="""
baselines_cot_dkv3_easy.json
baselines_dkv3_easy.json
baselines_greedy_dkv3_easy.json
majority_dkv3_n_16_easy.json
majoritybug_trace_TPL_CODEEXECUTOR_dkv3_n_16_easy.json
majoritybug_trace_TPL_CONCISETRACE_dkv3_n_16_easy.json
majoritybug_trace_TPL_NEXT_dkv3_n_16_easy.json
majoritybug_trace_TPL_OUR01_dkv3_n_16_easy.json
sec5_bug_trace_TPL_CODEEXECUTORrevision_vanilla_dkv3_easy_max_round_5.json
sec5_bug_trace_TPL_CONCISETRACErevision_vanilla_dkv3_easy_max_round_5.json
sec5_bug_trace_TPL_NEXTrevision_vanilla_dkv3_easy_max_round_5.json
sec5_bug_trace_TPL_OUR01revision_vanilla_dkv3_easy_max_round_5.json
sec5_revision_vanilla_dkv3_easy_max_round_5.json
"""


if __name__=="__main__":
    # print ("====>")
    # overall_zeroshot( search_dir = search_dir )
    # print ("<====")
    # print ("====>")
    # overall_seq_vanilla( search_dir = search_dir )
    # print ("<====")
    # print ("====>")
    # overall_zeroshot( search_dir = search_dir, prefix="__mbpp" )
    # print ("<====")
    # print ("====>")
    # overall_seq_vanilla( search_dir = search_dir, prefix="__mbpp" )



    # print ("<====")
    # print ("====>")
    # overall_voting( search_dir = search_dir  )
    # print ("<====")
    # print ("====>")
    # overall_voting( search_dir = search_dir, prefix="__mbpp" )
    #
    sear2= "/mnt/local/home_dir/wj_code/dl_trace/testscaling_trace/test_skythought__test/results_sky_v2"
    flist = [x.strip() for x in flist.split()]
    flist = list(set(flist))
    flist = list( sorted(flist)  )
    sec5_lcb( search_dir = sear2 , flist=flist)
    
    
    
    
    
#
# baselines_cot_qwen7b_easy.json
# baselines_dk7b_easy.json
# baselines_greedy_qwen7b_easy.json
# baselines_llama8b_easy.json
# baselines_marcon-o1_easy.json
# baselines_phi4_easy.json
# baselines_qwen7b_easy.json
# final_4omini_n_16_debug_public3_select_oracle_easy.json
# final__qwen7b_n_1_debug_public3_select_random_easy.json
# final_bug_trace_TPL_CODEEXECUTOR_dk7b_n_1_debug_public3_select_random_easy.json
# final_bug_trace_TPL_CODEEXECUTOR_llama8b_n_1_debug_public3_select_random_easy.json
# final_bug_trace_TPL_CODEEXECUTOR_marcon-o1_n_1_debug_public3_select_random_easy.json
# final_bug_trace_TPL_CODEEXECUTOR_phi4_n_1_debug_public3_select_random_easy.json
# final_bug_trace_TPL_CODEEXECUTOR_qwen7b_n1_debug_public3_select_random_easy.json
# final_bug_trace_TPL_CODEEXECUTOR_qwen7b_n_1_debug_public3_select_random_easy.json
# final_bug_trace_TPL_CODEEXECUTORqwen7b_n_16_debug_public3_select_oracle_easy.json
# final_bug_trace_TPL_CONCISETRACE_dk7b_n_1_debug_public3_select_random_easy.json
# final_bug_trace_TPL_CONCISETRACE_llama8b_n_1_debug_public3_select_random_easy.json
# final_bug_trace_TPL_CONCISETRACE_marcon-o1_n_1_debug_public3_select_random_easy.json
# final_bug_trace_TPL_CONCISETRACE_phi4_n_1_debug_public3_select_random_easy.json
# final_bug_trace_TPL_CONCISETRACE_qwen7b_n1_debug_public3_select_random_easy.json
# final_bug_trace_TPL_CONCISETRACE_qwen7b_n_1_debug_public3_select_random_easy.json
# final_bug_trace_TPL_CONCISETRACEqwen7b_n_16_debug_public3_select_oracle_easy.json
# final_bug_trace_TPL_NEXT_dk7b_n_1_debug_public3_select_random_easy.json
# final_bug_trace_TPL_NEXT_llama8b_n_1_debug_public3_select_random_easy.json
# final_bug_trace_TPL_NEXT_marcon-o1_n_1_debug_public3_select_random_easy.json
# final_bug_trace_TPL_NEXT_phi4_n_1_debug_public3_select_random_easy.json
# final_bug_trace_TPL_NEXT_qwen7b_n1_debug_public3_select_random_easy.json
# final_bug_trace_TPL_NEXT_qwen7b_n_1_debug_public3_select_random_easy.json
# final_bug_trace_TPL_NEXTqwen7b_n_16_debug_public3_select_oracle_easy.json
# final_bug_trace_TPL_OUR01_dk7b_n_1_debug_public3_select_random_easy.json
# final_bug_trace_TPL_OUR01_llama8b_n_1_debug_public3_select_random_easy.json
# final_bug_trace_TPL_OUR01_marcon-o1_n_1_debug_public3_select_random_easy.json
# final_bug_trace_TPL_OUR01_phi4_n_1_debug_public3_select_random_easy.json
# final_bug_trace_TPL_OUR01_qwen7b_n1_debug_public3_select_random_easy.json
# final_bug_trace_TPL_OUR01_qwen7b_n_1_debug_public3_select_random_easy.json
# final_bug_trace_TPL_OUR01qwen7b_n_16_debug_public3_select_oracle_easy.json
# final_no_trace_dk7b_n_1_debug_public3_select_random_easy.json
# final_no_trace_llama8b_n_1_debug_public3_select_random_easy.json
# final_no_trace_marcon-o1_n_1_debug_public3_select_random_easy.json
# final_no_trace_phi4_n_1_debug_public3_select_random_easy.json
# final_no_trace_qwen7b_n1_debug_public3_select_random_easy.json
# final_qwen7b_n_16_debug_public3_select_oracle_easy.json
# sec5__revision_refine_qwen_7b_easy_max_round_5.json
# sec5_bug_trace_TPL_CODEEXECUTOR_revision_bug_trace_TPL_CODEEXECUTOR_last_qwen_7b_easy_max_round_5.json
# sec5_bug_trace_TPL_CODEEXECUTOR_revision_refine_qwen_7b_easy_max_round_5.json
# sec5_bug_trace_TPL_CODEEXECUTORrevision_vanilla_qwen_7b_easy_max_round_5.json
# sec5_bug_trace_TPL_CONCISETRACE_revision_bug_trace_TPL_CONCISETRACE_last_qwen_7b_easy_max_round_5.json
# sec5_bug_trace_TPL_CONCISETRACE_revision_refine_qwen_7b_easy_max_round_5.json
# sec5_bug_trace_TPL_CONCISETRACErevision_vanilla_qwen_7b_easy_max_round_5.json
# sec5_bug_trace_TPL_NEXT_revision_bug_trace_TPL_NEXT_last_qwen_7b_easy_max_round_5.json
# sec5_bug_trace_TPL_NEXT_revision_refine_qwen_7b_easy_max_round_5.json
# sec5_bug_trace_TPL_NEXTrevision_last_qwen_7b_easy_max_round_5_with_4o_debug.json
# sec5_bug_trace_TPL_NEXTrevision_vanilla_qwen_7b_easy_max_round_5.json
# sec5_bug_trace_TPL_OUR01_revision_bug_trace_TPL_OUR01_last_qwen_7b_easy_max_round_5.json
# sec5_bug_trace_TPL_OUR01_revision_refine_qwen_7b_easy_max_round_5.json
# sec5_bug_trace_TPL_OUR01revision_last_qwen_7b_easy_max_round_5_with_4o_debug.json
# sec5_bug_trace_TPL_OUR01revision_vanilla_qwen_7b_easy_max_round_5.json
# sec5_revision_vanilla_qwen_7b_easy_max_round_5.json
