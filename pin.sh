P=$(pwd)						# save current location
cp $1 PIN/Work/$2.out			# copy executable to pin folder
cd PIN/Work						# move to pin folder
chmod +x $2.out					# make .out runnable
make $2.dump					# create event dump
cp $2.dump $P					# move dump back to original folder
cd $P							# move back to folder
python helpers/dump2dxml.py $2.dump		# add dump info to xml
