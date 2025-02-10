

num_workers=16

fdir=$1

if [ ! -d $ffdir ]; then 
	echo "not exist folder ="$fdir
	exit 1 
fi 

cur_dir=$(pwd)

echo "### step1 unique_id "

cd /home/xxxxxxx/wj_code/dl_execute/codeparrot___apps_metric

find $fdir -name '*jsonl'|grep -v fingerprinted000 |xargs -I {}  -P $num_workers sh -c "python step1_add_fingerprint_nouniq.py {} "


echo "### step2  sanitize "

cd $cur_dir 

find $fdir -name '*fingerprinted000.jsonl' |xargs -I {}  -P $num_workers sh -c "python step2_sanitize.py {} "


echo "### step3  verify "


find $fdir -name '*fingerprinted000-extracted.jsonl' |xargs -I {}  -P $num_workers sh -c "python step3_verify.py {} "
