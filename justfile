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
    cp tools/git-hooks/pre-commit "$HOOKS_DIR/pre-commit"; \
    chmod +x "$HOOKS_DIR/pre-commit"; \
    echo "Pre-commit hooks installed successfully at $HOOKS_DIR/pre-commit"

