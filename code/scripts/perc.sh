#!/bin/bash

g++ -o2 -std=c++11 ../source/perc_v2.cpp -o ../perc_v2

BASE_DIR="../../networks/ER"

BASE_NET=$1
BASE_NET_DIR="${BASE_DIR}/${BASE_NET}"

#for SEED in {00000..4999}; do
for SEED in {10000..19999}; do

    NET_NAME="${BASE_NET}_${SEED}"
    NET_DIR="${BASE_NET_DIR}/${NET_NAME}"
    NETWORK="${NET_DIR}/${NET_NAME}_gcc.txt"

    #for ATTACK in "Ran" "Deg" "Btw" "DegU" "BtwU"; do
    for ATTACK in "Ran"; do
        ORDER="${NET_DIR}/${ATTACK}/oi_list_${NET_NAME}.txt"
        echo ${ORDER}
        if [ ! -f "${ORDER}" ]; then 
            echo "File ${ORDER} does not exist"
            continue
        fi
        OUTPUT="${NET_DIR}/${ATTACK}/comp_data.txt"
        if [ -f "${OUTPUT}" ]; then 
            echo "File ${OUTPUT} already exist"
            continue
        fi
        #echo $NETWORK
        #echo $ORDER
        #echo $OUTPUT
        #if [[ -f "${ORDER}" && -f "${NETWORK}" && -f "${OUTPUT}" ]]; then 
        #    echo "Check"
        #fi
        ../perc_v2 $NETWORK $ORDER $OUTPUT 
    done
done
