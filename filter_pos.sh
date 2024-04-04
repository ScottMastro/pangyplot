CHR=chr3
START=198347210
END=198855552
#wget https://s3-us-west-2.amazonaws.com/human-pangenomics/pangenomes/freeze/freeze1/minigraph-cactus/hprc-v1.1-mc-chm13/hprc-v1.1-mc-chm13.chroms/${CHR}.full.og

PREFIX=./subset_${START}_${END}
mkdir -p $PREFIX

OG=${PREFIX}/subset.og
GFA=${PREFIX}/subset.gfa

odgi extract -t 15 -P -r CHM13#${CHR}:${START}-${END} -i ${CHR}.full.og -o ${PREFIX}/extracted.og
odgi unchop -P -i ${PREFIX}/extracted.og -o ${PREFIX}/unchopped.og
odgi view -g -i ${PREFIX}/unchopped.og > ${PREFIX}/unchopped.gfa
odgi build -t 15 -g ${PREFIX}/unchopped.gfa -s -O -o $OG
odgi view -g -i $OG > $GFA

PATHNAME=`cat $GFA | grep ^P | grep CHM13 | cut -f2`
PATHDETAILS=${PATHNAME#*:}
PATHSTART=${PATHDETAILS%-*}
PATHEND=${PATHDETAILS#*-}


odgi layout -t 15 -i $OG --tsv ${PREFIX}/subset.lay.tsv -o ${PREFIX}/subset.lay

cat $GFA | grep ^S | cut -f2 > ${PREFIX}/segment_starts.txt
odgi position -t 15 -i $OG -r $PATHNAME --graph-pos-file ${PREFIX}/segment_starts.txt > ${PREFIX}/start_positions.txt
rm ${PREFIX}/segment_starts.txt

cat $GFA | grep ^S | awk '{print $2 "," length($3)-1}' > ${PREFIX}/segment_ends.txt
odgi position -t 15 -i $OG -r $PATHNAME --graph-pos-file ${PREFIX}/segment_ends.txt > ${PREFIX}/end_positions.txt
rm ${PREFIX}/segment_ends.txt

awk -F"[,\t]" -v pathStart="$PATHSTART" '{split($4, pos, ":"); print $1 "\t" pos[1] ":" $7+$5+1+pathStart}' ${PREFIX}/start_positions.txt | grep -v ^"#" | sort -n -k1,1 > ${PREFIX}/tmp1.txt
awk -F"[,\t]" -v pathStart="$PATHSTART" '{split($4, pos, ":"); print $1 "\t" pos[1] ":" $7+$5+1+pathStart}' ${PREFIX}/end_positions.txt | grep -v ^"#" | sort -n -k1,1 > ${PREFIX}/tmp2.txt

join -t $'\t' ${PREFIX}/tmp1.txt ${PREFIX}/tmp2.txt > ${PREFIX}/subset.positions.txt
rm ${PREFIX}/tmp1.txt ; rm ${PREFIX}/tmp2.txt





#OLD STUFF BELOW


awk -F"[,\t]" '{split($4, pos, ":"); print $1 "\t" pos[1] ":" $5+1+198329888}' ${PREFIX}/start_positions.txt | grep -v ^"#" | sort -n -k1,1 > ${PREFIX}/tmp1.txt
awk -F"[,\t]" '{split($4, pos, ":"); print $1 "\t" pos[1] ":" $5+1+198329888}' ${PREFIX}/end_positions.txt | grep -v ^"#" | sort -n -k1,1 > ${PREFIX}/tmp2.txt

# --------------- POSITION FILE ----------------------------





#get a list of nodes to grab (could use a different extract method but this works)
awk -F'\t' '{ split($2, start, ":"); split($3, end, ":");
    if (start[2] >= 198347210 && end[2] <= 198855552)
        print $1}' node_positions.txt > ${PREFIX}/filtered_nodes.txt

#other extraction method
#odgi extract -E -r CHM13#chr3:198347210-198855552 -i chr3.full.og -o extracted.og

OG=${PREFIX}/subset.og
GFA=${PREFIX}/subset.gfa
odgi extract -O -i chr3.d9.og --node-list ${PREFIX}/filtered_nodes.txt --context-bases 1000 -o ${PREFIX}/subset.extract.og

#must remove short paths that prevent normalization
odgi view -g -i ${PREFIX}/subset.extract.og > $GFA
cat $GFA | grep -v ^P > ${PREFIX}/cat1.txt
cat $GFA | grep ^P | grep CHM13 > ${PREFIX}/cat2.txt
cat $GFA | grep ^P | grep GRCh38 > ${PREFIX}/cat3.txt
cat ${PREFIX}/cat*.txt > $GFA

odgi build -g $GFA -O -o ${PREFIX}/subset.abnormal.og
odgi normalize -i ${PREFIX}/subset.abnormal.og -o $OG
odgi view -g -i $OG > $GFA

odgi layout -i $OG --tsv ${PREFIX}/subset.lay.tsv -o ${PREFIX}/subset.lay

cat $GFA | grep ^S | cut -f2 > ${PREFIX}/segment_starts.txt
odgi position -i $OG -r $PATHNAME --graph-pos-file ${PREFIX}/segment_starts.txt > ${PREFIX}/start_positions.txt
rm ${PREFIX}/segment_starts.txt

cat $GFA | grep ^S | awk '{print $2 "," length($3)-1}' > ${PREFIX}/segment_ends.txt
odgi position -i $OG -r $PATHNAME --graph-pos-file ${PREFIX}/segment_ends.txt > ${PREFIX}/end_positions.txt
rm ${PREFIX}/segment_ends.txt


awk -F"[,\t]" '{split($4, pos, ":"); print $1 "\t" pos[1] ":" $5+1+198329888}' ${PREFIX}/start_positions.txt | grep -v ^"#" | sort -n -k1,1 > ${PREFIX}/tmp1.txt
awk -F"[,\t]" '{split($4, pos, ":"); print $1 "\t" pos[1] ":" $5+1+198329888}' ${PREFIX}/end_positions.txt | grep -v ^"#" | sort -n -k1,1 > ${PREFIX}/tmp2.txt

# --------------- POSITION FILE ----------------------------

join -t $'\t' ${PREFIX}/tmp1.txt ${PREFIX}/tmp2.txt > ${PREFIX}/subset.positions.txt
rm ${PREFIX}/tmp1.txt ; rm ${PREFIX}/tmp2.txt


