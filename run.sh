#!/bin/bash

# Container names
POLISH_CONTAINER="linguist-cards-polish"
ENGLISH_CONTAINER="linguist-cards-english"

# Function to start containers
start_containers() {
    echo "Starting Docker containers..."

    # Start Polish container
    sudo docker run -d --rm --name "$POLISH_CONTAINER" --env-file .env linguist-cards polish
    if [ $? -eq 0 ]; then
        echo "✓ Started $POLISH_CONTAINER"
    else
        echo "✗ Failed to start $POLISH_CONTAINER"
    fi

    # Start English container
    sudo docker run -d --rm --name "$ENGLISH_CONTAINER" --env-file .env linguist-cards english
    if [ $? -eq 0 ]; then
        echo "✓ Started $ENGLISH_CONTAINER"
    else
        echo "✗ Failed to start $ENGLISH_CONTAINER"
    fi

    echo "Done!"
}

# Function to stop containers
stop_containers() {
    echo "Stopping Docker containers..."

    # Stop Polish container
    sudo docker stop "$POLISH_CONTAINER" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✓ Stopped $POLISH_CONTAINER"
        sudo docker rm "$POLISH_CONTAINER" 2>/dev/null
        echo "✓ Removed $POLISH_CONTAINER"
    else
        echo "✗ Container $POLISH_CONTAINER not running or not found"
    fi

    # Stop English container
    sudo docker stop "$ENGLISH_CONTAINER" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✓ Stopped $ENGLISH_CONTAINER"
        sudo docker rm "$ENGLISH_CONTAINER" 2>/dev/null
        echo "✓ Removed $ENGLISH_CONTAINER"
    else
        echo "✗ Container $ENGLISH_CONTAINER not running or not found"
    fi

    echo "Done!"
}

# Main script logic
case "$1" in
    run)
        start_containers
        ;;
    stop)
        stop_containers
        ;;
    *)
        echo "Usage: $0 {run|stop}"
        echo "  run  - Start both linguist-cards containers (polish and english)"
        echo "  stop - Stop and remove both containers"
        exit 1
        ;;
esac

exit 0
