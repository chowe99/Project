#!/bin/bash

# Start the bot server in the background
python3 bot.py &

# Initialize the SQLite database if it doesn't exist
if [ ! -f "/tmp/database.db" ]; then
    sqlite3 /tmp/database.db < database.sql
    echo "Database initialized."
else
    echo "Database already exists."
fi

# Start the Flask application
flask run --host=0.0.0.0

