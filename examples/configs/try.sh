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

#window builder
tmux new -s topogen -d
tmux new-window -n builder -d  
tmux send -t builder 'cd ~/dengli/nettopbuilder&& ./nettopbuilder' ENTER 
echo "window builder done"

tmux new-window -n inputer -d
# wait 2s to ensure the nettopbuilder is begin
sleep 2

#window inputer
tmux send -t inputer "cd ~/dengli/nettopbuilder&&curl -X POST http://localhost:8083/1.0/config/n${num} --data @examples/configs/n${num}.json&&sleep 2&&curl http://localhost:8083/1.0/action/create/n${num}"  ENTER 

#examine if the creating process is done
rm -rf simple.txt
rm -rf output.txt
tmux attach
tmux capture-pane -t builder -S -
tmux save-buffer output.txt

grep '(create) started' output.txt
grep '(create) started' output.txt >>simple.txt
while(!(grep '(create) done' output.txt))
do
	tmux capture-pane -t builder -S -
	tmux save-buffer output.txt
done
grep '(create) done' output.txt >> simple.txt
echo "window inputer create done"

sleep 1
# do the starting process

tmux send -t inputer "curl http://localhost:8083/1.0/action/start/n${num}" ENTER
echo "waiting for the starting process"
tmux attach
tmux capture-pane -t builder -S -
tmux save-buffer output.txt

grep '(start) started' output.txt 
grep '(start) started' output.txt >> simple.txt

while(!(grep '(start) done' output.txt ))
do
	        tmux capture-pane -t builder -S -
		        tmux save-buffer output.txt
done    
grep '(start) done' output.txt >> simple.txt

echo "window inputer start done"

#

sleep 1


#change window to tmux to view results
#stopping process the same way to code
tmux send -t inputer "curl http://localhost:8083/1.0/action/stop/n${num}" ENTER
echo "waiting for the stopping process"
tmux attach
tmux capture-pane -t builder -S -
tmux save-buffer output.txt

grep '(stop) started' output.txt 
grep '(stop) started' output.txt >> simple.txt

while(!(grep '(stop) done' output.txt))
do
	    tmux capture-pane -t builder -S -
            tmux save-buffer output.txt
done
grep '(stop) done' output.txt >> simple.txt

      echo "window inputer stop done"

sleep 1
#the destroy process

tmux send -t inputer "curl http://localhost:8083/1.0/action/destroy/n${num}" ENTER
echo "waiting for the destroying process"
tmux attach
tmux capture-pane -t builder -S -
tmux save-buffer output.txt

grep '(delete) started' output.txt
grep '(delete) started' output.txt >> simple.txt

while(!(grep '(delete) done' output.txt ))
do
	     tmux capture-pane -t builder -S -
	     tmux save-buffer output.txt
done
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
tmux send -t 0 "exit" ENTER
tmux send -t builder "exit" ENTER




