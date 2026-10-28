# Contributing

Contributions are welcome when they preserve the public/private boundary and
make the method easier to reproduce or audit.

Before opening a change:

1. Run `python3 -m unittest discover -s tests -v`.
2. Run `python3 scripts/release_check.py`.
3. Use only synthetic examples unless a dataset has documented redistribution
   rights and a file-level rights review. A public URL is not permission to copy
   the linked data.
4. Add provenance for copied or adapted material and retain all required
   notices.
5. Keep proposed method changes separate from faithful-reproduction fixes.
6. Do not add voter data, addresses, precise coordinates, recordings, logs, sessions, credentials,
   private product code, campaign/news text, donor rows, or partner material.

By submitting a contribution, you agree that code and documentation may be
released under MIT and curated data annotations may be released under CC BY
4.0. Synthetic fixture contributions must be safe to dedicate under CC0 1.0
and must not encode a real person, address, or precise coordinate.

Bug reports should include a minimal synthetic input, the observed result, the
expected result, and whether the report concerns the pinned method or a proposed
change. Please do not disclose secrets or personal data in an issue.

