RELEASE NOTES — v4.0.2

Summary
-------
This patch fixes a truncation/regression introduced in the v4.x line where answers could be cut off mid-currency (e.g., "Rs. 10,000" became "Rs.") and restores the stricter answer length target that was used previously.

What changed
------------
- Restored the stricter length cutoff for generated answers (45–70 words target; truncation cutoff set to 70 words).
- Added logic to detect currency markers (e.g., "Rs.", "₹", "PKR", "Rupees") and append subsequent token(s) when truncation would split a currency+number pair so numeric amounts are not lost.
- Preserved the prior behavior of preferring sentence-boundary truncation and ensuring proper sentence termination.
- Added unit-safe protections to avoid over-appending (limits appended words to 5 and only until a numeric token is included).

Why this fixes the problem
--------------------------
Users reported repeated cases where currency mentions were truncated, causing misleading and incomplete answers. Restoring the original length policy while protecting currency/number token pairs preserves concise answers while preventing the bad cutoff.

Testing notes
-------------
- Manual tests: queries that end with currency mentions such as "What is the limit?" with answers like "The fee is Rs. 10,000 per application" should now return the full amount.
- Smoke test: run the Flask backend and issue a /chat request with a prompt designed to elicit a currency-ended sentence; verify the returned answer is not truncated.

Deployment
----------
This release is a small backend-only fix. Deploy by updating the server with the latest code and restarting the API process (or redeploy container if used).

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
