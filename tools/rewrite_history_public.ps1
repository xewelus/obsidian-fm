$ErrorActionPreference = 'Stop'

# Rewrite only 'master' ref so our backup branch stays untouched.
# Requires: python -m git_filter_repo

python -m git_filter_repo --force --refs master `
  --path .claude --invert-paths `
  --path ai --invert-paths `
  --path-glob '**/__pycache__/**' --invert-paths `
  --path-glob '**/*.pyc' --invert-paths `
  --path-glob '**/*.egg-info/**' --invert-paths `
  --replace-text .gitfilter-repo-replace.txt
