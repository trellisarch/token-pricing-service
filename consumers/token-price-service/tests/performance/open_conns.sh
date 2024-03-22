#!/bin/bash

# Function to execute SQL query and print result
export PGPASSWORD=postgres
get_open_connections() {
    psql -h localhost -U postgres -d postgres -t -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"
}

# Loop with a 2-second sleep interval
while true; do
    echo -n "Open connections: "; get_open_connections
    sleep 2
done
