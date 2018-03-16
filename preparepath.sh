
if [ -d '/nms/local' ]
then :
else
	mkdir /nms/local
fi

if echo $PATH |  grep '/nms/local/python2.7/bin' >/dev/null 2>&1
then :
else
	cd /home/$USER
	sed -i '$a\#for python2.7' .bash_profile
	sed -i '$a\export PATH=.:/nms/scandir/bin:/nms/local/python2.7/bin:$PATH' .bash_profile
fi
