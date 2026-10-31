#!/usr/bin/env bash
set -euo pipefail

tag=${1:?release tag required}
expected=${2:?expected commit required}
response=$(mktemp)
trap 'rm -f "$response" "$response.err"' EXIT

# The commits endpoint returns 422 for an unknown tag. The refs endpoint
# distinguishes a missing tag with 404; resolve its commit only if it exists.
if gh api "repos/$GITHUB_REPOSITORY/git/ref/tags/$tag" --silent > "$response" 2> "$response.err"; then
  actual=$(gh api "repos/$GITHUB_REPOSITORY/commits/$tag" --jq .sha)
  if [ "$actual" != "$expected" ]; then
    echo "::error::$tag points to $actual, expected $expected" >&2
    exit 1
  fi
elif ! grep -Fq '(HTTP 404)' "$response.err"; then
  cat "$response.err" >&2
  exit 1
fi
