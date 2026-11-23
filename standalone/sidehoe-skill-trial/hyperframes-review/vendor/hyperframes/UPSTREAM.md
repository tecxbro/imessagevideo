# HyperFrames reviewer source

The adjacent files listed in `SHA256SUMS` are byte-for-byte copies from
[heygen-com/hyperframes](https://github.com/heygen-com/hyperframes/tree/7cb548e45b846683d74dac3c2108fedceb5d146a)
at commit `7cb548e45b846683d74dac3c2108fedceb5d146a`. They include the CLI
commands for diff and snapshot review, their local imports, and the review
workflow. Apache 2.0 terms are in `LICENSE`. These excerpts are for code
review. The published `hyperframes@0.9.77` package supplies the executable
and its dependencies. Sidehoe uses the published `diff` command against
the final MP4.

From this directory run `shasum -a 256 -c SHA256SUMS` to verify the copy.
