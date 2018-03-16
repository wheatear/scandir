cd /nms
sed -i '$a\#for trap chinese word' .bash_profile
sed -i '$a\export LANG='zh_CN.gbk'' .bash_profile
