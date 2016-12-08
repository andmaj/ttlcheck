#!/usr/bin/env bash
if [ $# -ne 1 ]; then
	echo "Usage: succeed <filename>"
	exit 1
fi

cat $1 | awk -F  ";" '/OK/ {print $1}' | sort


