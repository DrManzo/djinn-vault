#!/bin/bash
# Run package tests across all supported distributions
#
# Usage:
#   ./run-tests.sh              # Test all distros
#   ./run-tests.sh debian       # Test specific distro
#   ./run-tests.sh --build      # Rebuild images first
#
# Prerequisites:
#   - Docker and Docker Compose installed
#   - Packages built in ../releases/

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# All available distros
ALL_DISTROS="debian debian-sid ubuntu fedora arch"

# Parse arguments
BUILD_FIRST=false
DISTROS=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --build|-b)
            BUILD_FIRST=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [options] [distro...]"
            echo ""
            echo "Options:"
            echo "  --build, -b    Rebuild Docker images before testing"
            echo "  --help, -h     Show this help"
            echo ""
            echo "Available distros: $ALL_DISTROS"
            echo ""
            echo "Examples:"
            echo "  $0                    # Test all distros"
            echo "  $0 debian fedora      # Test specific distros"
            echo "  $0 --build debian     # Rebuild and test Debian"
            exit 0
            ;;
        *)
            DISTROS="$DISTROS $1"
            shift
            ;;
    esac
done

# Default to all distros if none specified
if [[ -z "$DISTROS" ]]; then
    DISTROS="$ALL_DISTROS"
fi

# Check for packages
if ! ls ../releases/*/*.deb ../releases/*/*.rpm 2>/dev/null | head -1 > /dev/null; then
    echo -e "${RED}Error: No packages found in ../releases/${NC}"
    echo ""
    echo "Build packages first with:"
    echo "  ./scripts/package.sh"
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Voxtype Package Test Runner${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Show what we're testing
echo -e "${YELLOW}Packages found:${NC}"
ls -1 ../releases/*/*.deb ../releases/*/*.rpm 2>/dev/null | sed 's/^/  /'
echo ""

echo -e "${YELLOW}Distros to test:${NC} $DISTROS"
echo ""

# Build images if requested
if [[ "$BUILD_FIRST" == "true" ]]; then
    echo -e "${YELLOW}Building Docker images...${NC}"
    docker compose build $DISTROS
    echo ""
fi

# Track results
declare -A RESULTS
TOTAL_PASS=0
TOTAL_FAIL=0

# Run tests for each distro
for distro in $DISTROS; do
    echo -e "${BLUE}----------------------------------------${NC}"
    echo -e "${BLUE}Testing: $distro${NC}"
    echo -e "${BLUE}----------------------------------------${NC}"
    echo ""

    # Build image if it doesn't exist
    if ! docker image inspect "voxtype-test-$distro" > /dev/null 2>&1; then
        echo -e "${YELLOW}Building image for $distro...${NC}"
        docker compose build "$distro"
    fi

    # Run test
    set +e
    docker compose run --rm "$distro"
    exit_code=$?
    set -e

    if [[ $exit_code -eq 0 ]]; then
        RESULTS[$distro]="PASS"
        ((TOTAL_PASS++)) || true
    else
        RESULTS[$distro]="FAIL"
        ((TOTAL_FAIL++)) || true
    fi

    echo ""
done

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

for distro in $DISTROS; do
    if [[ "${RESULTS[$distro]}" == "PASS" ]]; then
        echo -e "  $distro: ${GREEN}PASS${NC}"
    else
        echo -e "  $distro: ${RED}FAIL${NC}"
    fi
done

echo ""
echo -e "Total: ${GREEN}$TOTAL_PASS passed${NC}, ${RED}$TOTAL_FAIL failed${NC}"
echo ""

if [[ $TOTAL_FAIL -gt 0 ]]; then
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
else
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
fi
