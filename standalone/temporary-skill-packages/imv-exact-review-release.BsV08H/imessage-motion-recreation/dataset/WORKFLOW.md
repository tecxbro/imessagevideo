---
name: imessage-dataset
description: Verify source and reuse rights, apply Observer's exclusion gate, and register and restore iMessage footage for the UI and Motion teams.
---

# iMessage Dataset

Use [the dataset intake](../../../datasets/imessage/README.md) from the
repository checkout. Before accepting footage, compare the proposed take
against [the capture queue](../../../datasets/imessage/CAPTURES.md).

```sh
python3 datasets/imessage/prove.py
```

Use the capture manifest's decoded frame and PTS ranges for a UI or Motion
handoff. Report unavailable states as capture gaps. Keep reserve identities
and footage in Observer's private workspace.
