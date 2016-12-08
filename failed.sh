#!/usr/bin/env bash
if [ $# -ne 1 ]; then
	echo "Usage: failed <filename>"
	exit 1
fi

cat $1 | awk -F  ";" '/FAIL/ {print $1}' | sort


