#!/bin/bash

# Check if BOT_TOKEN is set
if [ -z "$BOT_TOKEN" ] || [ "$BOT_TOKEN" = "demo_mode" ]; then
    echo "❌ BOT_TOKEN not set!"
    echo "Please set BOT_TOKEN environment variable with your bot token from @BotFather"
    echo "Example: BOT_TOKEN=123456789:ABCDEF..."
    exit 1
fi

echo "🤖 Starting Spotify Bot..."
echo "✅ BOT_TOKEN found"

# Run the bot
python3 start_bot.py