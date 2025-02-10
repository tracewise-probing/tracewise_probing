cat t.xt |xargs -I {} sh -c " cp rq1_lora64_xxxx.yaml rq1_lora64_{}.yaml "


cat t.xt |xargs -I {} sh -c " sed -i -e  's/xxxxxx/{}/g'  rq1_lora64_{}.yaml "
