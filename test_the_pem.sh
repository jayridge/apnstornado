#!/bin/bash

if [ $# -ne 2 -a $# -ne 3 ]; then
    echo "wrong num arg: should be \"$0 [sandbox] apple.pem entrust.pem\""
    exit 1
fi

HOST='gateway.push.apple.com'
CERT=$1
CAFILE=$2
if [ $# -eq 3 ]; then
    HOST='gateway.sandbox.push.apple.com'
    CERT=$2
    CAFILE=$3
fi

openssl s_client -connect $HOST:2195 -cert $CERT -debug -showcerts -CAfile $CAFILE 

