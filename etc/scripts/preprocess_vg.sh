#VG=$1
#OUTDIR=$2

REF=GRCh38
CHR=chrOther

OUTDIR=${CHR}
VG=${OUTDIR}/${CHR}.vg

THREADS=16

mkdir -p $OUTDIR

PREFIX=`basename $VG .vg`
PREFIX=${OUTDIR}/processed/${PREFIX}

GFA=${PREFIX}.gfa

# --------------- VG TO GFA ----------------------------
#vg view -g $VG > $GFA # outputs as GFAv2
vg convert -f --vg-algorithm -W $VG > ${PREFIX}.in.gfa

# --------------- GFA TO ODGI ----------------------------
odgi build -g ${PREFIX}.in.gfa -O -o ${PREFIX}.unsorted.og
odgi sort -Y -i ${PREFIX}.unsorted.og -o ${PREFIX}.sorted.og -P
odgi normalize -t $THREADS -i ${PREFIX}.sorted.og -o ${PREFIX}.og -P

# --------------- LAYOUT FILE ----------------------------
odgi layout -t $THREADS -i ${PREFIX}.og --tsv ${PREFIX}.lay.tsv -o ${PREFIX}.lay

# --------------- GFA FILE ----------------------------
odgi view -t $THREADS -i ${PREFIX}.og -g > ${PREFIX}.gfa

cat ${PREFIX}.gfa | grep ^P | cut -f 2 | grep $REF > ${OUTDIR}/reference_paths.txt
cat ${PREFIX}.gfa | grep ^S | cut -f2 > ${OUTDIR}/segment_starts.txt
cat ${PREFIX}.gfa | grep ^S | awk '{print $2 "," length($3)-1}' > ${OUTDIR}/segment_ends.txt
odgi position -t $THREADS -i ${PREFIX}.og --ref-paths ${OUTDIR}/reference_paths.txt --graph-pos-file ${OUTDIR}/segment_starts.txt > ${OUTDIR}/start_positions.txt
odgi position -t $THREADS -i ${PREFIX}.og --ref-paths ${OUTDIR}/reference_paths.txt --graph-pos-file ${OUTDIR}/segment_ends.txt > ${OUTDIR}/end_positions.txt

awk -F"[,\t]" '{print $1 "\t" $4 ":" $5+1}' ${OUTDIR}/start_positions.txt | grep -v ^"#" | sort -k1,1 > tmp1.txt
awk -F"[,\t]" '{print $1 "\t" $4 ":" $5+1}' ${OUTDIR}/end_positions.txt | grep -v ^"#" | sort -k1,1 > tmp2.txt

# --------------- POSITION FILE ----------------------------
join -t $'\t' tmp1.txt tmp2.txt > ${OUTDIR}/node_positions.txt
rm tmp1.txt ; rm tmp2.txt



