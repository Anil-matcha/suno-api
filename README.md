# Suno API: Python SDK for Music and Audio Generation

[![Powered by MuAPI](https://img.shields.io/badge/Powered%20by-MuAPI-6366f1?style=flat-square)](https://muapi.ai/suno?utm_source=github&utm_medium=badge&utm_campaign=suno-api)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A focused Python SDK for **Suno music and audio workflows** through [MuAPI](https://muapi.ai/suno?utm_source=github&utm_medium=readme&utm_campaign=suno-api). Create songs, remix or extend tracks, generate lyrics and sound effects, add vocals or instrumentals, make mashups, convert tracks to WAV, and run Suno's two-stage custom voice flow with one API key.

## Related Projects

- [Suno on MuAPI](https://muapi.ai/suno?utm_source=github&utm_medium=readme&utm_campaign=suno-api) — model landing page for Suno's music and audio capabilities.
- [Suno create music playground](https://muapi.ai/playground/suno-create-music?utm_source=github&utm_medium=readme&utm_campaign=suno-api) — try the primary workflow in the browser.
- [MuAPI music and speech docs](https://muapi.ai/docs/music-and-speech?utm_source=github&utm_medium=readme&utm_campaign=suno-api) — audio endpoint and workflow reference.
- [suno-comfyui](https://github.com/Anil-matcha/suno-comfyui) — focused ComfyUI nodes for Suno create, remix, extend, and utility workflows.
- [minimax-music-3-api](https://github.com/SamurAIGPT/minimax-music-3-api) — sibling Python SDK for MiniMax Music 3.0 text-to-music generation.
- [awesome-minimax-music-3-prompts](https://github.com/Anil-matcha/awesome-minimax-music-3-prompts) — curated music prompts and a practical lyrics-formatting guide.
- [minimax-music-3-comfyui](https://github.com/Anil-matcha/minimax-music-3-comfyui) — ComfyUI nodes for a related text-to-music model.
- [midjourney-api](https://github.com/Anil-matcha/midjourney-api) — sibling Python SDK for Midjourney image-generation workflows.
- [Open-Generative-AI](https://github.com/Anil-matcha/Open-Generative-AI) — open-source studio for running generative image, video, and audio workflows.
- [Generative-Media-Skills](https://github.com/SamurAIGPT/Generative-Media-Skills) — agent-ready skills for building generative-media pipelines.
- [muapi-cli](https://github.com/SamurAIGPT/muapi-cli) — CLI and MCP access to the same MuAPI model catalog.

## Features

- Create music with Suno V3.5 through V5.5 model options
- Remix and extend existing audio URLs
- Generate lyrics, sound effects, and expanded music-style descriptions
- Add vocals, add instrumentals, or create mashups from multiple tracks
- Convert a completed track to lossless WAV
- Two-stage custom voice cloning with phrase verification
- Async polling, webhook URLs, output URL extraction, and injectable HTTP sessions

## Installation

```bash
pip install suno-api
```

Or install the latest source:

```bash
git clone https://github.com/Anil-matcha/suno-api.git
cd suno-api
pip install -e .
```

Set your MuAPI key:

```bash
export MUAPI_API_KEY=your_muapi_api_key
```

Create a key from the [MuAPI access-key page](https://muapi.ai/access-keys?utm_source=github&utm_medium=readme&utm_campaign=suno-api).

## Quick start

```python
from suno_api import SunoAPI

api = SunoAPI()

task = api.create_music(
    style="Hip-Hop",
    prompt="A confident song about winning with a memorable hook",
    instrumental=False,
    model="V5",
)

result = api.wait_for_completion(task["request_id"])
for audio_url in api.extract_audio_urls(result):
    print(audio_url)
```

For a blocking helper, use `api.create_music_and_wait(style="Hip-Hop", prompt="...", instrumental=False)`.

## Core workflows

### Remix and extend

```python
remix = api.remix_music(
    audio_url="https://example.com/source.mp3",
    style="warm lo-fi jazz with brushed drums",
    prompt="Keep the melody recognizable but make the mix intimate",
)

extension = api.extend_music(
    audio_url="https://example.com/source.mp3",
    style="cinematic electronic pop",
    continue_at=42,
)
```

### Lyrics, sound effects, and style expansion

```python
lyrics = api.generate_lyrics("A hopeful song about rebuilding after a storm")
sound = api.generate_sounds("Distant thunder rolling across a mountain valley")
expanded_style = api.boost_music_style("dark electronic pop")
```

### Vocals, instrumentals, and mashups

```python
vocals = api.add_vocals(
    prompt="A confident lead vocal with a wide chorus",
    title="After the Rain",
    style="cinematic pop, uplifting, modern drums",
    audio_url="https://example.com/instrumental.mp3",
)

instrumental = api.add_instrumental(
    title="After the Rain Backing Track",
    tags="cinematic pop, modern drums, warm piano",
)

mashup = api.generate_mashup(
    ["https://example.com/intro.mp3", "https://example.com/chorus.mp3"],
    style="indie electronic",
    instrumental=True,
)
```

## Custom voice cloning

Voice cloning uses a required two-stage verification flow. The first request returns a fresh phrase; record yourself reading that phrase, upload the recording, then confirm it:

```python
stage_one = api.voice_clone(
    "https://example.com/clean-voice-sample.wav",
    voice_name="My Singing Voice",
    language="en",
)

# Poll until the result contains stage="awaiting_phrase" and a phrase.
phrase_state = api.get_result(stage_one["request_id"])
print(phrase_state["phrase"])

stage_two = api.confirm_voice_clone(
    stage_one["request_id"],
    "https://example.com/verification-phrase.wav",
)
completed = api.wait_for_completion(stage_two["request_id"])
print(completed.get("voice_id"))
```

The voice library helpers are `list_voices()`, `check_voice(voice_db_id)`, `refresh_voice(voice_db_id)`, and `delete_voice(voice_db_id)`. Only clone voices you have permission to use.

## API endpoints

| Workflow | Endpoint |
| --- | --- |
| Create music | `POST /api/v1/suno-create-music` |
| Remix music | `POST /api/v1/suno-remix-music` |
| Extend music | `POST /api/v1/suno-extend-music` |
| Convert to WAV | `POST /api/v1/suno-convert-to-wav` |
| Generate sounds | `POST /api/v1/suno-generate-sounds` |
| Generate lyrics | `POST /api/v1/suno-generate-lyrics` |
| Boost music style | `POST /api/v1/suno-boost-music-style` |
| Add vocals | `POST /api/v1/suno-add-vocals` |
| Generate mashup | `POST /api/v1/suno-generate-mashup` |
| Add instrumental | `POST /api/v1/suno-add-instrumental` |
| Start voice clone | `POST /api/v1/suno-voice-clone` |
| Confirm voice clone | `POST /api/v1/suno-voice-clone/{request_id}/confirm` |
| Poll task | `GET /api/v1/predictions/{request_id}/result` |

All requests use the `x-api-key` header. Inputs that reference audio must be publicly reachable URLs. Every generation returns a `request_id` immediately; use polling or provide `webhook_url`.

### Raw request shape

```bash
curl --location --request POST "https://api.muapi.ai/api/v1/suno-create-music" \
  --header "x-api-key: $MUAPI_API_KEY" \
  --header "Content-Type: application/json" \
  --data-raw '{
    "style": "Hip-Hop",
    "prompt": "A confident song about winning with a memorable hook",
    "model": "V5",
    "instrumental": false,
    "webhook_url": "https://example.com/webhook"
  }'
```

For a completed result, `extract_audio_urls(result)` returns the hosted output URLs. `extract_audio_ids(result)` returns the track IDs needed by `convert_to_wav()`.

## Development

```bash
python -m unittest discover -s tests -v
```

The tests mock HTTP calls and never spend credits.

## License

MIT — see [LICENSE](LICENSE).
