#!/bin/bash

#data process to simple.txt

begin=""
end=""
count=1
k=0
cat simple.txt|while read line
do
  j=$[$[count]%2]
#  echo ${line}| grep -Eo "01"
 if test $j -eq 1
 then	 
 begin=`echo ${line}|grep -o "[0-9]\{2\}\:[0-9]\{2\}\:[0-9]\{2\}"`
#echo ${line}|grep -o "[0-9]\{2\}\:[0-9]\{2\}\:[0-9]\{2\}"
 else
 end=`echo ${line}|grep -o "[0-9]\{2\}\:[0-9]\{2\}\:[0-9]\{2\}"`
#echo ${line}|grep -o "[0-9]\{2\}\:[0-9]\{2\}\:[0-9]\{2\}"
fi 

if test $j -eq 1
 then
	 begin1=$(date +%s -d ${begin})

#debug use 
 	 #echo ${begin1}
else
	 end1=$(date +%s -d ${end})
         trap
#debug use
 	 #echo ${end1}
fi
# echo "${end}-${begin}" 

array=(create-time: start-time: stop-time: delete-time:)

if test $j -eq 0
then
	echo ${array[k]}

	#echo ${end1}
	#echo ${begin1}
	result=`expr ${end1} - ${begin1}`
	min=`expr ${result} / 60`	
	sec=`expr ${result} % 60`
	echo "${min} min ${sec} sec"
	let k+=1
fi
let count+=1

done


