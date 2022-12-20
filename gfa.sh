#!/bin/bash -i

alias odgi="/home/scott/bin/odgi/bin/odgi"

shopt -s expand_aliases

IN_GFA=$1
PREFIX="${IN_GFA%.*}"

echo $PREFIX

THREADS=4

#-------------------------
# Sort

ODGI_OG=${PREFIX}.og
ODGI_LOG_FILE=${PREFIX}.og.log

(odgi build -t $THREADS -P -g $IN_GFA -o - -O | \
   odgi unchop -P -t $THREADS -i - -o - | \
   odgi sort -P -p Ygs -t $THREADS -i - -o $ODGI_OG) 2> $ODGI_LOG_FILE

#-------------------------

ODGI_GFA=${PREFIX}.og.gfa
odgi view -i $ODGI_OG -g > $ODGI_GFA

#make vcf
#vg deconstruct -P consensus -H # -e -a -t 16 /data/out/all.fa.gz.44691e7.417fcdf.20e3026.smooth.final.gfa
#bcftools stats "$vcf" > "$vcf".stats

#-------------------------

odgi viz -i $ODGI_OG -o ${PREFIX}.viz_multiqc.png \
         -x 1500 -y 500 -a 10 -I viz_
odgi viz -i $ODGI_OG -o ${PREFIX}.viz_pos_multiqc.png \
         -x 1500 -y 500 -a 10 -u -d -I viz_
odgi viz -i $ODGI_OG -o ${PREFIX}.viz_depth_multiqc.png \
         -x 1500 -y 500 -a 10 -m -I viz_
odgi viz -i $ODGI_OG -o ${PREFIX}.viz_pos_multiqc.png \
         -x 1500 -y 500 -a 10 -z -I viz_
odgi viz -i $ODGI_OG -o ${PREFIX}.viz_O_multiqc.png \
         -x 1500 -y 500 -a 10 -O -I viz_

#-------------------------

LAYOUT=${PREFIX}.lay

odgi layout -i $ODGI_OG -o $LAYOUT -T ${LAYOUT}.tsv -t $THREADS -P 

odgi draw -i $ODGI_OG -c $LAYOUT -p ${LAYOUT}.draw.png -H 1000
#odgi draw -i $ODGI_OG -c $LAYOUT -s ${LAYOUT}.draw.svg -H 1000
#odgi draw -i $ODGI_OG -c $LAYOUT -p ${LAYOUT}.draw_multiqc.png -C -w 20 -H 1000



fix="u"
odgi layout -i HGSVC_chr22_17119590_17880307.og -o ${fix}.lay -T ${fix}.lay.tsv \
  -t 4 -P --layout-initialization=u
odgi draw -i HGSVC_chr22_17119590_17880307.og -c ${fix}.lay -p ${fix}.draw.png -H 1000


