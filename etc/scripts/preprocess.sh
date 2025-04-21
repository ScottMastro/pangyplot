GFA="static/data/cf_hifi.sv.gfa"
BED="static/data/gencode.v43.basic.annotation.bed"
PREFIX=`basename $GFA .gfa`

THREADS=16
OUT=./static/data/preprocess
mkdir -p $OUT

PREFIX=${OUT}/${PREFIX}

odgi build -t $THREADS -g $GFA -O -o ${PREFIX}.unsorted.og
odgi sort -t $THREADS -Y -i ${PREFIX}.unsorted.og -o ${PREFIX}.sorted.og
odgi normalize -t $THREADS -i ${PREFIX}.sorted.og -o ${PREFIX}.og

# zcat gencode.v43.basic.annotation.gff3.gz | grep HAVANA.gene | gff2bed > gencode.v43.basic.annotation.bed
# sed -i 's/^/id=CHM13|/' gencode.v43.basic.annotation.bed
#odgi inject -t $THREADS -b $BED -i ${PREFIX}.og -o ${PREFIX}.annotated.og

# --------------- LAYOUT FILE ----------------------------
odgi layout -t $THREADS -i ${PREFIX}.og --tsv ${PREFIX}.lay.tsv -o ${PREFIX}.lay

# --------------- GFA FILE ----------------------------
odgi view -t $THREADS -i ${PREFIX}.og -g > ${PREFIX}.gfa

cat ${PREFIX}.gfa | grep ^P | cut -f 2 | grep CHM13 > ${OUT}/reference_paths.txt
cat ${PREFIX}.gfa | grep ^S | cut -f2 > ${OUT}/segment_starts.txt
cat ${PREFIX}.gfa | grep ^S | awk '{print $2 "," length($3)-1}' > ${OUT}/segment_ends.txt
odgi position -t $THREADS -i ${PREFIX}.og --ref-paths ${OUT}/reference_paths.txt --graph-pos-file ${OUT}/segment_starts.txt > ${OUT}/start_positions.txt
odgi position -t $THREADS -i ${PREFIX}.og --ref-paths ${OUT}/reference_paths.txt --graph-pos-file ${OUT}/segment_ends.txt > ${OUT}/end_positions.txt

awk -F"[,\t]" '{print $1 "\t" $4 ":" $5+1}' ${OUT}/start_positions.txt | grep -v ^"#" | sort -k1,1 > tmp1.txt
awk -F"[,\t]" '{print $1 "\t" $4 ":" $5+1}' ${OUT}/end_positions.txt | grep -v ^"#" | sort -k1,1 > tmp2.txt

# --------------- POSITION FILE ----------------------------
join -t $'\t' tmp1.txt tmp2.txt > ${OUT}/node_positions.txt
rm tmp1.txt ; rm tmp2.txt



