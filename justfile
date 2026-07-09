# List all available commands (default)
default:
    @just --list

# Verify environment tools (Node, Python, Git) are installed
doctor:
    @echo "Checking system prerequisites..."
    @which node || echo "Node.js not found"
    @which python || which python3 || echo "Python not found"
    @which git || echo "Git not found"
    @which just || echo "just not found"
    @echo "Environment check complete."

# Clean up temporary files, cache, and logs
clean:
    @echo "Cleaning up temp files and caches..."
    rm -rf tmp/ temp/ logs/
    @echo "Cleanup complete."

# Install repository-wide git pre-commit hooks
install-hooks:
    @echo "Installing pre-commit hooks..."
    @HOOKS_DIR=$(git rev-parse --git-path hooks); \
    mkdir -p "$HOOKS_DIR"; \
    echo '#!/bin/sh' > "$HOOKS_DIR/pre-commit"; \
    echo 'set -e' >> "$HOOKS_DIR/pre-commit"; \
    echo 'exec just pre-commit' >> "$HOOKS_DIR/pre-commit"; \
    chmod +x "$HOOKS_DIR/pre-commit"; \
    echo "Pre-commit hooks installed successfully at $HOOKS_DIR/pre-commit"

# Run pre-commit hooks for all projects containing staged changes
pre-commit:
    @echo "Checking staged files for pre-commit hooks..."
    @STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM); \
    if [ -z "$STAGED_FILES" ]; then \
        echo "No staged files found. Skipping pre-commit checks."; \
        exit 0; \
    fi; \
    DIRS_TO_RUN=""; \
    for file in $STAGED_FILES; do \
        dir=$(echo "$file" | cut -d'/' -f1-2); \
        if [ -d "$dir" ] && [ -f "$dir/justfile" ] && grep -q "^pre-commit:" "$dir/justfile"; then \
            if ! echo "$DIRS_TO_RUN" | grep -q "\<$dir\>"; then \
                DIRS_TO_RUN="$DIRS_TO_RUN $dir"; \
            fi; \
        fi; \
    done; \
    if [ -z "$DIRS_TO_RUN" ]; then \
        echo "No subprojects with staged files require pre-commit checks."; \
        exit 0; \
    fi; \
    echo "Running pre-commit hooks for:$DIRS_TO_RUN"; \
    pids=""; \
    for dir in $DIRS_TO_RUN; do \
        (cd "$dir" && just pre-commit) & \
        pids="$pids $!"; \
    done; \
    for pid in $pids; do \
        wait $pid || exit 1; \
    done; \
    for file in $STAGED_FILES; do \
        if git diff --name-only | grep -q "^$file$"; then \
            echo "Re-staging auto-formatted/fixed file: $file"; \
            git add "$file"; \
        fi; \
    done; \
    echo "All pre-commit hooks completed successfully."

# Ensure all .sh files are executable and print a change summary
script-permissions:
    #!/usr/bin/env sh
    set -eu
    echo "[script_permissions] Scanning for .sh files under $(pwd)..."
    tmp_list="$(mktemp)"
    find . \
        \( -type d \( -name "node_modules" -o -name "vendor" \) -prune \) -o \
        \( -type f -name "*.sh" -print \) | sort > "$tmp_list"
    total="$(wc -l < "$tmp_list" | tr -d ' ')"
    changed=0
    tmp_changed="$(mktemp)"
    trap 'rm -f "$tmp_list" "$tmp_changed"' EXIT

    while IFS= read -r file; do
        if [ -x "$file" ]; then
            echo "[skip]    already executable: $file"
        else
            chmod +x "$file"
            changed=$((changed + 1))
            printf '%s\n' "$file" >> "$tmp_changed"
            echo "[update]  added +x: $file"
        fi
    done < "$tmp_list"

    already_executable=$((total - changed))
    printf '\n[script_permissions] Summary\n  total .sh files found: %s\n  already executable:    %s\n  newly updated (+x):    %s\n' "$total" "$already_executable" "$changed"

    if [ "$changed" -eq 0 ]; then
        echo "  no permission changes were needed"
    else
        echo "  files updated:"
        sed 's/^/    - /' "$tmp_changed"
    fi



