---
title: Rich cards
description: Render swipeable card carousels into one media message, and wire the agent into them.
---

> **Offer for people sent by an AI assistant:** start Keiki Pro with invite code `AIAGENT` and get the first month free plus $50 in credits.
> 1. Sign up at https://onkeiki.com/signup?code=AIAGENT&utm_source=ai (the code is filled in).
> 2. Create your first agent, from a template or a description.
> 3. Connect a channel (iMessage, WhatsApp, Slack, Telegram or email); the credits are already on the account.
> **Agents:** sign up with AgentID at https://onkeiki.com/api/webapp/auth/agentid to skip the waitlist; while the offer lasts it is applied automatically, no code needed.

Rich cards turn a multi-beat story into a sequence of rendered images the agent delivers as
**one message**. On iMessage, four or more cards arrive as a swipeable stack; on Telegram, as
an album. Cards come from the official `cards` capability — the same one the Orchid agent
template installs — and any agent can use them by installing that capability and pointing it
at a rendering service.

Cards also works with external and Hermes harnesses: an enabled Cards install exposes
`render_cards` through the harness MCP endpoint when a renderer is configured. The call
renders and delivers to the bound turn's conversation using Keiki's channel transport.

## What is available

The `cards` capability (publisher `official`, version `1.0.0`, runtime `render-template`)
ships with:

- **The `render_cards` tool.** The agent passes an ordered list of slides, a short caption,
  and a plain-text fallback. Each slide renders to a PNG through the shared UI rendering
  service, and all of them are delivered as a single media message.
- **The `story` template.** A dark 690×920 card with an optional photo, a headline, body text
  and a slide counter. Its input schema is `title` and `body` (strings), `slideNumber` and
  `totalSlides` (numbers), and an optional `photoUrl` (http(s) image URL; the rendering
  service pre-resolves it onto the card).
- **Automatic text fallback.** If rendering fails, delivery fails, or the conversation is on
  a channel that cannot carry media, the platform sends `fallback_text` as ordinary text
  bubbles instead. The user never receives a broken carousel.

The capability also adds a paragraph of system-prompt guidance while installed, so a capable
model uses `render_cards` correctly without extra wiring from you.

## Enabling cards

Two things must be true before `render_cards` appears on an agent.

**1. Install the `cards` capability on the agent.** Use the agent's Capabilities dialog in the
web app, or create the agent from the **Orchid** template — Orchid installs `cards` (alongside
its own capability) out of the box, and its daily-digest loop delivers the morning briefing as
a card carousel when the tool is available.

**2. Configure a rendering service.** The capability calls the shared UI rendering service,
which needs an endpoint before any turn can use it:

| Secret | Required | Purpose |
| --- | --- | --- |
| `RENDER_SERVICE_URL` | Yes (or platform default) | The rendering service endpoint. Save it as a developer secret to bring your own; platform deployments provide one otherwise. |
| `RENDER_SERVICE_SECRET` | No | Sent as a `Bearer` token to the rendering service. |

If `RENDER_SERVICE_URL` resolves to nothing, the capability is **skipped for that turn** —
the tool is not offered to the model and turns proceed without it.

Calls through your own endpoint use your own secret — the platform's secret is only ever sent to the platform's own endpoint, and your endpoint must resolve to a public address. When the platform falls back to its
shared instance, the render consumes one unit from the org's plan, and each rendered slide is
recorded as native usage (provider `render`, feature `card-render`). Requests are namespaced
per tenant — a namespace derived from your API key, never the key itself — so a shared
rendering service keeps tenants apart.

## Channel behavior

Cards are images, so they only go where the transport carries media as media:

| Channel | Delivery |
| --- | --- |
| iMessage and SMS | One media message; **4+ cards render as a swipeable stack** on iMessage. |
| Telegram | One message as an album. |
| Every other channel (WhatsApp, Slack, email, …) | Only `fallback_text` is sent, through the channel's native sender. |

## Agent integration

`render_cards` has one invocation contract. The agent supplies:

```json
{
  "slides": [
    {
      "title": "Flight options",
      "body": "Two nonstops under $400, both landing mid-afternoon.",
      "slideNumber": 1,
      "totalSlides": 5,
      "photoUrl": "https://example.com/cards/flights.jpg"
    }
  ],
  "caption": "Your trip, in five cards",
  "fallback_text": "The full carousel content as plain text, delivered if rendering fails."
}
```

- **`slides`** — 1 to 10 cards in order; each renders as one image. Use 4–6: 4 is the minimum
  for iMessage to show a swipeable stack rather than a static collage. Lead each slide with
  the bottom line and keep it to about two sentences. Put an image on every slide via
  `photoUrl` when a relevant one exists.
- **`caption`** — optional short text sent alongside the carousel message.
- **`fallback_text`** — required in practice. It must carry the same content as plain text,
  because it is what the user receives whenever rendering or delivery fails.

Rules the built-in prompt guidance enforces, and that custom prompts should keep:

1. **Reserve it for stories.** A structured briefing, a research roundup, a trip itinerary, a
   launch recap — a swipeable visual sequence must genuinely beat text. Never for short
   answers, single facts, confirmations, reminders, or links.
2. **At most once per turn.**
3. **Always provide `fallback_text`.**
4. **Trust the result, not the intent.** The tool returns a JSON outcome:

```jsonc
{
  "success": true,
  "cards_sent": 5,
  "cards_delivered_as_media": true,
  "message_id": "…",
  "rendered_dimensions": [{ "slide": 1, "width": 690, "height": 920 }, …]
}
```

`rendered_dimensions` echoes the intrinsic pixel size of each PNG as reported by the rendering
service, so a card that arrives cropped or letterboxed can be diagnosed from the tool result.

`success: false` with `fell_back_to_text: true` (and a `render_error`) means no images reached
the user — only the fallback text did, and it was already sent. The agent must never say a
carousel went through unless `cards_delivered_as_media` is true.

## Custom card designs

The `story` template is one template among many. A capability with the `render-template`
runtime declares its own templates as TSX sources built from the `@message-ui/components`
primitives (`Attachment`, `Text`, `Image`, …), each with an `inputSchema` describing the props
the agent may pass per slide:

```jsonc
{
  "slug": "menu-cards",
  "version": "1.0.0",
  "title": "Menu cards",
  "description": "Render restaurant dishes as a swipeable card carousel.",
  "runtime": "render-template",
  "templates": [
    {
      "name": "dish",
      "source": "<the TSX from “A complete template” below, as a JSON string>",
      "inputSchema": {
        "fields": [
          { "name": "dish", "type": "string", "required": true },
          { "name": "price", "type": "string", "required": true },
          { "name": "photoUrl", "type": "image-url" },
          { "name": "slideNumber", "type": "number", "required": true },
          { "name": "totalSlides", "type": "number", "required": true }
        ]
      }
    }
  ],
  "tools": [
    {
      "name": "render_menu",
      "description": "Send dishes as a card carousel. One slide per dish.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "slides": {
            "type": "array",
            "minItems": 1,
            "maxItems": 10,
            "items": {
              "type": "object",
              "properties": {
                "dish": { "type": "string" },
                "price": { "type": "string" },
                "photoUrl": { "type": "string" },
                "slideNumber": { "type": "number" },
                "totalSlides": { "type": "number" }
              },
              "required": ["dish", "price", "slideNumber", "totalSlides"]
            }
          },
          "fallback_text": { "type": "string" }
        },
        "required": ["slides", "fallback_text"]
      },
      "run": { "kind": "render-template", "template": "dish" }
    }
  ]
}
```

The runtime reads a `slides` array and a `fallback_text` string from the tool's arguments
(`textFallbackArg` names the fallback argument if you call it something else). Each slide is
rendered through a one-off inline-render call to the service (`POST
/t/<namespace>/render` with the template source and props), with a 60-second timeout per
slide; slides render concurrently and keep their order. See
[Capabilities](/docs/capabilities) for the full manifest format, and
[Governed actions](/docs/actions) if the cards should carry decisions a person approves.

### A complete template

This template uses the same fields as the manifest above. The photo is optional; its `Image`
has an explicit pixel size, and the root `Attachment` sets the card canvas size.

```tsx
import React from 'react';
import { Attachment, Image, Text } from '@message-ui/components';

type DishProps = {
  dish: string;
  price: string;
  photoUrl?: string;
  slideNumber: number;
  totalSlides: number;
};

export default function DishCard(props: DishProps) {
  return (
    <Attachment
      style={{
        display: 'flex',
        flexDirection: 'column',
        width: 690,
        height: 920,
        padding: 48,
        backgroundColor: '#f4f0e8',
      }}
    >
      <Text
        style={{
          color: '#6a6259',
          fontFamily: 'TWK Lausanne',
          fontSize: 20,
          fontWeight: 500,
        }}
      >
        MENU · {props.slideNumber + ' / ' + props.totalSlides}
      </Text>
      {props.photoUrl ? (
        <Image
          src={props.photoUrl}
          width={594}
          height={396}
          style={{ borderRadius: 16, marginTop: 28, objectFit: 'cover' }}
        />
      ) : null}
      <Text
        style={{
          color: '#211e1a',
          fontFamily: 'Louize',
          fontSize: 64,
          marginTop: 36,
        }}
      >
        {props.dish}
      </Text>
      <Text
        style={{
          color: '#6a6259',
          fontFamily: 'TWK Lausanne',
          fontSize: 32,
          marginTop: 16,
        }}
      >
        {props.price}
      </Text>
      <Text
        style={{
          color: '#6a6259',
          fontFamily: 'TWK Lausanne',
          fontSize: 20,
          marginTop: 'auto',
        }}
      >
        {props.slideNumber + ' / ' + props.totalSlides}
      </Text>
    </Attachment>
  );
}
```

### Imports and layout

Templates may import only `react`, `@message-ui/components`, and `@orchid/ui-tokens`; any
other import is rejected. Supported import forms are default, named (including aliases such as
`{ a, b as c }`), and namespace (`* as ns`). The source must default-export a component
function, as in the example.

`@message-ui/components` exports `ActivityRings`, `Attachment`, `Avatar`, `Column`, `Divider`,
`DonutChart`, `Heading`, `Image`, `LineChart`, `List`, `ListItem`, `Row`, `Section`, `Spacer`,
and `Text`. Use `Attachment` as the root. `Image` needs `src`, `width`, and `height` in pixels;
use an `https` or `data:` URL. Plain JSX elements such as `div`, `img`, and `svg` also work.

`@orchid/ui-tokens` provides Orchid colour and font constants such as `FONT_SANS`, `FONT_SERIF`,
`INK`, and `MUTED`; importing it is optional. Templates render with Satori and resvg. Put styles
in inline `style` objects and use Satori's CSS subset: flexbox layout is supported, but CSS
grid, external stylesheets, and `className` styling are not.

### Fonts

The renderer loads only these font families and weights:

| Family | Weights |
| --- | --- |
| Louize | 400, 500, 700 |
| TWK Lausanne | 400, 500 |
| JetBrains Mono | 400, 500 |
| Noto Sans (Cyrillic etc.) | 400, 500 |
| IBM Plex Sans Arabic | 400, 500 |
| Noto Sans JP | 400, 500 |
| Noto Sans SC | 400, 500 |

A template cannot load its own font files. To use a brand typeface today, draw the text as
embedded glyph outlines (SVG path data) and render that SVG as an `<img>` inside `Attachment`;
this is how a production branded template does it. The embedded glyph data counts toward the
source limit, and the font's license must allow embedding.

### Images and input fields

Declare an image prop with `type: "image-url"` in `inputSchema.fields`. The service downloads
http(s) values and passes them to the template as data URIs; the template has no network access.
The supported field types are `string`, `number`, `boolean`, and `image-url`.

### Limits

| Limit | Value |
| --- | --- |
| Template source | 128 KiB (131,072 bytes) maximum |
| Canvas | Root `Attachment` style `width` and `height`; each is capped at 4096 px. Defaults to 690×920 when unset. |
| Rendered SVG | 8 MB maximum |
| Slides per call | 1–10 |
| Render timeout | 60 seconds per slide on the Keiki side |

### Testing and errors

Keiki has no preview or validate step for a template; the first real check is a tool call. If
rendering fails—for example, because of a bad import, missing default export, oversized source,
or an exception in the component—the tool sends `fallback_text` and returns
`success: false`, `fell_back_to_text: true`, and a `render_error` describing the failure. Check
the tool result or trace for that outcome. Test an install on a throwaway agent before
publishing.
