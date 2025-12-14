#!/bin/bash
pkill -f "Google Chrome" 2>/dev/null
sleep 2

/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
    --user-data-dir="$HOME/chrome-test-profile" \
    --remote-debugging-port=9222 \
    &

echo "Chrome launched. Open YouTube and chrome://media-internals"
