#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ "$PWD" != "$PROJECT_ROOT" ]]; then
    echo "Warning: run this script from the project root ($PROJECT_ROOT). Current directory: $PWD" >&2
    exit 1
fi

mkdir -p uml

# Package overview
pyreverse -k -o svg -p Project .
mv packages_Project.svg uml/package_overview.svg

# Class diagrams
for pkg in llm refactoring tree_of_thoughts utility; do
    pyreverse -o svg -p $pkg $pkg
    mv classes_$pkg.svg uml/${pkg}_classes.svg
    rm packages_$pkg.svg
done

echo "UML diagrams generated in uml/"