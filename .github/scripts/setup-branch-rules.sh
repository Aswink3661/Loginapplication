#!/usr/bin/env bash
# setup-branch-rules.sh
#
# Configures branch protection rules for the Loginapplication repository:
#   Rule 1 – Auto-delete head branches after a PR is merged.
#   Rule 2 – 'main' only accepts PRs from 'develop' (enforced via required
#             "Check PR Source Branch" CI status check).
#   Rule 3 – PRs cannot be merged before all CI checks pass.
#
# Usage:
#   export GITHUB_TOKEN=<your-personal-access-token>   # needs repo scope
#   bash .github/scripts/setup-branch-rules.sh
#
# The token requires the 'repo' scope.  A fine-grained token needs
# "Administration: Read & Write" and "Pull requests: Read & Write" on this repo.
# ---------------------------------------------------------------------------

set -euo pipefail

OWNER="Aswink3661"
REPO="Loginapplication"
API="https://api.github.com"

if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  echo "Error: GITHUB_TOKEN environment variable is not set."
  exit 1
fi

AUTH_HEADER="Authorization: Bearer ${GITHUB_TOKEN}"
CONTENT="Content-Type: application/json"
ACCEPT="Accept: application/vnd.github+json"
API_VERSION="X-GitHub-Api-Version: 2022-11-28"

# ── Helper ──────────────────────────────────────────────────────────────────

github_api() {
  local method="$1"
  local path="$2"
  local body="${3:-}"

  if [[ -n "$body" ]]; then
    curl -sS -X "$method" \
      -H "$AUTH_HEADER" -H "$ACCEPT" -H "$CONTENT" -H "$API_VERSION" \
      "${API}${path}" \
      -d "$body"
  else
    curl -sS -X "$method" \
      -H "$AUTH_HEADER" -H "$ACCEPT" -H "$CONTENT" -H "$API_VERSION" \
      "${API}${path}"
  fi
}

# ── Rule 1: Auto-delete head branch after merge ──────────────────────────────
echo "==> [Rule 1] Enabling auto-delete of head branches after merge..."

response=$(github_api PATCH "/repos/${OWNER}/${REPO}" \
  '{"delete_branch_on_merge": true}')

if echo "$response" | grep -q '"delete_branch_on_merge": true'; then
  echo "    ✓ Auto-delete head branches is enabled."
else
  echo "    Response: $response"
  echo "    Warning: Could not confirm setting. Check the response above."
fi

# ── Rule 3 + Rule 2 (develop): Protect 'develop' branch ─────────────────────
# Requires 'All Checks Passed' status check before merge.
echo ""
echo "==> [Rule 3] Setting branch protection for 'develop'..."

DEVELOP_PROTECTION=$(cat <<'JSON'
{
  "required_status_checks": {
    "strict": false,
    "contexts": ["All Checks Passed"]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": false,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 0
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
JSON
)

response=$(github_api PUT "/repos/${OWNER}/${REPO}/branches/develop/protection" \
  "$DEVELOP_PROTECTION")

if echo "$response" | grep -q '"url"'; then
  echo "    ✓ 'develop' branch protection applied:"
  echo "      - Required status check: 'All Checks Passed'"
  echo "      - Force pushes: blocked"
  echo "      - Branch deletion: blocked"
else
  echo "    Response: $response"
  echo "    Warning: Could not confirm 'develop' protection. Check the response above."
fi

# ── Rule 2 + Rule 3 (main): Protect 'main' branch ───────────────────────────
# Requires BOTH 'All Checks Passed' AND 'Check PR Source Branch'.
# The 'Check PR Source Branch' CI job fails unless the PR comes from 'develop'.
echo ""
echo "==> [Rule 2 + Rule 3] Setting branch protection for 'main'..."

MAIN_PROTECTION=$(cat <<'JSON'
{
  "required_status_checks": {
    "strict": false,
    "contexts": ["All Checks Passed", "Check PR Source Branch"]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": false,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 0
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
JSON
)

response=$(github_api PUT "/repos/${OWNER}/${REPO}/branches/main/protection" \
  "$MAIN_PROTECTION")

if echo "$response" | grep -q '"url"'; then
  echo "    ✓ 'main' branch protection applied:"
  echo "      - Required status checks: 'All Checks Passed', 'Check PR Source Branch'"
  echo "      - Force pushes: blocked"
  echo "      - Branch deletion: blocked"
else
  echo "    Response: $response"
  echo "    Warning: Could not confirm 'main' protection. Check the response above."
fi

echo ""
echo "Done. Summary of applied rules:"
echo "  [Rule 1] Head branch auto-deleted after every merged PR."
echo "  [Rule 2] 'main' only accepts PRs from 'develop' (CI-enforced)."
echo "  [Rule 3] PRs to 'main' and 'develop' cannot merge before CI passes."
