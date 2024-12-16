# Use the official MySQL image
FROM mysql:5.7

# Copy the initialization SQL script into the container
COPY init.sql /docker-entrypoint-initdb.d/

# The MySQL entrypoint script automatically executes the scripts in /docker-entrypoint-initdb.d/ 
