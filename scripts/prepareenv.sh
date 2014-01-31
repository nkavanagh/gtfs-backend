#!/bin/bash

mbta_gtfs_url="http://www.mbta.com/uploadedfiles/MBTA_GTFS.zip"
root=$(cd -P -- "$(dirname -- "$0")" && printf "%s\n" "$(pwd -P)")
instance=$(cd $root/../instance; pwd)

echo $instance

mkdir -p "$instance/feeds/mbta"
curl "$mbta_gtfs_url" -o "$instance/feeds/mbta/mbta_gtfs.zip" &&
    unzip "$instance/feeds/mbta/mbta_gtfs.zip" -d "$instance/feeds/mbta"

exit 0
