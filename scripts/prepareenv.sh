#!/bin/bash

mbta_gtfs_url="http://www.mbta.com/uploadedfiles/MBTA_GTFS.zip"
scripts=$(cd -P -- "$(dirname -- "$0")" && printf "%s\n" "$(pwd -P)")
mkdir -p "$scripts/../instance"
instance=$(cd $scripts/../instance; pwd)

mkdir -p "$instance/feeds/mbta"
curl "$mbta_gtfs_url" -o "$instance/feeds/mbta/mbta_gtfs.zip" &&
    unzip "$instance/feeds/mbta/mbta_gtfs.zip" -d "$instance/feeds/mbta"

exit 0
