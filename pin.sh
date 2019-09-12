#!/bin/bash
set -x # echo on

P=$(pwd)								# save current location
exe=${1##*/}							# extract executable and input filename
cp $1 PIN/Work/$exe.out					# copy executable to pin folder
cp static.offset PIN/Work/final.offset
cp static_global.offset PIN/Work/final_global.offset
cp dependencies.p PIN/Work/
if [ $# -eq 2 ]
then
	inp=${2##*/}
	cp $2 PIN/Work/$inp					# copy input file to pin if specified
else
	inp=""
fi

cd PIN/Work								# move to pin folder
make ./obj-intel64/memtracker.so		# build the pin so
chmod +x $exe.out						# make .out runnable
make inp=$inp $exe.dump					# create the dump
# readelf -sW $exe.out | grep "OBJECT" > $exe.symtab	# collect its symtab
# awk -f merge $exe.symtab FS="\t" final_global.offset > $exe_global.offset	# link with final_global.offset
# ../PIN/pin -t obj-intel64/memtracker.so -- ./$exe.out $inp > op.txt
python pass2.py $exe.dump		# add dump info to xml
cp dynamic.xml $P
