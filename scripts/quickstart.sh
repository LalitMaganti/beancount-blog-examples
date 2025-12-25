#!/bin/bash
# Quickstart script for beancount-blog-examples
# Usage: ./quickstart.sh [chapter-directory] [variant]
# Example: ./quickstart.sh demo
#          ./quickstart.sh chapter-2
#          ./quickstart.sh chapter-5          # defaults to net view
#          ./quickstart.sh chapter-5 gross    # gross view
#          ./quickstart.sh chapter-6          # defaults to total view
#          ./quickstart.sh chapter-6 lalit    # lalit's individual view
#          ./quickstart.sh chapter-6 wife     # wife's individual view

set -e

CHAPTER="${1:-chapter-2}"
VARIANT="${2:-}"
REPO_URL="https://github.com/LalitMaganti/beancount-blog-examples"

# Function to setup python environment
# Usage: setup_env <pip-install-arguments>
setup_env() {
    local install_args="$@"

    # Check if we need to setup the environment (missing fava binary)
    if [ ! -f ".venv/bin/fava" ]; then
        echo "==> Setting up Python environment..."
        if command -v uv &> /dev/null; then
            echo "    Using uv for optimization"
            uv venv .venv --allow-existing
            # shellcheck disable=SC2086
            uv pip install --python .venv $install_args
        else
            echo "    Using standard pip"
            python3 -m venv .venv
            # shellcheck disable=SC2086
            .venv/bin/pip install $install_args
        fi
    fi
}

# --- Mode 1: Running inside the cloned repository ---
if [ -f "pyproject.toml" ] && [ -d "scripts" ]; then
    echo "==> Detected repository root. Running in local mode."

    if ! [ -d "$CHAPTER" ]; then
        echo "Error: Directory '$CHAPTER' not found."
        echo "Available chapters:"
        ls -d chapter* demo
        exit 1
    fi

    # Install the current project in editable mode
    setup_env -e .

    # Path to the journal file relative to the project root
    # Handle chapters with multiple journal files
    if [ -f "$CHAPTER/journal.beancount" ]; then
        JOURNAL_PATH="$CHAPTER/journal.beancount"
    elif [ -f "$CHAPTER/journal-net.beancount" ]; then
        # Chapter 5: net (default) or gross view
        if [ "$VARIANT" = "gross" ]; then
            JOURNAL_PATH="$CHAPTER/journal-gross.beancount"
        else
            JOURNAL_PATH="$CHAPTER/journal-net.beancount"
        fi
    elif [ -f "$CHAPTER/total/journal-net.beancount" ]; then
        # Chapter 6: total (default), lalit, or wife view
        if [ -n "$VARIANT" ]; then
            JOURNAL_PATH="$CHAPTER/$VARIANT/journal-net.beancount"
        else
            JOURNAL_PATH="$CHAPTER/total/journal-net.beancount"
        fi
    else
        echo "Error: No journal file found in '$CHAPTER'."
        exit 1
    fi

# --- Mode 2: Standalone download (curl | bash) ---
else
    echo "==> Running in standalone mode."

    # Create a temporary directory and ensure it's cleaned up?
    # For now, let's keep it so they can see logs, but use /tmp.
    WORK_DIR=$(mktemp -d 2>/dev/null || mktemp -d -t 'beancount-quickstart')
    echo "==> Working in temporary directory: $WORK_DIR"

    echo "==> Downloading $CHAPTER from $REPO_URL..."
    # Download specific folder and strip components so contents are in WORK_DIR
    curl -sL "$REPO_URL/archive/refs/heads/main.tar.gz" | tar xz -C "$WORK_DIR" "beancount-blog-examples-main/$CHAPTER" --strip-components=2

    cd "$WORK_DIR"

    # Install specific dependencies for standalone usage
    setup_env beancount fava

    # Path to the journal file is now in the root of WORK_DIR
    # Handle chapters with multiple journal files
    if [ -f "journal.beancount" ]; then
        JOURNAL_PATH="journal.beancount"
    elif [ -f "journal-net.beancount" ]; then
        # Chapter 5: net (default) or gross view
        if [ "$VARIANT" = "gross" ]; then
            JOURNAL_PATH="journal-gross.beancount"
        else
            JOURNAL_PATH="journal-net.beancount"
        fi
    elif [ -f "total/journal-net.beancount" ]; then
        # Chapter 6: total (default), lalit, or wife view
        if [ -n "$VARIANT" ]; then
            JOURNAL_PATH="$VARIANT/journal-net.beancount"
        else
            JOURNAL_PATH="total/journal-net.beancount"
        fi
    else
        echo "Error: No journal file found."
        exit 1
    fi
fi

# Chapter 3 uses beancount-import instead of Fava
if [ "$CHAPTER" = "chapter-3" ]; then
    echo "==> Starting beancount-import for $CHAPTER..."
    echo "    Web UI will open at http://localhost:8101"
    echo "    Press Ctrl+C to stop"
    echo ""
    .venv/bin/python "$CHAPTER/beancount_import_config.py"
else
    echo "==> Starting Fava for $CHAPTER..."
    echo "    Press Ctrl+C to stop"
    echo ""
    .venv/bin/fava "$JOURNAL_PATH"
fi
