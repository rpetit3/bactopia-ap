#! /bin/bash

# Update Databases
mkdir -p data/mentalist data/ariba
cd mentalist
mkdir mlst cgmlst
mentalist download_pubmlst -o mlst/ -s "Staphylococcus aureus" -k 31 --db mlst/mlst-31.db
mentalist download_cgmlst -o cgmlst/ -s "Staphylococcus aureus" -k 31 --db cgmlst/cgmlst-31.db
rm cgmlst.html dbases.xml
cd ..
tar cf - mentalist/ | gzip --best > mentalist.tar.gz
rm -rf mentalist/
date > mentalist-updated.txt


cd ariba
ariba getref megares megares
ariba prepareref -f megares.fa -m megares.tsv megares
ariba getref vfdb_core vfdb
ariba prepareref -f vfdb.fa -m vfdb.tsv vfdb
rm -rf tmp* megares.* vfdb.*
cd mlst/pubmlst_download/
mkdir mlst-blastdb
ls *.tfa | xargs -I {} makeblastdb -in {} -dbtype nucl -out mlst-blastdb/{}
cp profile.txt mlst-blastdb/
tar cf - mlst-blastdb/ | gzip --best > mlst-blastdb.tar.gz
mv mlst-blastdb.tar.gz ../../../
rm -rf mlst-blastdb/
cd ../../../
tar cf - ariba | gzip --best > ariba.tar.gz
rm -rf ariba/
date > ariba-updated.txt
date > mlst-blastdb-updated.txt
