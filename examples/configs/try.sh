#!/bin/sh

#edit topogen.py
cd ~/dengli/nettopbuilder/examples/configs
echo "Input node number to be created:"
read num
sed -i "206c name = \"n${num}\"" topogen.py
sed -i "207c node_num = ${num}" topogen.py
python3 topogen.py

#
#tmux operation
#new window -s name -d move to backconsole 
#perfect suffix -d makes process simple

rm -rf simple.txt
rm -rf output.txt

#window builder
tmux new -s topogen -d
tmux new-window -n builder -d  
tmux send -t builder 'cd ~/dengli/nettopbuilder&& ./nettopbuilder' ENTER 
echo "window builder done"

tmux new-window -n inputer -d
# wait 2s to ensure the nettopbuilder is begin
sleep 2

#window inputer
tmux capture-pane -t builder -S -
tmux send -t inputer "cd ~/dengli/nettopbuilder&&curl -X POST http://localhost:8083/1.0/config/n${num} --data @examples/configs/n${num}.json&&sleep 2&&curl http://localhost:8083/1.0/action/create/n${num}"  ENTER 

tmux save-buffer output.txt

#examine if the creating process is done
tmux capture-pane -t builder -S -
tmux save-buffer output.txt

#tmux detach
tmux send -t 0 "tmux detach" ENTER
tmux attach
tmux capture-pane -t builder -S -
tmux save-buffer output.txt
#tmux show-buffer
#tmux send -t 0 "tmux detach" ENTER



sleep 1


#  Worker n10-n10-192.168.31.15(create) started
#grep '(create) started' output.txt
while(!(grep '(create) started' output.txt))
	do
		tmux capture-pane -t builder -S -
		tmux save-buffer output.txt
		tmux show-buffer
		grep '(create) started' output.txt >>simple.txt
	done

while(!(grep '(create) done' output.txt))
do
	tmux capture-pane -t builder -S -
	tmux save-buffer output.txt
	tmux show-buffer
#cpu info
	rm -rf cpu.txt
	echo "cpu-n${num}" >> cpu.txt
	echo "create:"
	echo "create:">>cpu.txt
	b=`vmstat 1 |head -n 4 |tail -n 1 |awk '{print $ 13}'`
	if [ $b -ge 80 ];then
	        echo "cpu >80%,restart server----------------" >>cpu.txt
	else
		        #echo "`date +%x%T ` cpu:$b"
			        echo "`date` cpu:$b%"
				        echo "`date` cpu:$b%">>cpu.txt
				fi
				#

	c=`vmstat 1 |head -n 4 |tail -n 1 |awk '{print $ 4}'`
	d=`vmstat 1 |head -n 4 |tail -n 1 |awk '{print $ 3}'`
	echo "`date` Free memory:$c KB , Swpd memory: $d KB"
	echo "`date` Free memory:$c KB , Swpd memory: $d KB">>cpu.txt
        sleep 1
done

sleep 2
#grep '(create) started' output.txt >>simple.txt
grep '(create) done' output.txt >> simple.txt
echo "window inputer create done"

sleep 1
# do the starting process

tmux send -t inputer "curl http://localhost:8083/1.0/action/start/n${num}" ENTER
echo "waiting for the starting process"
#tmux detach

tmux send -t 0 "tmux detach" ENTER
tmux attach
tmux capture-pane -t builder -S -
tmux save-buffer output.txt


sleep 5

grep '(start) started' output.txt 
#grep '(start) started' output.txt >> simple.txt



while(!(grep '(start) done' output.txt ))
do
	        tmux capture-pane -t builder -S -
		tmux save-buffer output.txt
		
		tmux show-buffer
		#
		#cpu info
		
		echo "start:"
		echo "start:">>cpu.txt
		b=`vmstat 1 |head -n 4 |tail -n 1 |awk '{print $ 13}'`
		if [ $b -ge 80 ];
		then        echo "cpu >80%,restart server----------------" >>cpu.txt
		else
			#echo "`date +%x%T ` cpu:$b"
			echo "`date` cpu:$b%"
			echo "`date` cpu:$b%">>cpu.txt
		fi

		#
		 c=`vmstat 1 |head -n 4 |tail -n 1 |awk '{print $ 4}'`
		         d=`vmstat 1 |head -n 4 |tail -n 1 |awk '{print $ 3}'`
			         echo "`date` Free memory:$c KB , Swpd memory: $d KB"
				 echo "`date` Free memory:$c KB , Swpd memory: $d KB">>cpu.txt

				sleep 1
done    
grep '(start) started' output.txt >> simple.txt
grep '(start) done' output.txt >> simple.txt

echo "window inputer start done"

#
      #echo "continue? Y or N"



#read flag    
#if [ $flag = "Y" ] ; then    
#	echo "get Y"
#elif [ $flag = "y" ] ; then  
#	echo "get y"
#elif [ $flag = "N" ] ; then
#	echo "get N"
#	exit
#elif [$flag="n"];then
#	echo "get n"
#	exit
#else 
#	echo "continue"
#fi     #ifend

#change window to tmux to view results
#stopping process the same way to code
tmux send -t inputer "curl http://localhost:8083/1.0/action/stop/n${num}" ENTER
echo "waiting for the stopping process"
#tmux detach

tmux send -t 0 "tmux detach" ENTER
tmux attach
tmux capture-pane -t builder -S -
tmux save-buffer output.txt



sleep 5

grep '(stop) started' output.txt 
#grep '(stop) started' output.txt >> simple.txt

while(!(grep '(stop) done' output.txt))
do

       	tmux capture-pane -t builder -S -
            tmux save-buffer output.txt
	    tmux show-buffer
	#cpu info
	#rm -rf cpu.txt

	echo "stop:"
	echo "stop:">>cpu.txt
	b=`vmstat 1 |head -n 4 |tail -n 1 |awk '{print $ 13}'`
	if [ $b -ge 80 ];then
		echo "cpu >80%,restart server----------------" >>cpu.txt
	else
		#echo "`date +%x%T ` cpu:$b"
		echo "`date` cpu:$b%"
		echo "`date` cpu:$b%">>cpu.txt
	fi
	#

         c=`vmstat 1 |head -n 4 |tail -n 1 |awk '{print $ 4}'`
         d=`vmstat 1 |head -n 4 |tail -n 1 |awk '{print $ 3}'`
	 echo "`date` Free memory:$c KB , Swpd memory: $d KB"
	 echo "`date` Free memory:$c KB , Swpd memory: $d KB">>cpu.txt
	sleep 1
done
grep '(stop) started' output.txt >> simple.txt
grep '(stop) done' output.txt >> simple.txt

      echo "window inputer stop done"

sleep 1
#the destroy process

tmux send -t inputer "curl http://localhost:8083/1.0/action/destroy/n${num}" ENTER
echo "waiting for the destroying process"

tmux send -t 0 "tmux detach" ENTER
tmux attach
tmux capture-pane -t builder -S -
tmux save-buffer output.txt



sleep 5


grep '(delete) started' output.txt
#grep '(delete) started' output.txt >> simple.txt

while(!(grep '(delete) done' output.txt ))
do
	     tmux capture-pane -t builder -S -
	     tmux save-buffer output.txt
	     
	     tmux show-buffer
	     #cpu info
	#rm -rf cpu.txt

	echo "delete:"
	echo "delete:">>cpu.txt
        b=`vmstat 1 |head -n 4 |tail -n 1 |awk '{print $ 13}'`
	if [ $b -ge 80 ];then
		echo "cpu >80%,restart server----------------" >>cpu.txt
	else
		#echo "`date +%x%T ` cpu:$b"
		echo "`date` cpu:$b%"
		echo "`date` cpu:$b%">>cpu.txt
	fi
	#     
 c=`vmstat 1 |head -n 4 |tail -n 1 |awk '{print $ 4}'`
 d=`vmstat 1 |head -n 4 |tail -n 1 |awk '{print $ 3}'`
 echo "`date` Free memory:$c KB , Swpd memory: $d KB"
 echo "`date` Free memory:$c KB , Swpd memory: $d KB">>cpu.txt
 sleep 1

done
grep '(delete) started' output.txt >> simple.txt

grep '(delete) done' output.txt >> simple.txt

      echo "window inputer delete done"



#sleep 20 #for test 
#our next goal is to extract the timestamp from the scrolling program prompts
#tmux capture-pane -t builder -S -
#tmux save-buffer output.txt


#tmux kill-window -t builder
#tmux kill-window -t input

#the final work to clean the file
echo "auto reset-all"
cd ~/dengli/nettopbuilder
./reset_all.sh

tmux send -t inputer "exit" ENTER

tmux send -t builder "exit" ENTER

tmux send -t 0 "exit" ENTER
tmux kill-server



