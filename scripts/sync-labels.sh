#!/bin/bash

# Script to sync GitHub labels from .github/labels.yml
# Usage: bash scripts/sync-labels.sh

set -e

LABELS_FILE=".github/labels.yml"

if [ ! -f "$LABELS_FILE" ]; then
  echo "Error: $LABELS_FILE not found"
  exit 1
fi

echo "Syncing labels from $LABELS_FILE..."

# Parse YAML and create/update labels
# This uses yq if available, or falls back to a simple grep-based parser

if command -v yq &> /dev/null; then
  echo "Using yq to parse YAML..."

  # Count labels
  LABEL_COUNT=$(yq eval '. | length' "$LABELS_FILE")
  echo "Found $LABEL_COUNT labels to sync"

  for i in $(seq 0 $((LABEL_COUNT - 1))); do
    NAME=$(yq eval ".[$i].name" "$LABELS_FILE")
    COLOR=$(yq eval ".[$i].color" "$LABELS_FILE")
    DESCRIPTION=$(yq eval ".[$i].description" "$LABELS_FILE")

    # Remove quotes if present
    NAME=$(echo "$NAME" | tr -d '"')
    COLOR=$(echo "$COLOR" | tr -d '"')
    DESCRIPTION=$(echo "$DESCRIPTION" | tr -d '"')

    echo "Processing: $NAME"

    # Check if label exists
    if gh label list --json name --jq '.[].name' | grep -q "^${NAME}$"; then
      echo "  Updating existing label: $NAME"
      gh label edit "$NAME" --color "$COLOR" --description "$DESCRIPTION" || echo "  Warning: Failed to update $NAME"
    else
      echo "  Creating new label: $NAME"
      gh label create "$NAME" --color "$COLOR" --description "$DESCRIPTION" || echo "  Warning: Failed to create $NAME"
    fi
  done
else
  echo "yq not found, using grep-based parser..."
  echo "Note: Install yq for better parsing: brew install yq"
  echo ""

  # Simple grep-based parser (works for our specific YAML format)
  while IFS= read -r line; do
    if [[ $line =~ ^-\ name:\ (.+)$ ]]; then
      NAME="${BASH_REMATCH[1]}"
      NAME=$(echo "$NAME" | tr -d '"' | xargs)
    elif [[ $line =~ ^\ \ color:\ \"(.+)\"$ ]]; then
      COLOR="${BASH_REMATCH[1]}"
    elif [[ $line =~ ^\ \ description:\ \"(.+)\"$ ]]; then
      DESCRIPTION="${BASH_REMATCH[1]}"

      # We have all three fields, create/update the label
      if [ -n "$NAME" ] && [ -n "$COLOR" ] && [ -n "$DESCRIPTION" ]; then
        echo "Processing: $NAME"

        # Check if label exists
        if gh label list --json name --jq '.[].name' | grep -q "^${NAME}$"; then
          echo "  Updating existing label: $NAME"
          gh label edit "$NAME" --color "$COLOR" --description "$DESCRIPTION" 2>/dev/null || echo "  Warning: Failed to update $NAME"
        else
          echo "  Creating new label: $NAME"
          gh label create "$NAME" --color "$COLOR" --description "$DESCRIPTION" 2>/dev/null || echo "  Warning: Failed to create $NAME"
        fi

        # Reset for next label
        NAME=""
        COLOR=""
        DESCRIPTION=""
      fi
    fi
  done < "$LABELS_FILE"
fi

echo ""
echo "✅ Label sync complete!"
echo ""
echo "Current labels:"
gh label list
