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
