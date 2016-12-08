#!/usr/bin/env bash
if [ $# -ne 1 ]; then
	echo "Usage: summary <filename>"
	exit 1
fi

echo -n "Succeed "
./succeed.sh $1 | wc -l

echo -n "Failed "
./failed.sh $1 | wc -l


