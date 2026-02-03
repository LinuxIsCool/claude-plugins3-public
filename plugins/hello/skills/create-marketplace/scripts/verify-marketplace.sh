#!/bin/bash
# Verify marketplace structure is valid
# Usage: ./verify-marketplace.sh /path/to/marketplace

# Don't use set -e because ((var++)) returns 1 when var is 0

MARKETPLACE_PATH="${1:-.}"
ERRORS=0
WARNINGS=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "Verifying marketplace at: $MARKETPLACE_PATH"
echo "========================================"
echo ""

check_file() {
    local file="$1"
    local required="$2"

    if [[ -f "$MARKETPLACE_PATH/$file" ]]; then
        echo -e "${GREEN}OK${NC}: $file"
        return 0
    elif [[ "$required" == "required" ]]; then
        echo -e "${RED}ERROR${NC}: Missing required file: $file"
        ((ERRORS++))
        return 1
    else
        echo -e "${YELLOW}WARN${NC}: Missing optional file: $file"
        ((WARNINGS++))
        return 0
    fi
}

check_dir() {
    local dir="$1"
    local required="$2"

    if [[ -d "$MARKETPLACE_PATH/$dir" ]]; then
        echo -e "${GREEN}OK${NC}: $dir/"
        return 0
    elif [[ "$required" == "required" ]]; then
        echo -e "${RED}ERROR${NC}: Missing required directory: $dir/"
        ((ERRORS++))
        return 1
    else
        echo -e "${YELLOW}WARN${NC}: Missing optional directory: $dir/"
        ((WARNINGS++))
        return 0
    fi
}

validate_json() {
    local file="$1"
    local full_path="$MARKETPLACE_PATH/$file"

    if [[ -f "$full_path" ]]; then
        if python3 -m json.tool "$full_path" > /dev/null 2>&1; then
            echo -e "${GREEN}OK${NC}: $file is valid JSON"
            return 0
        else
            echo -e "${RED}ERROR${NC}: $file is not valid JSON"
            ((ERRORS++))
            return 1
        fi
    fi
}

echo "--- Core Structure ---"
check_file ".claude-plugin/marketplace.json" "required"
check_file "CLAUDE.md" "required"
check_file "README.md" "optional"
check_dir "plugins" "required"

echo ""
echo "--- JSON Validation ---"
validate_json ".claude-plugin/marketplace.json"

echo ""
echo "--- Plugin Discovery ---"

# Find and check all plugins
if [[ -d "$MARKETPLACE_PATH/plugins" ]]; then
    for plugin_dir in "$MARKETPLACE_PATH/plugins"/*; do
        if [[ -d "$plugin_dir" ]]; then
            plugin_name=$(basename "$plugin_dir")
            echo ""
            echo "Plugin: $plugin_name"

            # Check plugin.json
            if [[ -f "$plugin_dir/.claude-plugin/plugin.json" ]]; then
                echo -e "  ${GREEN}OK${NC}: .claude-plugin/plugin.json"

                # Validate plugin.json
                if python3 -m json.tool "$plugin_dir/.claude-plugin/plugin.json" > /dev/null 2>&1; then
                    echo -e "  ${GREEN}OK${NC}: plugin.json is valid JSON"
                else
                    echo -e "  ${RED}ERROR${NC}: plugin.json is not valid JSON"
                    ((ERRORS++))
                fi
            else
                echo -e "  ${RED}ERROR${NC}: Missing .claude-plugin/plugin.json"
                ((ERRORS++))
            fi

            # Check for skills directory
            if [[ -d "$plugin_dir/skills" ]]; then
                skill_count=$(find "$plugin_dir/skills" -name "SKILL.md" | wc -l)
                echo -e "  ${GREEN}OK${NC}: skills/ (${skill_count} skills found)"
            else
                echo -e "  ${YELLOW}WARN${NC}: No skills/ directory"
                ((WARNINGS++))
            fi

            # Check for commands directory
            if [[ -d "$plugin_dir/commands" ]]; then
                cmd_count=$(find "$plugin_dir/commands" -name "*.md" | wc -l)
                echo -e "  ${GREEN}OK${NC}: commands/ (${cmd_count} commands found)"
            else
                echo -e "  ${YELLOW}WARN${NC}: No commands/ directory"
                ((WARNINGS++))
            fi
        fi
    done
fi

echo ""
echo "========================================"
if [[ $ERRORS -eq 0 ]]; then
    if [[ $WARNINGS -eq 0 ]]; then
        echo -e "${GREEN}PASSED${NC}: Marketplace verification successful"
    else
        echo -e "${GREEN}PASSED${NC} with ${YELLOW}$WARNINGS warning(s)${NC}"
    fi
    exit 0
else
    echo -e "${RED}FAILED${NC}: $ERRORS error(s), $WARNINGS warning(s)"
    exit 1
fi
