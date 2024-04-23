CHR=chr3
START=198347210
END=198855552

PREFIX=./subset_${START}_${END}
mkdir -p $PREFIX
OG=${PREFIX}/subset.og
GFA=${PREFIX}/subset.gfa

#wget https://s3-us-west-2.amazonaws.com/human-pangenomics/pangenomes/freeze/freeze1/minigraph-cactus/hprc-v1.1-mc-chm13/hprc-v1.1-mc-chm13.chroms/${CHR}.full.og

odgi extract -t 15 -P -r CHM13#${CHR}:${START}-${END} -i ${CHR}.full.og -o ${PREFIX}/extracted.og
odgi unchop -P -i ${PREFIX}/extracted.og -o ${PREFIX}/unchopped.og

#odgi view -g -i ${PREFIX}/unchopped.og > ${PREFIX}/unchopped.gfa
#odgi build -t 15 -g ${PREFIX}/unchopped.gfa -s -O -o ${PREFIX}/unchopped.og

odgi flip -t 15 -i ${PREFIX}/unchopped.og -o ${PREFIX}/flipped.og
#odgi groom -t 15 -i ${PREFIX}/flipped.og -o ${PREFIX}/groom.og

odgi sort -p Ygs -i flipped.og -o $OG

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

