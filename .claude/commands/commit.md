Analyse the files currently in git staging (use `git diff --cached`) and recent commit history (use `git log --oneline -10`).

Based on the staged changes:
1. Summarise what the changes do
2. Determine the type: fix, feat, refactor, chore, docs, test, etc.
3. Write a concise commit message following conventional commits format
4. Create the commit

Rules:
- The commit subject should be under 72 characters
- Use imperative mood ("add" not "added")
- If the changes span multiple concerns, use a multi-line commit message with a summary line and bullet points
- End the commit message with: Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
- If nothing is staged, tell the user and do not commit
