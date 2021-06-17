#!/usr/bin/env bash

set -eu

components=$(find /sys/devices/virtual/powercap/intel-rapl -name "energy_uj")

OUTPUT_DIR="$HOME/power-monitoring-db"

read_energy() {
    local data=""
    for component in ${components[@]}; do
        name=$(cat ${component%energy_uj}/name)
        energy=$(cat "$component")
        data=$data$component,$name,$energy\;
        echo "name: $name"
    done
    data="${data%;}"
    echo "$data"
}

read_maxenergy() {
    local data=""
    for component in ${components[@]}; do
        name=$(cat ${component%energy_uj}/name)
        energy=$(cat ${component%energy_uj}/max_energy_range_uj)
        data=$data$component,$name,$energy\;
    done
    data="${data%;}"
    echo "$data"
}

# Calculate the energy values for each component
calculate_energy() {
    begins=$1
    ends=$2
    maxenergies=$3
    echo | awk -v begins="$begins" -v ends="$ends" -v maxenergies="$maxenergies" 'BEGIN \
    {
    split(ends,ends1,";");
    split(begins,begins1,";");
    split(maxenergies,maxenergies1,";");


    for (i in ends1 ){
        split(ends1[i],dataends,",")
        names[dataends[1]]  = dataends[2]
        energiesends[dataends[1]] =dataends[3]
    }

     for (i in begins1 ){
        split(begins1[i],databegins,",")
        energiesbegins[databegins[1]]=databegins[3]
    }

    for (i in maxenergies1 ){
        split(maxenergies1[i],datamax,",")
        energiesmax[datamax[1]]=datamax[3]
    }


    for (i in names ){
        x = energiesends[i] - energiesbegins[i]
        if (x < 0) {
            x=x+energiesmax[i]
        }
        printf i","names[i]","x";"
    }

    }'

}

# Printing functions

print_append_csv() {
    echo | awk -v data="$1" 'BEGIN \
    {
        split(data,data1,";");
        asort(data1)
        for (line in data1)  {
            split(data1[line],line1,",");
            path=line1[1];
            name=line1[2];
            value=line1[3];
            split(path,path1,":")
            cpu=path1[2]
            split(cpu,cpu1,"/")
            cpu=cpu1[1]
            energies[name,cpu]=value
        }
        asorti(energies,indices )
         for (i in indices ) {
           printf ";"energies[indices[i]]
        }

    }'
}

list_domains() {
    echo -n duration
    echo | awk -v data=$1 'BEGIN \
    {
        split(data,data1,";");
        asort(data1)
        for (line in data1) {
            split(data1[line],line1,",");
            path=line1[1];
            name=line1[2];
            value=line1[3];
            split(path,path1,":")
            cpu=path1[2]
            split(cpu,cpu1,"/")
            cpu=cpu1[1]
            energies[name,cpu]=value

        }
        asorti(energies,indices)
        for (i in indices) {
           printf ";"toupper(indices[i])
        }
    }'
}

get_raw_energy() {
    begin_energy=$(read_energy)
    beginT=$(date +"%s%N")

    ###############################################
    sleep 1
    ###############################################

    endT=$(date +"%s%N")
    end_energy=$(read_energy)

    ### Calculate the energies

    energies=$(calculate_energy "$begin_energy" "$end_energy" "$maxenergies")
    duration=$(((endT - beginT) / 1000))
    # Remove the last ;
    energies="${energies%;}"
    # Rename 'package-0' with CPU
    energies=$(echo "$energies" | sed -r 's/package-([0-9]+)/cpu/g')

    results=$energies

    results=$results";global:/,exit_code,0"

    echo -n $duration
    print_append_csv "$results"
    echo ""
}


###############################

csv_header() {
    maxenergies=$(read_maxenergy)

    echo -n "timestamp;"
    maxenergies=$(echo "$maxenergies" | sed -r 's/package-([0-9]+)/cpu/g')
    list_domains "$maxenergies"
    echo ";EXIT_CODE"
}

print_energy() {
    maxenergies=$(read_maxenergy)
    get_raw_energy
}


generate_fname() {
    local datestring;
    datestring=$(date +%Y-%m-%d)
    echo "$datestring.csv"
}

timestamp() {
    date --iso-8601=seconds
}

rand_delay() {
    local total_ms=$(( RANDOM % 5000 + 1 ))
    local seconds=$((total_ms / 1000))
    local remaining_ms;
    remaining_ms=$((total_ms % 1000))
    echo "$seconds.$remaining_ms"
}

write_entry() {
    local outfile;
    outfile="$OUTPUT_DIR/$(generate_fname)"

    # If it's the first time we write to the file, add a header,
    # and in the same step create the file.
    if [[ ! -f "$outfile" ]]; then
        csv_header > "$outfile"
    fi

    entry="$(timestamp);$(print_energy)"
    echo "$entry" >> "$outfile"
}

main() {
    if [[ ! -d "$OUTPUT_DIR" ]]; then
        mkdir -p "$OUTPUT_DIR"
    fi

    while true
    do
        write_entry
        sleep "$(rand_delay)"
    done
}

main
