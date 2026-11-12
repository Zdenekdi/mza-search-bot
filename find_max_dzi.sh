#!/bin/bash
base_url="https://www.mza.cz/iipsrv/iipsrv.fcgi?Deepzoom=/srv/LUN113/LUN113/216000010/216000010-00165-00000000000-000-000000000-000000107/216000010-00165-00000000000-000-000000000-000000107-"
low=1
high=300
max_found=0

check_exists() {
    num=$1
    val=$((num * 10))
    formatted=$(printf "%05d" $val)
    url="${base_url}${formatted}.jp2.dzi"
    content=$(curl -s -A "Mozilla/5.0" "$url" | head -c 100)
    if [[ "$content" == *xmlns* ]]; then
        return 0
    else
        return 1
    fi
}

while [ $low -le $high ]; do
    mid=$(((low + high) / 2))
    if check_exists $mid; then
        max_found=$mid
        low=$((mid + 1))
    else
        high=$((mid - 1))
    fi
done

echo "Max image is: $((max_found * 10))"

rm -f lanove_dzi_links.txt
for i in $(seq 1 $max_found); do
    val=$((i * 10))
    formatted=$(printf "%05d" $val)
    echo "${base_url}${formatted}.jp2.dzi" >> lanove_dzi_links.txt
done
echo "Saved $max_found links to lanove_dzi_links.txt"
