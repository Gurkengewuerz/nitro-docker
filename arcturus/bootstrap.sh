#!/bin/sh

FILE="/bootstrapped"

if test -f "$FILE"; then
    echo "Skipping bootstrapping"
else
    echo "Bootstrapping for first time"
    wget https://github.com/billsonnn/nitro-react/files/10334858/room.nitro.zip
    unzip -o room.nitro.zip -d /app/assets/assets/bundled/generic
    rm /app/room.nitro.zip
    rm /app/assets/assets/bundled/generic/__MACOSX -R
    touch "$FILE"
fi

/usr/bin/java -jar /app/emulator.jar