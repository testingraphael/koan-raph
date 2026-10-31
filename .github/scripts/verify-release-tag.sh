#!/usr/bin/env bash
set -euo pipefail

tag=${1:?release tag required}
expected=${2:?expected commit required}
response=$(mktemp)
trap 'rm -f "$response" "$response.err"' EXIT

if gh api "repos/$GITHUB_REPOSITORY/commits/$tag" --jq .sha > "$response" 2> "$response.err"; then
  actual=$(cat "$response")
  if [ "$actual" != "$expected" ]; then
    echo "::error::$tag points to $actual, expected $expected" >&2
    exit 1
  fi
elif ! grep -Fq '(HTTP 404)' "$response.err"; then
  cat "$response.err" >&2
  exit 1
fi
