This issue is the build room, and this body is the team brief. Every agent reads all of it before starting. It is part of your goal.

## The team

Seven Codex agents are building one reusable iMessage video skill at the same time, each in its own chat, all in this repo.

- **Observer** puts everyone's work behind one skill entry point, tests it on fresh agents, and decides what is ready for Darshan.
- **Recreation** takes a reference film and rebuilds it as editable source that matches the original.
- **Motion** builds the library of reusable movements and the tool that picks the right one for a request.
- **Dataset** finds real iMessage footage, takes it in with its source, rights and fingerprints, and feeds it to the team every week.
- **Direction** makes original films from a product brief, with no reference film.
- **Sound** designs, mixes and edits the audio and keeps it in sync with the picture.
- **Clone iMessage UI** builds the editable iMessage interface that every film renders with.

Your work counts once a teammate has run it, so talk to each other directly here. Darshan does not relay messages.

## Working together

**Branches.** Base commit `c49482aec7b8ed0b840f97c61a5e5b860c4077b6`. Branches are `codex-video-v3/` followed by `observer`, `recreate`, `motion`, `dataset`, `direction`, `sound` or `ui` (`ui` is Clone iMessage UI). Create yours from the base and push to it. If it already exists from your own earlier run, continue it. Leave `main` and the other six branches alone. Follow `AGENTS.md` in the repo for setup and for how the repo stores large files.

**This room.** There is only this one; never create another. Comments here don't notify anyone, so read the room when you start, at every milestone, before you ask for something, before you push, before you call anything done, and at least every 30 minutes.

**Handoffs.** When you give a teammate something, comment `TO <role> | <pushed commit>:<path> | run <command> | expect <result>`. They run it and reply `RAN <commit> | PASS <what they saw>` or `FAIL <step and output>`. A handoff with no reply has not landed. Answer every request addressed to you. If a teammate is silent for 30 minutes, post what you are missing, build against a clearly labelled stand-in, and keep going. You are not finished while a request to you is unanswered or something you depend on is still a stand-in.

**Ownership.** `S` means `skill/imessage-motion-recreation`. Your new work goes in `S/<your branch word>/` and films for review go in `review/imv-v3/<your branch word>/`. Dataset also owns `datasets/imessage/` and its intake workflow file. Existing code in the repo on your subject is yours to take over and extend; post which paths you have taken so two roles don't edit the same file. Only Observer edits `S/SKILL.md`, `S/checksums.json`, `S/version.json`, `S/contracts/` and the shared renderer code under `S/scripts/engines/`, because every branch depends on them. To change those, or anything a teammate owns, send the owner a patch.

**Media.** Hand over the exact file with its SHA-256, committed in your review folder and split above 24 MiB the way the repo's archives are. The receiver checks the hash and decodes that file.

**Evidence.** You judge picture from frames (contact sheets plus runs of consecutive frames around each event) and sound from measurements. Report them as that. Say "watched" or "listened" only about a named person who did. Work can be released as technically checked with human review pending. Unfinished films stay inside the team.

**Darshan.** Mark a comment `needs-darshan` only for credentials, spending, deployment, permissions, rights, or a product fact you cannot verify.

## Who gives what to whom

Each row is a promise on both sides: the giver sends it, and the receiver runs it and replies.

| Giver → receiver | What | It has landed when |
|---|---|---|
| Observer → everyone | shared contracts and a tiny moving example | each agent runs the example and gets the same event at the same frame |
| Observer → Dataset | fingerprint tool and exclusion list | Dataset's intake rejects an excluded test file |
| Observer → fresh testers, privately | a reserved film or the second brief | the tester confirms it arrived in an isolated workspace |
| Clone iMessage UI → Recreation, Motion, Direction | the interface adapter | each changes a state and renders it |
| Motion → Recreation, Direction | editable motions | each renders one in its own scene |
| Recreation → Motion | newly measured movements | Motion publishes each one or says why not |
| Dataset → Motion | new footage with its source, time range and the behavior spotted | Motion builds the motion or says why not |
| Direction → Motion | motions it invented for its film | Motion publishes each one or says why not |
| Motion, Clone iMessage UI → Sound | stable event IDs | Sound finds each event's frame in the picture |
| Sound → Motion, Clone iMessage UI, Recreation, Direction | cue anchors | each resolves one against its own picture clock |
| Clone iMessage UI, Motion → Dataset | a request for a missing capture: starting state, action, ending state | Dataset confirms what it will look for |
| Dataset → whoever asked | the capture, or a note that none was found | the requester reproduces the state or records the gap |
| Dataset → Observer | each new archive with its rights record and hashes | Observer registers it and a clean restore passes |
| Direction → Recreation | a request to measure a chosen passage | Direction says what it used from the measurement |
| Direction, Recreation → Sound | picture file, its hash and an event map | Sound confirms the hash and the event frames |
| Sound → Direction, Recreation | mix, stems and mux | the picture owner decodes the export and checks it |
| Every builder → Observer | sub-skill and runnable example | Observer runs it through the central skill |

## Notes by role, beyond the table

- **Observer.** Post the contracts here as your first handoff. Chase any row that was sent and not answered, or have a substitute run the same check.
- **Recreation.** Build with Clone iMessage UI's interface instead of redrawing Messages, and tell it which behaviors you keep having to redraw. Send Sound your clean silent picture, not the reference audio mux. Tell Direction which of your rules exist only for faithful copying, so they don't become rules for original films.
- **Motion.** Render through Clone iMessage UI's interface, and ask it for verified gestures and which layers move or stay fixed. Give Direction a search and render command early, and ask for a real brief your search handled badly.
- **Dataset.** Admit nothing until Observer's exclusions are in the repo. Put requests from Clone iMessage UI and Motion at the front of the scout's queue.
- **Direction.** Tell Clone iMessage UI which interactions your idea needs. Tell Motion where its suggestions helped or boxed the film in. Send Sound a playable rough cut and event map early, trade timing changes before picture lock, then send the locked picture and choose between the treatments it returns. Ask Recreation to measure a passage only after you have chosen an influence. Give Observer the film before the concept or script.
- **Sound.** Give Direction two treatments for one passage that matters. Build Recreation an independent soundtrack. Ask Recreation where its delivered picture differs from the reference. Give Observer unlabeled treatments to audition, and check that your revision resolves the notes that come back.
- **Clone iMessage UI.** Give Recreation, Motion and Direction an import, a small editable example, a render command and the frames to expect. Ask Recreation what it keeps redrawing and Direction what its film needs. Give Motion your verified gestures and which layers move or stay fixed. Ask Observer to change the conversation in ways you didn't design for. Answer each request with a commit, an import or command, and a moving example.

## Sources

Clone all six at these commits. Study all of them, including the ones that don't look like your subject. Copy whatever works, keep its license and notices, and build on top of it.

- https://github.com/tecxbro/imessagevideo/tree/c49482aec7b8ed0b840f97c61a5e5b860c4077b6
- https://github.com/theswerd/imessage-ui/tree/1f132909792ff540501385f91d37ef20629c55b7
- https://github.com/tecxbro/imessagedemo/tree/807e86e03e4a7e95ae6954b4a8c4dd5e031854bc
- https://github.com/heygen-com/hyperframes/tree/9813a6cbef97fffda70f5a147b87747f7e35a77b
- https://github.com/per-simmons/launch-video-clone/tree/7e97ac6488eb61ca4d25affe7fc1da7cfb80b376
- https://github.com/serenakeyitan/awesome-ai-clonable-launch-videos/tree/6a02fa07dfa5696ba3191dd905a06dbedc932e38

Some earlier work in imessagevideo is not in the base tree. Fetch these commits too:

- `a23bfb294fbc65739811a84f264ad306ca192fe1`: an earlier motion library
- `b525e7e11279db836bbdd2ff4b1b8953b56b946f`: an earlier conversation implementation
- `69595dfa2ef588a59d1b0b4d5836817a49d0f809`: a sound trial and its export checker
- `b303dde12ca8a314a36a7e70ed42e3e0f1605464`: the pinch-hit trial and its editorial notes

The repo already holds six accepted films, their silent picture masters, sound sources, and five working renderers: Python/Pillow with FFmpeg, JavaScript/TypeScript with GSAP, React/JSX with Remotion, HTML/CSS/SVG, and Motion Canvas. Find them, run them, and build on them.

These sources are where you start. Throughout the build, keep searching other repos, tools, films and real footage for anything better, and bring it in.

## How to build

You are here to build. Every attempt should end in code that runs or film that renders. Get a thin working version to your teammates early. Then keep going: render it, inspect the frames, fix what is wrong, try a second approach where one might be better and keep the winner, and widen what it covers. Use subagents to build in parallel and to check your work without your assumptions. You are done when a fresh agent can use your work without your help and another round no longer improves it. Observer makes the final call, so expect work to come back.
