cd /nms

sed -i '$a\#for python2.7' .bash_profile
sed -i '$a\export PATH=.:/nms/scandir/bin:/nms/local/python2.7/bin:$PATH' .bash_profile

mkdir scandir
mkdir scandir/bin
mkdir scandir/config
mkdir scandir/log

