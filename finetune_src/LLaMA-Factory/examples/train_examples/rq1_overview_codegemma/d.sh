cat t.xt |xargs -I {} sh -c " cp rq1_full_xxxx.yaml rq1_full_{}.yaml "


cat t.xt |xargs -I {} sh -c " sed -i -e  's/xxxxxx/{}/g'  rq1_full_{}.yaml "