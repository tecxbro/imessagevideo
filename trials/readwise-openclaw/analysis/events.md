# Readwise / OpenClaw — source event inventory

**Analysis only.** 3840×2160, 30 fps, 1110 frames / 37 seconds. All frame numbers are **0-based**; intervals include both endpoints. Coordinates are in original source pixels. No film implementation or source media is included.

**Coverage notice:** principal copy, title/composer/command glyph timing, shot boundaries and major interactions were measured. This is a bounded inventory, not an exhaustive frame-exact transcription of every small UI label or keyboard prediction. Unresolved items are listed explicitly below and in JSON.

## Shots and transitions

| Shot | Frames | Content |
|---|---:|---|
| S1 | 0–67 | Gradient/title |
| S2 | 68–138 | Tilted Twitter/X bookmark close-up |
| S3 | 139–210 | Tilted browser/Reader save |
| S4 | 211–333 | YouTube share sheet, Reader saved screen, phone zoom-out |
| S5 | 334–403 | Gradient-only lead-in 334–342, typed title 343–402, gradient-only frame 403 |
| S6 | 404–990 | Ghosty chat |
| S7 | 991–1099 | Readwise icon fades in; command types; large faint arc |
| black_tail | 1100–1109 | Abrupt black; codec residual at 1100, exact zero from 1101 |

**Important correction to rough timing:** phone disappears at 334; title disappears at 403; chat starts at 404; end card begins at 991; command starts at 997. The ending is an abrupt cut to black at 1100, not a gradual fade. Frame 1100 has tiny codec residuals; 1101–1109 are zero black. End-card icon interior sample changes from 994 through 1023 and settles at 1024; fringe onset can differ.

## Text reveal tracks

Each table records a new visible prefix. Multiple glyphs can arrive in one source frame. The JSON also expands every final string to individual character indices/first-visible frames. Spaces have no glyph and use `space_present_by_frame`, not fabricated key-down times.

### S1.title

Final display:
```
Save from anywhere.
```

| Frame | Visible prefix |
|---:|---|
| 9 | `S` |
| 10 | `Sa` |
| 11 | `Sav` |
| 12 | `Save` |
| 14 | `Save f` |
| 15 | `Save fr` |
| 16 | `Save fro` |
| 17 | `Save from` |
| 19 | `Save from a` |
| 20 | `Save from an` |
| 21 | `Save from any` |
| 22 | `Save from anyw` |
| 23 | `Save from anywh` |
| 24 | `Save from anywhe` |
| 25 | `Save from anywher` |
| 26 | `Save from anywhere` |
| 27 | `Save from anywhere.` |

### S5.title

Final display:
```
Your OpenClaw already knows.
```

| Frame | Visible prefix |
|---:|---|
| 343 | `Y` |
| 344 | `Yo` |
| 345 | `Your` |
| 347 | `Your O` |
| 348 | `Your Ope` |
| 349 | `Your Open` |
| 350 | `Your OpenCl` |
| 351 | `Your OpenCla` |
| 352 | `Your OpenClaw` |
| 353 | `Your OpenClaw a` |
| 354 | `Your OpenClaw al` |
| 355 | `Your OpenClaw alr` |
| 356 | `Your OpenClaw alrea` |
| 357 | `Your OpenClaw alread` |
| 358 | `Your OpenClaw already` |
| 359 | `Your OpenClaw already k` |
| 360 | `Your OpenClaw already kn` |
| 361 | `Your OpenClaw already know` |
| 362 | `Your OpenClaw already knows` |
| 363 | `Your OpenClaw already knows.` |

### S6.user1.composer

Final display:
```
What did I save today?
Give me a brief summary
on each.
```

| Frame | Visible prefix |
|---:|---|
| 456 | `W` |
| 457 | `Wh` |
| 458 | `Wha` |
| 459 | `What` |
| 462 | `What d` |
| 463 | `What di` |
| 464 | `What did` |
| 468 | `What did I` |
| 473 | `What did I s` |
| 475 | `What did I sa` |
| 477 | `What did I save` |
| 479 | `What did I save t` |
| 480 | `What did I save to` |
| 482 | `What did I save tod` |
| 483 | `What did I save toda` |
| 484 | `What did I save today` |
| 488 | `What did I save today?` |
| 494 | `What did I save today? G` |
| 496 | `What did I save today? Gi` |
| 498 | `What did I save today? Giv` |
| 499 | `What did I save today? Give` |
| 501 | `What did I save today? Give me` |
| 504 | `What did I save today? Give me a` |
| 512 | `What did I save today? Give me a b` |
| 513 | `What did I save today? Give me a br` |
| 514 | `What did I save today? Give me a bri` |
| 515 | `What did I save today? Give me a brie` |
| 516 | `What did I save today? Give me a brief` |
| 518 | `What did I save today? Give me a brief s` |
| 519 | `What did I save today? Give me a brief su` |
| 521 | `What did I save today? Give me a brief sum` |
| 522 | `What did I save today? Give me a brief summ` |
| 523 | `What did I save today? Give me a brief summa` |
| 524 | `What did I save today? Give me a brief summar` |
| 525 | `What did I save today? Give me a brief summary` |
| 529 | `What did I save today? Give me a brief summary o` |
| 531 | `What did I save today? Give me a brief summary on` |
| 533 | `What did I save today? Give me a brief summary on e` |
| 535 | `What did I save today? Give me a brief summary on ea` |
| 537 | `What did I save today? Give me a brief summary on eac` |
| 538 | `What did I save today? Give me a brief summary on each` |
| 541 | `What did I save today? Give me a brief summary on each.` |

### S6.user2.composer

Final display:
```
Which one should I read
first?
```

| Frame | Visible prefix |
|---:|---|
| 757 | `W` |
| 759 | `Wh` |
| 761 | `Whi` |
| 763 | `Whic` |
| 764 | `Which` |
| 767 | `Which o` |
| 769 | `Which one` |
| 772 | `Which one s` |
| 773 | `Which one sh` |
| 775 | `Which one sho` |
| 776 | `Which one shou` |
| 778 | `Which one shoul` |
| 779 | `Which one should` |
| 781 | `Which one should I` |
| 785 | `Which one should I r` |
| 787 | `Which one should I re` |
| 789 | `Which one should I rea` |
| 790 | `Which one should I read` |
| 793 | `Which one should I read f` |
| 794 | `Which one should I read fir` |
| 796 | `Which one should I read first` |
| 802 | `Which one should I read first?` |

### S7.command

Final display:
```
npx clawhub install readwise-official
```

| Frame | Visible prefix |
|---:|---|
| 997 | `n` |
| 998 | `npx` |
| 999 | `npx c` |
| 1000 | `npx cla` |
| 1001 | `npx clawh` |
| 1002 | `npx clawhu` |
| 1003 | `npx clawhub` |
| 1004 | `npx clawhub in` |
| 1005 | `npx clawhub inst` |
| 1006 | `npx clawhub instal` |
| 1007 | `npx clawhub install` |
| 1008 | `npx clawhub install r` |
| 1009 | `npx clawhub install rea` |
| 1010 | `npx clawhub install readw` |
| 1011 | `npx clawhub install readwis` |
| 1012 | `npx clawhub install readwise` |
| 1013 | `npx clawhub install readwise-off` |
| 1014 | `npx clawhub install readwise-offic` |
| 1015 | `npx clawhub install readwise-offic` |
| 1016 | `npx clawhub install readwise-officia` |
| 1017 | `npx clawhub install readwise-official` |

## Other visible copy

Line breaks below preserve the settled display layout unless explicitly labeled clipped fragments.

### S2.post.visible_fragments

```
/schedule - create scheduled jobs for claude in the cloud
… PM · Mar 23, 2026 · 100K Views
73
118
1.4K
932 → 933
View quotes >
Post your reply
Reply
Trending in Canada
Toronto
Sports · Trending
Odegaard
Sports · Trending
Vancouver
Show more
Terms of Service
Accessibility
```
- **status:** Clipped UI: ellipsis denotes off-screen text, not a source glyph. Exact left-clipped time/date prefix and partially off-screen footer wording unresolved. Stats 118, 1.4K, 932/933 visually checked; 73 partly clipped.

### S2.tooltip.before

```
Bookmark
```
- **first_frame:** 99
- **last_frame:** 106

### S2.tooltip.after

```
Remove from Bookmarks
```
- **first_frame:** 107
- **last_frame:** 131

### S2.toast

```
Added to your Bookmarks    Add to Folder
```
- **layout:** single horizontal row, not two source lines
- **first_frame:** 120
- **last_frame:** 138

### S3.url

```
…-the-compounding-teams
```
- **status:** left clipped; OCR at 139 reads ave-seen-the-compounding-teams

### S3.article

```
…at are compounding aren’t writing code at all. The each have built a
…ce the Amplifier framework) around a model. They will have some
…to Claude Code or Codex - something that has callback hooks, tool
…control, but then the system they build will be much more proactive.
…s of strategies, tools, opinions and behaviors that let it run more
…of the teams I’ve seen doing this so far are making extensive use
…ing tools to give the system access to itself. All are heavily
…t, use markdown, kubernetes, xml and other common tools. I
…e of software at scale will be built on these programmer tools,
…the same way models will sometimes privately write code
…asked by a non-coder. It’s fairly clear that these are good
```
- **status:** Serif italic body is clipped at left and bottom. Below are observed line fragments, not completed invented sentences; exact full transcription unresolved.

### S3.toolbar

```
Auto highlighting
Ink
```
- **status:** Additional small toolbar labels are partially clipped/unresolved.
- **first_frame:** 171
- **last_frame:** 210

### S3.toast

```
Saved to Reader
```
- **first_frame:** 175
- **last_frame:** 210

### S4.youtube.actions

```
Share
Ask
Remix
Thanks
Clip
Report
```
- **status:** Visible left-side action strip; other cropped video text is unresolved.
- **first_frame:** 211
- **last_frame:** 234

### S4.share_sheet

```
The collapse of modern a...
youtube.com
SharePlay
AirDrop
Reader
Slack
Messages
Copy
Add to New Quick Note
Save Document to Reader
Find products on Amazon
```
- **status:** Sheet slides upward 235–240. Header title/thumbnail finish loading after first appearance. Header truncation punctuation transcribed visually; final row cropped at some camera positions.
- **first_frame:** 235
- **last_frame:** 272

### S4.saved

```
R
Saved to Reader
Read Now
Tap anywhere to dismiss
```
- **other_content:** Five round action icons, no additional readable labels.
- **first_frame:** 278
- **last_frame:** 333

### S6.chrome

```
9:41
Ghosty
bot
No messages here yet...
Message
Today
Unread Messages
```
- **status:** Persistent and conditional chrome. Header changes to animated dots + typing while bot waits; exact typing-indicator boundary frames unresolved.

### S6.user1.bubble

```
What did I save today? Give me a brief summary on each.
```
- **timestamp:** 7:31 PM
- **first_frame:** 569

### S6.bot1

```
Same 3 saves today:

1. Noah Zweben tweet — Claude added /
schedule for recurring cloud jobs from
the terminal. Useful for CI fixes, doc
updates, automations that run while your
laptop's closed.
2. Cal Newport video — AI "workslop" is
creating more noise, not less work. Talks
about reclaiming focus, deep work
strategies, and whether AI tools have
actually delivered.
3. Sam Schillace article —
"Compounding teams" that go beyond
vibe coding — teams integrating AI deeply
to multiply their output over time.
```
- **timestamp:** 7:32 PM
- **bold_runs:** ['Noah Zweben tweet', 'Cal Newport video', 'Sam Schillace article']
- **status:** Intro scrolls out of viewport as bubble grows. Display linebreaks correspond to settled chat-width layout, not composer.
- **first_frame:** 644
- **complete_readable_by_frame:** 692

### S6.user2.bubble

```
Which one should I read first?
```
- **timestamp:** 7:32 PM
- **first_frame:** 830

### S6.bot2

```
The Sam Schillace article — it's a quick
4-min read and the most relevant to you
as a product designer working on a tool
people use daily. Understanding how
"compounding teams" work with AI could
directly inform how you think about
Reader's design.

The Cal Newport video is good but it's a
long watch — save it for when you have
time. The tweet is just a feature
announcement, low priority.
```
- **timestamp:** 7:32 PM
- **bold_runs:** ['Sam Schillace article']
- **first_frame:** 889
- **complete_readable_by_frame:** 942

### S7.icon

```
R
```
- **note:** Readwise icon is editable geometry to reconstruct later; no source image included.

## Interactions and response reveals

### S2.bookmark

- **hover_blue_halo_by_frame:** 94
- **tooltip_first_frame:** 99
- **tooltip_first_absent_frame:** 132
- **cursor_press_visual_range:** [100, 112]
- **cursor_minimum_size_frame:** 104
- **bookmark_filled_frame:** 107
- **count_scroll_first_frame:** 111
- **count_933_settled_frame:** 112
- **physical_click_frame:** None
- **note:** Visible response is exact 107; OS click is inferred, not observable as an event log.

### S2.toast_motion

- **first_frame:** 120
- **last_frame:** 138
- **motion:** Enters from below/right with tilt matching UI plane; most of slide occurs between 119 and 120. At 120 blue visible bbox in full-source px [730,1780,3020,2160], clipped by bottom. No exit before cut.
- **precision:** Exact first blue frame measured; full transformed toast bounds unresolved.

### S3.extension

- **cursor_press_visual_range:** [150, 160]
- **cursor_minimum_size_frame_estimate:** 154
- **response_toolbar_first_frame:** 171
- **response_toolbar_readable_frame:** 172
- **toast_first_frame:** 175
- **toast_slide_settled_by_frame:** 180
- **physical_click_frame:** None
- **note:** Cursor visibly shrinks then rebounds; no separately logged physical mouse event. Blue badge/check is visible later. Toast grows/slides leftward out from right, not a cut.

### S4.share

- **sheet_first_visible_frame:** 235
- **sheet_slide_settled_by_frame:** 240
- **share_tap_frame:** None
- **note:** YouTube actions visible through 234; no clearly isolated finger/tap marker recovered.

### S4.reader

- **highlight_first_frame:** 268
- **highlight_last_frame:** 268
- **release_frame:** 269
- **reader_panel_slide_first_frame:** 272
- **spinner_first_frame:** 274
- **spinner_last_frame:** 277
- **saved_screen_first_frame:** 278
- **note:** Reader icon darkens for one sampled frame 268; no finger marker. 272 split sliding screen, 273 blank Reader panel, 274–277 spinner.

### S6.send1

- **last_composer_only_frame:** 568
- **first_outgoing_bubble_frame:** 569
- **composer_empty_by_frame:** 571
- **bubble_settled_by_frame:** 573
- **send_press_frame:** None
- **note:** 569 is observed send animation start; physical tap frame not separately visible.

### S6.bot1.stream

- **mode:** streamed chunks with animated bubble growth/scroll; not instant and not strictly one line per update
- **first_frame:** 644
- **chunks:** [{"first_frame": 644, "readable_by_frame": 646, "ends_with": "schedule for"}, {"first_frame": 659, "readable_by_frame": 661, "ends_with": "updates, automations that run while"}, {"first_frame": 674, "readable_by_frame": 678, "ends_with": "actually delivered"}, {"first_frame": 689, "readable_by_frame": 692, "ends_with": "to multiply their output over time."}]
- **note:** Chunk additions every 15 frames; intervening frames show layout/scroll interpolation. Exact sub-frame source text insertion is not recoverable.

### S6.send2

- **last_composer_only_frame:** 829
- **first_outgoing_bubble_frame:** 830
- **composer_empty_by_frame:** 833
- **bubble_settled_by_frame:** 835
- **send_press_frame:** None

### S6.bot2.stream

- **mode:** streamed chunks with animated bubble growth/scroll
- **first_frame:** 889
- **chunks:** [{"first_frame": 889, "readable_by_frame": 891, "ends_with": "4-min"}, {"first_frame": 905, "readable_by_frame": 907, "ends_with": "as a product designer working"}, {"first_frame": 922, "readable_by_frame": 926, "ends_with": "long"}, {"first_frame": 939, "readable_by_frame": 942, "ends_with": "announcement, low priority."}]
- **precision:** First readable new glyph in inspected adjacent frames; low-opacity/layout onset may precede the readable state by one frame.

## Cursor

source px; tip = topmost white contour pixel; bbox scaled from 1920 analysis frame. Estimated accuracy ±6 px after thresholding; some badge contamination noted in JSON.

| Frame | Tip x,y | Visible bbox x0,y0,x1,y1 |
|---:|---|---|
| 90 | [2512, 1292] | [2512, 1292, 2770, 1680] |
| 92 | [2440, 1234] | [2440, 1234, 2704, 1630] |
| 93 | [2416, 1216] | [2416, 1216, 2682, 1614] |
| 94 | [2384, 1190] | [2384, 1190, 2650, 1592] |
| 96 | [2352, 1166] | [2352, 1166, 2618, 1570] |
| 98 | [2332, 1150] | [2332, 1150, 2606, 1558] |
| 100 | [2324, 1144] | [2324, 1144, 2592, 1548] |
| 103 | [2322, 1140] | [2322, 1140, 2552, 1488] |
| 104 | [2322, 1140] | [2322, 1140, 2546, 1480] |
| 108 | [2324, 1146] | [2324, 1146, 2572, 1518] |
| 109 | [2324, 1146] | [2324, 1146, 2580, 1534] |
| 110 | [2324, 1146] | [2324, 1146, 2586, 1540] |
| 111 | [2324, 1146] | [2324, 1146, 2590, 1546] |
| 112 | [2324, 1146] | [2324, 1146, 2592, 1550] |
| 113 | [2324, 1146] | [2324, 1146, 2592, 1550] |
| 118 | [2326, 1146] | [2324, 1146, 2594, 1554] |
| 119 | [2326, 1146] | [2324, 1146, 2594, 1554] |
| 120 | [2326, 1146] | [2324, 1146, 2594, 1554] |
| 121 | [2326, 1146] | [2324, 1146, 2594, 1554] |
| 123 | [2326, 1146] | [2324, 1146, 2594, 1554] |
| 128 | [2336, 1174] | [2336, 1174, 2608, 1580] |
| 133 | [2384, 1250] | [2384, 1250, 2648, 1656] |
| 138 | [2480, 1392] | [2480, 1392, 2744, 1798] |
| 149 | [3060, 332] | [3010, 332, 3228, 634] |
| 150 | [3066, 336] | [3020, 336, 3228, 624] |
| 154 | [3072, 346] | [3034, 346, 3214, 596] |
| 155 | [3074, 348] | [3034, 348, 3216, 600] |
| 159 | [3076, 344] | [3026, 344, 3240, 642] |
| 160 | [3076, 344] | [3026, 344, 3242, 646] |
| 164 | [3076, 344] | [3024, 344, 3246, 652] |
| 165 | [3076, 344] | [3024, 344, 3246, 652] |
| 169 | [3076, 344] | [3024, 344, 3246, 652] |
| 170 | [3102, 336] | [3024, 336, 3248, 652] |
| 171 | [3102, 336] | [3024, 336, 3248, 652] |
| 172 | [3106, 334] | [3024, 334, 3248, 652] |
| 173 | [3076, 344] | [3024, 344, 3248, 652] |
| 174 | [3076, 344] | [3024, 344, 3248, 652] |
| 175 | [3076, 344] | [3024, 344, 3248, 652] |
| 179 | [3076, 344] | [3024, 344, 3248, 652] |
| 180 | [3096, 344] | [3024, 344, 3246, 652] |
| 184 | [3096, 344] | [3024, 344, 3246, 652] |

## Keyboard

Alphabetic layout: `qwertyuiop / asdfghjkl / zxcvbnm`; shift, delete, `123`, emoji, `space`, `return`, microphone. Numeric layout: `1234567890 / - / : ; ( ) $ & @ ” / . , ? ! ’`; `#+=`, `ABC`, delete, emoji, space, return.

Observed numeric transitions at 485, 539 and 799; alphabetic state observed again at 490 and 740. Exact transient case, popups and all predictive transitions remain incomplete. Full partial OCR prediction observations are in JSON, explicitly **not ground truth**. Selected visually read examples:

- {'frame': 450, 'middle': 'the', 'right': 'i’m'}
- {'frame': 478, 'middle': 'dab'}
- {'frame': 484, 'middle': 'today’s'}
- {'frame': 516, 'middle': 'brief'}
- {'frame': 523, 'middle': 'summary'}
- {'frame': 538, 'middle': 'each'}
- {'frame': 542, 'middle': 'thank'}
- {'frame': 750, 'middle': 'the', 'right': 'i’m'}
- {'frame': 760, 'middle': 'Eh'}
- {'frame': 769, 'middle': 'on'}
- {'frame': 789, 'middle': 'read'}
- {'frame': 795, 'middle': 'firxt'}
- {'frame': 796, 'middle': 'first'}
- {'frame': 804, 'middle': 'the'}

## Camera / framing

Foreground mask versus gradient-only frame 340, RGB max difference >27 at 480x270. Largest connected-component visible bbox; central scanline estimates phone rails. All coordinates scaled 8x. Shadows excluded approximately, rails can be 8–16px uncertain. Visible bbox is clipped, not extrapolated full phone bounds.

The scale column uses a 904px-wide whole-phone reference. Bboxes describe visible foreground, not extrapolated offscreen phone bounds.

| Frame | Visible bbox | Rail center x | Rail width | Relative scale |
|---:|---|---:|---:|---:|
| 211 | [1096, 0, 2792, 2160] | 1952.0 | 1600 | 1.76991 |
| 221 | [1144, 0, 2768, 2160] | 1960.0 | 1584 | 1.75221 |
| 230 | [1168, 0, 2768, 2160] | 1964.0 | 1576 | 1.74336 |
| 231 | [1168, 0, 2768, 2160] | 1964.0 | 1576 | 1.74336 |
| 240 | [1168, 0, 2768, 2160] | 1964.0 | 1576 | 1.74336 |
| 241 | [1168, 0, 2768, 2160] | 1964.0 | 1576 | 1.74336 |
| 251 | [1168, 0, 2768, 2160] | 1964.0 | 1576 | 1.74336 |
| 261 | [1168, 0, 2768, 2160] | 1964.0 | 1576 | 1.74336 |
| 270 | [1168, 0, 2768, 2160] | 1964.0 | 1576 | 1.74336 |
| 271 | [1168, 0, 2768, 2160] | 1964.0 | 1576 | 1.74336 |
| 280 | [1168, 0, 2768, 2160] | 1964.0 | 1576 | 1.74336 |
| 281 | [1168, 0, 2768, 2160] | 1964.0 | 1576 | 1.74336 |
| 290 | [1216, 0, 2736, 2160] | 1968.0 | 1520 | 1.68142 |
| 291 | [1224, 0, 2720, 2160] | 1964.0 | 1496 | 1.65487 |
| 300 | [1328, 0, 2608, 2160] | 1960.0 | 1264 | 1.39823 |
| 301 | [1336, 0, 2592, 2160] | 1960.0 | 1248 | 1.38053 |
| 310 | [1392, 0, 2536, 2160] | 1956.0 | 1128 | 1.24779 |
| 311 | [1400, 0, 2520, 2160] | 1956.0 | 1128 | 1.24779 |
| 320 | [1408, 16, 2496, 2152] | 1948.0 | 1064 | 1.17699 |
| 321 | [1424, 16, 2496, 2152] | 1948.0 | 1064 | 1.17699 |
| 330 | [1432, 48, 2488, 2144] | 1948.0 | 1048 | 1.15929 |
| 331 | [1432, 56, 2488, 2152] | 1948.0 | 1048 | 1.15929 |
| 333 | [1432, 56, 2488, 2144] | 1964.0 | 1016 | 1.12389 |
| 404 | [1464, 128, 2384, 2056] | 1932.0 | 904 | 1.0 |
| 414 | [1464, 128, 2384, 2056] | 1932.0 | 904 | 1.0 |
| 420 | [1464, 128, 2384, 2056] | 1932.0 | 904 | 1.0 |
| 424 | [1416, 64, 2432, 2160] | 1932.0 | 1000 | 1.10619 |
| 425 | [1376, 8, 2480, 2160] | 1932.0 | 1064 | 1.17699 |
| 430 | [1232, 0, 2688, 2160] | 1924.0 | 1368 | 1.51327 |
| 434 | [1184, 0, 2736, 2160] | 1932.0 | 1464 | 1.61947 |
| 435 | [1184, 0, 2736, 2160] | 1928.0 | 1472 | 1.62832 |
| 440 | [1168, 0, 2752, 2160] | 1932.0 | 1496 | 1.65487 |
| 444 | [1168, 0, 2744, 2160] | 1928.0 | 1504 | 1.66372 |
| 445 | [1168, 0, 2744, 2160] | 1928.0 | 1504 | 1.66372 |
| 450 | [1168, 0, 2768, 2160] | 1932.0 | 1512 | 1.67257 |
| 454 | [1168, 0, 2768, 2160] | 1932.0 | 1512 | 1.67257 |
| 464 | [1168, 0, 2768, 2160] | 1932.0 | 1512 | 1.67257 |
| 474 | [1168, 0, 2768, 2160] | 1932.0 | 1512 | 1.67257 |
| 484 | [1168, 0, 2784, 2160] | 1932.0 | 1512 | 1.67257 |
| 494 | [1168, 0, 2784, 2160] | 1932.0 | 1512 | 1.67257 |
| 504 | [1168, 0, 2784, 2160] | 1932.0 | 1512 | 1.67257 |
| 514 | [1168, 0, 2784, 2160] | 1932.0 | 1512 | 1.67257 |
| 524 | [1168, 0, 2784, 2160] | 1932.0 | 1512 | 1.67257 |
| 534 | [1168, 0, 2784, 2160] | 1932.0 | 1512 | 1.67257 |
| 544 | [1168, 0, 2752, 2160] | 1928.0 | 1504 | 1.66372 |
| 554 | [1168, 0, 2752, 2160] | 1928.0 | 1504 | 1.66372 |
| 564 | [1168, 0, 2768, 2160] | 1928.0 | 1504 | 1.66372 |
| 574 | [1168, 0, 2768, 2160] | 1928.0 | 1504 | 1.66372 |
| 584 | [1168, 0, 2768, 2160] | 1928.0 | 1504 | 1.66372 |
| 590 | [1168, 0, 2768, 2160] | 1928.0 | 1504 | 1.66372 |
| 594 | [1168, 0, 2768, 2160] | 1928.0 | 1504 | 1.66372 |
| 595 | [1168, 0, 2768, 2160] | 1928.0 | 1504 | 1.66372 |
| 600 | [1168, 0, 2768, 2160] | 1928.0 | 1504 | 1.66372 |
| 604 | [1280, 0, 2640, 2160] | 1936.0 | 1280 | 1.41593 |
| 605 | [1312, 0, 2584, 2160] | 1932.0 | 1192 | 1.31858 |
| 610 | [1424, 72, 2424, 2160] | 1928.0 | 992 | 1.09735 |
| 614 | [1456, 112, 2400, 2080] | 1924.0 | 936 | 1.0354 |
| 615 | [1456, 120, 2400, 2072] | 1928.0 | 912 | 1.00885 |
| 620 | [1464, 128, 2384, 2056] | 1932.0 | 904 | 1.0 |
| 624 | [1464, 128, 2384, 2056] | 1932.0 | 904 | 1.0 |
| 625 | [1464, 128, 2384, 2056] | 1932.0 | 904 | 1.0 |
| 630 | [1464, 128, 2384, 2056] | 1932.0 | 904 | 1.0 |
| 634 | [1464, 128, 2384, 2056] | 1932.0 | 904 | 1.0 |
| 644 | [1464, 128, 2384, 2056] | 1932.0 | 904 | 1.0 |
| 654 | [1464, 128, 2384, 2056] | 1932.0 | 904 | 1.0 |
| 664 | [1464, 128, 2384, 2056] | 1932.0 | 904 | 1.0 |
| 674 | [1464, 128, 2384, 2056] | 1932.0 | 904 | 1.0 |
| 684 | [1464, 128, 2384, 2056] | 1932.0 | 904 | 1.0 |
| 694 | [1464, 128, 2384, 2056] | 1932.0 | 904 | 1.0 |
| 704 | [1464, 128, 2384, 2056] | 1932.0 | 904 | 1.0 |
| 714 | [1464, 128, 2384, 2056] | 1932.0 | 904 | 1.0 |
| 724 | [1464, 128, 2384, 2056] | 1932.0 | 904 | 1.0 |
| 730 | [1464, 128, 2384, 2056] | 1932.0 | 904 | 1.0 |
| 734 | [1440, 96, 2400, 2088] | 1932.0 | 936 | 1.0354 |
| 735 | [1416, 40, 2432, 2160] | 1932.0 | 1000 | 1.10619 |
| 740 | [1248, 0, 2656, 2160] | 1928.0 | 1328 | 1.46903 |
| 744 | [1192, 0, 2720, 2160] | 1928.0 | 1456 | 1.61062 |
| 745 | [1184, 0, 2728, 2160] | 1928.0 | 1456 | 1.61062 |
| 750 | [1176, 0, 2744, 2160] | 1932.0 | 1496 | 1.65487 |
| 754 | [1168, 0, 2744, 2160] | 1928.0 | 1504 | 1.66372 |
| 764 | [1168, 0, 2776, 2160] | 1928.0 | 1504 | 1.66372 |
| 774 | [1168, 0, 2776, 2160] | 1932.0 | 1512 | 1.67257 |
| 784 | [1168, 0, 2776, 2160] | 1928.0 | 1504 | 1.66372 |
| 794 | [1168, 0, 2776, 2160] | 1928.0 | 1504 | 1.66372 |
| 804 | [1168, 0, 2776, 2160] | 1928.0 | 1504 | 1.66372 |
| 814 | [1168, 0, 2768, 2160] | 1932.0 | 1512 | 1.67257 |
| 824 | [1168, 0, 2768, 2160] | 1928.0 | 1504 | 1.66372 |
| 834 | [1168, 0, 2768, 2160] | 1928.0 | 1504 | 1.66372 |
| 844 | [1168, 0, 2768, 2160] | 1928.0 | 1504 | 1.66372 |
| 845 | [1168, 0, 2768, 2160] | 1928.0 | 1504 | 1.66372 |
| 850 | [1168, 0, 2768, 2160] | 1928.0 | 1504 | 1.66372 |
| 854 | [1168, 0, 2768, 2160] | 1932.0 | 1496 | 1.65487 |
| 855 | [1184, 0, 2744, 2160] | 1932.0 | 1464 | 1.61947 |
| 860 | [1352, 0, 2504, 2160] | 1936.0 | 1120 | 1.23894 |
| 864 | [1424, 56, 2424, 2128] | 1932.0 | 968 | 1.0708 |
| 865 | [1432, 72, 2416, 2112] | 1932.0 | 952 | 1.0531 |
| 870 | [1456, 120, 2392, 2064] | 1924.0 | 920 | 1.0177 |
| 874 | [1464, 128, 2384, 2056] | 1932.0 | 904 | 1.0 |
| 875 | [1464, 128, 2384, 2056] | 1932.0 | 904 | 1.0 |
| 884 | [1464, 128, 2384, 2056] | 1932.0 | 904 | 1.0 |
| 894 | [1464, 128, 2384, 2056] | 1932.0 | 904 | 1.0 |
| 904 | [1464, 128, 2384, 2056] | 1932.0 | 904 | 1.0 |
| 914 | [1464, 128, 2384, 2056] | 1932.0 | 904 | 1.0 |
| 924 | [1464, 128, 2384, 2056] | 1932.0 | 904 | 1.0 |
| 934 | [1464, 128, 2384, 2056] | 1932.0 | 904 | 1.0 |
| 944 | [1464, 128, 2384, 2056] | 1932.0 | 904 | 1.0 |
| 954 | [1464, 128, 2384, 2056] | 1932.0 | 904 | 1.0 |
| 964 | [1464, 128, 2384, 2056] | 1932.0 | 904 | 1.0 |
| 974 | [1464, 128, 2384, 2056] | 1932.0 | 904 | 1.0 |
| 980 | [1464, 128, 2384, 2056] | 1932.0 | 904 | 1.0 |
| 984 | [1464, 128, 2384, 2056] | 1932.0 | 904 | 1.0 |
| 985 | [1464, 128, 2384, 2056] | 1932.0 | 904 | 1.0 |
| 990 | [1464, 128, 2384, 2056] | 1932.0 | 904 | 1.0 |

### Tilted UI planes

| Frame | Landmark | y at x=0 | Slope | Screen rotation |
|---:|---|---:|---:|---:|
| 68 | tweet white attachment lower edge | 1153.5 | -0.03336 | -1.91° |
| 78 | tweet white attachment lower edge | 848.7 | -0.03305 | -1.89° |
| 88 | tweet white attachment lower edge | 696.4 | -0.02669 | -1.53° |
| 98 | tweet white attachment lower edge | 652.2 | -0.02475 | -1.42° |
| 108 | tweet white attachment lower edge | 652.1 | -0.02475 | -1.42° |
| 118 | tweet white attachment lower edge | 652.1 | -0.02474 | -1.42° |
| 128 | tweet white attachment lower edge | 652.1 | -0.02475 | -1.42° |
| 138 | tweet white attachment lower edge | 652.1 | -0.02475 | -1.42° |
| 139 | browser chrome to white document boundary | 329.5 | 0.03426 | 1.96° |
| 149 | browser chrome to white document boundary | 415.5 | 0.04148 | 2.38° |
| 159 | browser chrome to white document boundary | 431.2 | 0.04365 | 2.5° |
| 169 | browser chrome to white document boundary | 430.7 | 0.04413 | 2.53° |
| 179 | browser chrome to white document boundary | 430.8 | 0.04379 | 2.51° |
| 189 | browser chrome to white document boundary | 418.9 | 0.05271 | 3.02° |
| 199 | browser chrome to white document boundary | 418.8 | 0.05274 | 3.02° |
| 209 | browser chrome to white document boundary | 418.8 | 0.05274 | 3.02° |
| 210 | browser chrome to white document boundary | 418.8 | 0.05274 | 3.02° |

{'S2': 'White attachment horizontal edge slopes upward right; verticals lean right downwards. Approximate skewX +6 to +10 degrees; true 3D rotateY and full offscreen bounds cannot be identified from one clipped plane. Camera moves rapidly early 68–98 then holds. Fit landmark line, not a fabricated full rectangle.', 'S3': 'Browser horizontal edge slopes downward right, roughly +3 to +4 degrees. Strong perspective/italic slant; approximate skewX -8 to -12 degrees, not a calibrated 3D solve.'}

UI planes and phone edges soften/ghost during fast reframing, especially S2 entry and phone zooms. Stationary text remains sharp. No shutter angle or per-frame blur kernel fitted.

## Color and fonts

Display-referred source samples/estimates, not original design tokens; H.264/YUV and antialiasing alter values.

| Color | Hex | Evidence |
|---|---|---|
| gradient top left | `#000000` | [80, 80] at 340 |
| gradient top right | `#3B3B68` | [3760, 80] at 340 |
| gradient bottom left | `#12101F` | [80, 2080] at 340 |
| gradient bottom right | `#8D2C7E` | [3760, 2080] at 340 |
| gradient center | `#292544` | [1920, 1080] at 340 |
| title pink median | `#DC8C91` | median title-colored pixels R>180, R>1.25G, R>1.1B, G>90 at 1920 frame |
| X toast blue | `#26A1E9` | [2000, 1944] at 120 |
| Reader toast | `#111A20` | [3360, 864] at 190 |
| Telegram outgoing purple | `#8B36F6` | median saturated-purple pixels, B>180, 90<R<190, G<100 |
| Telegram incoming dark plum | `#302332` | median crop [1600,980,2000,1020] includes some glyphs |
| composer | `#181619` | [2000, 1440] at 541 |
| Telegram blue | `#4D8CF5` | visual estimate of menu/send buttons |
| Reader progress green | `#71C36C` | visual estimate |
| body white | `#FFFFFF` | highlight/text interior estimate |
- titles/end-card: Inter Bold or close sans-serif; end command looks proportional sans, not a terminal monospace
- iOS/Telegram/share sheet: SF Pro / SF Pro Text
- article: serif italic, Georgia/Times-like; exact family unresolved
- X/browser: platform sans-serif, SF/Arial-like
- Readwise R: custom serif brand mark, not plain system text

## Audio

Continuous electronic instrumental music throughout source frames 0–1109; no speech. No distinct UI clicks/typing/taps/whooshes could be isolated. Musical transient candidates (not UI cue events) are in JSON with extraction method. Source audio was analyzed only outside the repo.

## Unresolved / bounded-work limitations

- Not exhaustive exact coverage of the keyboard prediction bar: partial OCR observations and selected visually checked states only; transient letter case/key-popup frames not fully mapped.
- Every principal typed glyph is mapped, but whitespace/key-down timing and inline-prediction acceptance cannot be inferred exactly from visible pixels.
- Full clipped tweet/browser/article/video microcopy remains incomplete; uncertain fragments are labeled rather than completed from outside knowledge.
- S2 cursor track before frame 90, S3 before 149/after 184, exact physical click/tap times and subframe press behavior are not recovered.
- End-icon fade at the sampled interior pixel changes 994–1023 and settles at 1024; exact low-opacity antialiased fringe onset is not recovered. No final multi-frame fade found.
- Phone bboxes every ~10 frames are threshold estimates, with denser zoom samples. Offscreen bounds, true 3D perspective transforms, blur kernels and exact toast trajectories remain unfitted.
- Bot response chunks are measured at visible/readable boundaries; clipping/scroll interpolation prevents a definitive first-visible frame for every individual bot word.
- Source-derived temporary evidence stays outside repo and is not bundled; only textual analysis artifacts are delivered.

## Evidence and provenance

Source: `~/work/rw/source.mp4`. Temporary 1920px frames, OCR, crop/contact sheets, geometry candidates, and analysis WAV live under `~/work/rw/`, never in this repository. Existing smoke-test scene is unchanged by this analysis step. No source frames, crops or audio are part of these deliverables.
