#!/usr/bin/env bash
if [ $# -ne 3 ]; then
        echo "Usage: filter <ttlcheck_filename> <scan_filename> <result_filename>"
        exit 1
fi

containsElement () {
	local e
	for e in "${@:2}"; do [[ "$e" == "$1" ]] && return 0; done
	return 1
}

differ=$(comm -13 <(sort <(cat $2 | awk '{print $2}')) <(sort <(cat $1 | awk -F ";" '{print $1}')))

>$3

while IFS='' read -r line || [[ -n "$line" ]]; do
	IFS=';' read -r -a ttliparr <<< "$line"
	if ! containsElement "${ttliparr[0]}" "${differ[@]}"
	then
		echo $line >> $3
	fi;
done < "$1"

