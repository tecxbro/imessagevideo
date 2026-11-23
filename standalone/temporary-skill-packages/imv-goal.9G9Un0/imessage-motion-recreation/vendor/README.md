# Upstream source

The files under these two directories are verbatim excerpts. The upstream
entry documents use the local name `UPSTREAM.md` so the archive has a single
installable skill entry. Local integration lives in [upstream](../upstream/README.md).

| Source | Pin | Included source |
| --- | --- | --- |
| [REA Video](https://github.com/JuneYaooo/rea-video/tree/86486c6e104b917fb4b6a2d6501134686c05b219) | `86486c6e104b917fb4b6a2d6501134686c05b219` | Agent skill, references, VIDEO.md format, LICENSE and NOTICE |
| [HyperFrames](https://github.com/heygen-com/hyperframes/tree/7cb548e45b846683d74dac3c2108fedceb5d146a) | `7cb548e45b846683d74dac3c2108fedceb5d146a` | Creation, CLI, registry, media, style and reverse-video skills, the number pop-in component, LICENSE and CREDITS |

The project runtime installs the published HyperFrames npm CLI 0.9.77 and
REA Video from its Git commit. Source excerpts cover workflow documents and
code. Obtain any separately licensed media or fonts for a project and record
their provenance there.

The local runner uses direct CLI calls, stages GSAP as a local asset, uses
independent picture assets and original audio for recreation, and runs our
candidate-bound acceptance check. Upstream documents also cover online
services, telemetry, and global skill installation. The local workflow has
no dependencies on those features.
