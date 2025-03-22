#!/bin/bash
# Demo script to apply patches

# Display colorful output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}===== Patch Demo =====\n${NC}"

# Function to show file contents
show_file() {
    echo -e "${YELLOW}Contents of $1:${NC}"
    cat "$1"
    echo -e "\n"
}

# Function to show patch
show_patch() {
    echo -e "${YELLOW}Contents of $1:${NC}"
    cat "$1"
    echo -e "\n"
}

# Function to apply a patch
apply_patch() {
    echo -e "${GREEN}Applying patch $2 to $1...${NC}"
    patch "$1" -i "$2" -o "$3"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Patch applied successfully!${NC}"
    else
        echo -e "${RED}Patch application failed.${NC}"
    fi
    echo -e "\n"
}

# Calculator example
echo -e "${BLUE}Calculator Patch Example${NC}"
echo -e "${YELLOW}This example shows adding new features to a calculator program${NC}\n"

# Show original file
show_file "calculator_v1.py"

# Show patch
show_patch "calculator.patch"

# Apply patch
apply_patch "calculator_v1.py" "calculator.patch" "calculator_patched.py"

# Show result
echo -e "${GREEN}Result after applying the patch:${NC}"
show_file "calculator_patched.py"

# Greeting example
echo -e "${BLUE}Greeting Bugfix Example${NC}"
echo -e "${YELLOW}This example shows fixing a bug in a greeting program${NC}\n"

# Show original file with bug
show_file "greeting_v1.py"

# Show patch
show_patch "greeting_bugfix.patch"

# Apply patch
apply_patch "greeting_v1.py" "greeting_bugfix.patch" "greeting_patched.py"

# Show result
echo -e "${GREEN}Result after applying the patch:${NC}"
show_file "greeting_patched.py"

echo -e "${BLUE}===== Demo Complete =====\n${NC}"
echo -e "You can also verify that the patched files are identical to the v2 versions:"
echo -e "diff calculator_patched.py calculator_v2.py"
echo -e "diff greeting_patched.py greeting_v2.py" 