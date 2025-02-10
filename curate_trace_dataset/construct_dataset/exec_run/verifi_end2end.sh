

fdir=$1


if [ -d $fdir ]; then
	
	cd /home/xxxxxxx/wj_code/dl_execute/codeparrot___apps_metric

	find $fdir -name '*jsonl' |grep -v  finger |xargs -I {} sh -c "python step1_add_fingerprint_nouniq.py {} "

	cd /home/xxxxxxx/wj_code/dl_execute/reverse_train_data_collecting/collect_semcoder_different_rsp_LLMs

	find $fdir -name '*fingerprinted000.jsonl'|xargs -I {} -P 4 sh -c "  bash run_sanitize.sh {} "

	cd /home/xxxxxxx/wj_code/dl_execute/self-oss-instruct/selfcodealign 
	
	find $fdir -name '*fingerprinted000-extracted.jsonl' |xargs -I {} -P 3 sh -c "bash exec_filter_multi_pytest.sh {} "

fi 	
