# Scene format (`04_script.json`)

Owner: Julia. Draft: Julia makes it final by Tue Oct 13 and adds `docs/example-script.json`.

The script agent writes one JSON file. Voiceover, the scene builder and assembly all read it.

```json
{
  "topic": "How electric vehicle batteries work",
  "total_words": 1020,
  "scenes": [
    {
      "id": 1,
      "title": "Why batteries matter",
      "narration": "Every electric car on the road depends on one part more than any other...",
      "duration_sec": 35,
      "visual_type": "title",
      "visual_content": { "heading": "Why batteries matter", "subheading": "The heart of every EV" },
      "sources": ["https://example.com/source-page"]
    }
  ]
}
```

| Field | Type | Meaning |
|---|---|---|
| `id` | number | Scene order, starting at 1 |
| `title` | text | Short scene name |
| `narration` | text | Exactly what the voiceover says |
| `duration_sec` | number | Target length; the real voiceover length overrides it |
| `visual_type` | one of `title`, `bullets`, `chart`, `quote`, `image` | Which template the scene uses |
| `visual_content` | object | What appears on screen; its fields depend on `visual_type` (to be defined by Julia) |
| `sources` | list of URLs | Where the scene's facts come from (from `03_checked.md`) |
