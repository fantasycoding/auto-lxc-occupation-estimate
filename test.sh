#!/bin/bash
curl -X POST http://localhost:8083/1.0/config/n50 --data @examples/configs/n50.json
command
curl http://localhost:8083/1.0/action/create/n50>file.txt
curl http://localhost:8083/1.0/action/start/n50>file.txt

 ../reset_all.sh
