#!/bin/bash -i

alias wfmash="/home/scott/bin/wfmash/build/bin/wfmash"
alias seqwish="/home/scott/bin/seqwish/bin/seqwish"
alias smoothxg="/home/scott/bin/smoothxg/bin/smoothxg"
alias gfaffix="/home/scott/bin/GFAffix-0.1.4/gfaffix"
alias odgi="/home/scott/bin/odgi/bin/odgi"


shopt -s expand_aliases

#pggb -i in.fa \       # input file in FASTA format
#     -o output \      # output directory
#     -n 9 \           # number of haplotypes
#     -t 16 \          # number of threads (defaults to `getconf _NPROCESSORS_ONLN`)
#     -p 90 \          # (default) minimum average nucleotide identity for a seed mapping
#     -s 5k \          # (default) segment length
#     -V 'ref:#:1000'  # make a VCF against "ref" decomposing variants >1000bp

IN_FASTA=$1
#samtools faidx $IN_FASTA

OUT_DIR=$2
mkdir -p $OUT_DIR

N_HAPS=4
SEGMENT_LENGTH=5000
MAP_PCT_ID=90
THREADS=16
CONSENSUS_PREFIX=Consensus_

N_HAPS_MINUS_1=$( echo "$N_HAPS - 1" | bc )
PAF_SPEC=W-s${SEGMENT_LENGTH}-l25000-p${MAP_PCT_ID}-n$N_HAPS_MINUS_1-k$19-H$0.001-X
PREFIX_PAF="$IN_FASTA".$(echo "$PAF_SPEC" | sha256sum | head -c 7)
WFMASH_LOG_FILE_APPROX=${PREFIX_PAF}.wfmash.approx.log
WFMASH_LOG_FILE=${PREFIX_PAF}.wfmash.log

WFMASH_PAF_APPROX=${PREFIX_PAF}.mappings.wfmash.paf
WFMASH_PAF=${PREFIX_PAF}.alignments.wfmash.paf

wfmash -s $SEGMENT_LENGTH -l 25000 -p $MAP_PCT_ID -n $N_HAPS_MINUS_1 -k 19 -H 0.001 -X \
       -t $THREADS --tmp-base $OUT_DIR "$IN_FASTA" --approx-map \
          > $WFMASH_PAF_APPROX 2> "$WFMASH_LOG_FILE_APPROX"

wfmash -s $SEGMENT_LENGTH -l 25000 -p $MAP_PCT_ID -n $N_HAPS_MINUS_1 -k 19 -H 0.001 -X \
       -t $THREADS --tmp-base $OUT_DIR "$IN_FASTA" -i $WFMASH_PAF_APPROX --invert-filtering \
          > "$WFMASH_PAF" 2> "$WFMASH_LOG_FILE"

#-------------------------

PREFIX_GFA="$PREFIX_PAF".$(echo k19-f0-B10000000 | sha256sum | head -c 7)
SEQWISH_LOG_FILE=${PREFIX_GFA}.seqwish.log
SEQWISH_GFA="$PREFIX_GFA".seqwish.gfa

seqwish -s "$IN_FASTA" -p "$WFMASH_PAF" -k 19 \
      -f 0 -g $SEQWISH_GFA -B 10000000 -t $THREADS \
      --temp-dir "$OUT_DIR" -P 2> "$SEQWISH_LOG_FILE"

#-------------------------

BLOCK_ID_MIN=$(echo "scale=4; $MAP_PCT_ID / 100.0" | bc)
PAD_MAX_DEPTH=100
MAX_DEPTH_HAP=$(echo "$PAD_MAX_DEPTH * $N_HAPS" | bc)

TARGET_POA_LENGTH=700,900,1100
POA_PARAM=1,19,39,3,81,1

# poa param (-P) suggestions from minimap2 
# - asm5, --poa-params 1,19,39,3,81,1, ~0.1 divergence
# - asm10, --poa-params 1,9,16,2,41,1, ~1 divergence
# - asm20, --poa-params 1,4,6,2,26,1, ~5% divergence
# between asm10 and asm20 ~ 1,7,11,2,33,1

PREFIX_SMOOTH="$PREFIX_GFA".$(echo h${N_HAPS}-j0-e0-d0-I${BLOCK_ID_MIN}-R0-S-O0.001  | sha256sum | head -c 7).smooth
SMOOTH_LOG_FILE=${PREFIX_SMOOTH}.log
SMOOTH_GFA=${PREFIX_SMOOTH}.gfa

smoothxg -t $THREADS -T $THREADS -g $SEQWISH_GFA -r $N_HAPS \
         --base $OUT_DIR --chop-to 100 -I $BLOCK_ID_MIN -R 0 \
         -j 0 -e 0 -O 0.001 -Y $MAX_DEPTH_HAP -d 0 -D 0 -S \
         -m ${PREFIX_SMOOTH}.maf -P $POA_PARAM -Q $CONSENSUS_PREFIX \
         -l $TARGET_POA_LENGTH -V -o $SMOOTH_GFA 2> "$SMOOTH_LOG_FILE"

#-------------------------
# Collapse redundant nodes where possible

FIX_GFA=${PREFIX_SMOOTH}.fix.gfa
FIX_LOG_FILE=${PREFIX_SMOOTH}.fix.log

gfaffix $SMOOTH_GFA -o $FIX_GFA | pigz > ${PREFIX_SMOOTH}.fix.affixes.tsv.gz 2> $FIX_LOG_FILE

#-------------------------
# Sort

ODGI_PREFIX=${PREFIX_SMOOTH}.final
ODGI_OG=${ODGI_PREFIX}.og
ODGI_GFA=${ODGI_PREFIX}.gfa
ODGI_LOG_FILE=${ODGI_PREFIX}.log

(odgi build -t $THREADS -P -g $FIX_GFA -o - -O | \
   odgi unchop -P -t $THREADS -i - -o - | \
   odgi sort -P -p Ygs --temp-dir $OUT_DIR -t $THREADS -i - -o $ODGI_OG) 2> $ODGI_LOG_FILE

#-------------------------

odgi view -i $ODGI_OG -g > $ODGI_GFA

#make vcf
#vg deconstruct -P consensus -H # -e -a -t 16 /data/out/all.fa.gz.44691e7.417fcdf.20e3026.smooth.final.gfa
#bcftools stats "$vcf" > "$vcf".stats

#-------------------------

odgi viz -i $ODGI_OG -o ${ODGI_PREFIX}.viz_multiqc.png \
         -x 1500 -y 500 -a 10 -I $CONSENSUS_PREFIX
odgi viz -i $ODGI_OG -o ${ODGI_PREFIX}.viz_pos_multiqc.png \
         -x 1500 -y 500 -a 10 -u -d -I $CONSENSUS_PREFIX
odgi viz -i $ODGI_OG -o ${ODGI_PREFIX}.viz_depth_multiqc.png \
         -x 1500 -y 500 -a 10 -m -I $CONSENSUS_PREFIX
odgi viz -i $ODGI_OG -o ${ODGI_PREFIX}.viz_pos_multiqc.png \
         -x 1500 -y 500 -a 10 -z -I $CONSENSUS_PREFIX
odgi viz -i $ODGI_OG -o ${ODGI_PREFIX}.viz_O_multiqc.png \
         -x 1500 -y 500 -a 10 -O -I $CONSENSUS_PREFIX

#-------------------------

LAYOUT=${ODGI_PREFIX}.lay

odgi layout -i $ODGI_OG -o $LAYOUT -T ${LAYOUT}.tsv -t $THREADS --temp-dir $OUT_DIR -P 

odgi draw -i $ODGI_OG -c $LAYOUT -p ${LAYOUT}.draw.png -H 1000
#odgi draw -i $ODGI_OG -c $LAYOUT -s ${LAYOUT}.draw.svg -H 1000
#odgi draw -i $ODGI_OG -c $LAYOUT -p ${LAYOUT}.draw_multiqc.png -C -w 20 -H 1000




#-------------------------

GFA="DRB1-3123_sorted.gfa"
PREFIX="DRB1-3123_sorted_simple"

vg convert -g $GFA -v > ${PREFIX}.temp.vg
vg simplify -a small -m 10000 ${PREFIX}.temp.vg > ${PREFIX}_simple.vg ; rm ${PREFIX}.temp.vg
vg view -g ${PREFIX}.simple.vg > ${PREFIX}.simple.gfa
odgi build -g ${PREFIX}.simple.gfa -o ${PREFIX}.simple.og -O
odgi layout -i ${PREFIX}.simple.og -o ${PREFIX}.simple.og.lay -P --threads 2
odgi draw -i ${PREFIX}.simple.og -c ${PREFIX}.simple.og.lay -p ${PREFIX}.simple.og.lay.png -C -w 50








