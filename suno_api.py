"""Python client for Suno music and audio workflows on MuAPI."""

import os
import time
from typing import Any, Dict, Iterable, List, Optional

import requests


DEFAULT_BASE_URL = "https://api.muapi.ai/api/v1"
MUSIC_MODELS = frozenset({"V3_5", "V4", "V4_5", "V4_5PLUS", "V4_5ALL", "V5", "V5_5"})
EXTRA_MODELS = frozenset({"V4", "V4_5", "V4_5PLUS", "V4_5ALL", "V5", "V5_5"})
ADD_ON_MODELS = frozenset({"V4", "V4_5", "V4_5PLUS", "V5"})
VOICE_LANGUAGES = frozenset({"en", "zh", "es", "fr", "pt", "de", "ja", "ko", "hi", "ru"})
SOUND_KEYS = frozenset(
    {
        "Any",
        "Cm",
        "C#m",
        "Dm",
        "D#m",
        "Em",
        "Fm",
        "F#m",
        "Gm",
        "G#m",
        "Am",
        "A#m",
        "Bm",
        "C",
        "C#",
        "D",
        "D#",
        "E",
        "F",
        "F#",
        "G",
        "G#",
        "A",
        "A#",
        "B",
    }
)
TERMINAL_SUCCESS_STATUSES = frozenset({"completed", "success", "succeeded", "done"})
TERMINAL_FAILURE_STATUSES = frozenset({"failed", "error", "cancelled", "canceled"})


class SunoAPI:
    """Submit Suno music jobs and retrieve their asynchronous results."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        session: Optional[requests.Session] = None,
    ):
        self.api_key = api_key or os.getenv("MUAPI_API_KEY")
        if not self.api_key:
            raise ValueError("An API key is required. Set MUAPI_API_KEY or pass api_key.")

        configured_base_url = base_url or os.getenv("SUNO_API_BASE_URL") or DEFAULT_BASE_URL
        self.base_url = configured_base_url.rstrip("/")
        self.headers = {"x-api-key": self.api_key, "Content-Type": "application/json"}
        self.session = session or requests.Session()

    def create_music(
        self,
        style: str,
        *,
        prompt: Optional[str] = None,
        model: str = "V5",
        custom_mode: bool = True,
        title: Optional[str] = None,
        persona_id: Optional[str] = None,
        persona_model: Optional[str] = None,
        instrumental: bool = True,
        negative_tags: Optional[str] = None,
        vocal_gender: Optional[str] = None,
        style_weight: Optional[float] = None,
        weirdness_constraint: Optional[float] = None,
        audio_weight: Optional[float] = None,
        webhook_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate original music from a style description and optional lyrics/prompt."""
        self._validate_music(
            style,
            prompt=prompt,
            model=model,
            title=title,
            persona_model=persona_model,
            vocal_gender=vocal_gender,
            instrumental=instrumental,
            style_weight=style_weight,
            weirdness_constraint=weirdness_constraint,
            audio_weight=audio_weight,
        )
        return self._post(
            "suno-create-music",
            self._music_payload(
                style=style,
                prompt=prompt,
                model=model,
                custom_mode=custom_mode,
                title=title,
                persona_id=persona_id,
                persona_model=persona_model,
                instrumental=instrumental,
                negative_tags=negative_tags,
                vocal_gender=vocal_gender,
                style_weight=style_weight,
                weirdness_constraint=weirdness_constraint,
                audio_weight=audio_weight,
                webhook_url=webhook_url,
            ),
        )

    def remix_music(
        self,
        audio_url: str,
        style: str,
        *,
        prompt: Optional[str] = None,
        model: str = "V5",
        custom_mode: bool = True,
        title: Optional[str] = None,
        persona_id: Optional[str] = None,
        persona_model: Optional[str] = None,
        instrumental: bool = True,
        negative_tags: Optional[str] = None,
        vocal_gender: Optional[str] = None,
        style_weight: Optional[float] = None,
        weirdness_constraint: Optional[float] = None,
        audio_weight: Optional[float] = None,
        webhook_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new version of an existing track in a different style."""
        self._validate_music(
            style,
            prompt=prompt,
            model=model,
            title=title,
            persona_model=persona_model,
            vocal_gender=vocal_gender,
            instrumental=instrumental,
            style_weight=style_weight,
            weirdness_constraint=weirdness_constraint,
            audio_weight=audio_weight,
        )
        self._require_text(audio_url, "audio_url")
        payload = self._music_payload(
            style=style,
            prompt=prompt,
            model=model,
            custom_mode=custom_mode,
            title=title,
            persona_id=persona_id,
            persona_model=persona_model,
            instrumental=instrumental,
            negative_tags=negative_tags,
            vocal_gender=vocal_gender,
            style_weight=style_weight,
            weirdness_constraint=weirdness_constraint,
            audio_weight=audio_weight,
            webhook_url=webhook_url,
        )
        payload["audio_url"] = audio_url
        return self._post("suno-remix-music", payload)

    def extend_music(
        self,
        audio_url: str,
        style: str,
        *,
        prompt: Optional[str] = None,
        model: str = "V5",
        custom_mode: bool = True,
        title: Optional[str] = None,
        persona_id: Optional[str] = None,
        persona_model: Optional[str] = None,
        instrumental: bool = True,
        continue_at: int = 1,
        negative_tags: Optional[str] = None,
        vocal_gender: Optional[str] = None,
        style_weight: Optional[float] = None,
        weirdness_constraint: Optional[float] = None,
        audio_weight: Optional[float] = None,
        webhook_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Continue an existing track from a selected point in seconds."""
        self._validate_music(
            style,
            prompt=prompt,
            model=model,
            title=title,
            persona_model=persona_model,
            vocal_gender=vocal_gender,
            instrumental=instrumental,
            style_weight=style_weight,
            weirdness_constraint=weirdness_constraint,
            audio_weight=audio_weight,
        )
        self._require_text(audio_url, "audio_url")
        if not isinstance(continue_at, int) or continue_at < 0:
            raise ValueError("continue_at must be a non-negative integer.")
        payload = self._music_payload(
            style=style,
            prompt=prompt,
            model=model,
            custom_mode=custom_mode,
            title=title,
            persona_id=persona_id,
            persona_model=persona_model,
            instrumental=instrumental,
            negative_tags=negative_tags,
            vocal_gender=vocal_gender,
            style_weight=style_weight,
            weirdness_constraint=weirdness_constraint,
            audio_weight=audio_weight,
            webhook_url=webhook_url,
        )
        payload.update({"audio_url": audio_url, "continue_at": continue_at})
        return self._post("suno-extend-music", payload)

    def convert_to_wav(
        self,
        task_id: str,
        audio_id: str,
        *,
        webhook_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Convert one completed Suno track to lossless WAV."""
        self._require_text(task_id, "task_id")
        self._require_text(audio_id, "audio_id")
        return self._post(
            "suno-convert-to-wav",
            self._without_none({"task_id": task_id, "audio_id": audio_id, "webhook_url": webhook_url}),
        )

    def generate_sounds(
        self,
        prompt: str,
        *,
        model: str = "V5",
        sound_loop: bool = False,
        sound_tempo: Optional[int] = None,
        sound_key: str = "Any",
        grab_lyrics: bool = False,
        webhook_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a sound effect, loop, or short musical soundscape."""
        self._require_text(prompt, "prompt")
        self._validate_model(model, EXTRA_MODELS, "model")
        if sound_key not in SOUND_KEYS:
            raise ValueError(f"Unsupported sound_key {sound_key!r}.")
        return self._post(
            "suno-generate-sounds",
            self._without_none(
                {
                    "prompt": prompt,
                    "model": model,
                    "sound_loop": sound_loop,
                    "sound_tempo": sound_tempo,
                    "sound_key": sound_key,
                    "grab_lyrics": grab_lyrics,
                    "webhook_url": webhook_url,
                }
            ),
        )

    def generate_lyrics(self, prompt: str, *, webhook_url: Optional[str] = None) -> Dict[str, Any]:
        """Generate lyrics from a topic, concept, or song brief."""
        self._require_text(prompt, "prompt")
        return self._post("suno-generate-lyrics", self._without_none({"prompt": prompt, "webhook_url": webhook_url}))

    def boost_music_style(self, content: str, *, webhook_url: Optional[str] = None) -> Dict[str, Any]:
        """Expand a short style description into a richer music brief."""
        self._require_text(content, "content")
        return self._post("suno-boost-music-style", self._without_none({"content": content, "webhook_url": webhook_url}))

    def add_vocals(
        self,
        prompt: str,
        title: str,
        style: str,
        *,
        negative_tags: Optional[str] = None,
        audio_url: Optional[str] = None,
        model: str = "V5",
        vocal_gender: Optional[str] = "male",
        style_weight: Optional[float] = 0.65,
        weirdness_constraint: Optional[float] = 0.65,
        audio_weight: Optional[float] = 0.65,
        webhook_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add generated vocals to an instrumental or supplied audio track."""
        self._validate_add_on(title, style, model, vocal_gender, style_weight, weirdness_constraint, audio_weight)
        self._require_text(prompt, "prompt")
        payload = self._without_none(
            {
                "prompt": prompt,
                "title": title,
                "style": style,
                "negative_tags": negative_tags,
                "audio_url": audio_url,
                "model": model,
                "vocal_gender": vocal_gender,
                "style_weight": style_weight,
                "weirdness_constraint": weirdness_constraint,
                "audio_weight": audio_weight,
                "webhook_url": webhook_url,
            }
        )
        return self._post("suno-add-vocals", payload)

    def generate_mashup(
        self,
        audios_list: Iterable[str],
        *,
        prompt: Optional[str] = None,
        style: Optional[str] = None,
        title: Optional[str] = None,
        instrumental: bool = True,
        model: str = "V5",
        vocal_gender: Optional[str] = "male",
        style_weight: Optional[float] = 0.65,
        weirdness_constraint: Optional[float] = 0.65,
        audio_weight: Optional[float] = 0.65,
        webhook_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Blend a list of audio URLs into a new Suno track."""
        if isinstance(audios_list, (str, bytes)):
            raise ValueError("audios_list must be an iterable of audio URLs.")
        audio_urls = list(audios_list)
        if not audio_urls or any(not isinstance(url, str) or not url.strip() for url in audio_urls):
            raise ValueError("audios_list must contain at least one non-empty audio URL.")
        if title is not None and len(title) > 80:
            raise ValueError("title must be 80 characters or fewer.")
        self._validate_model(model, EXTRA_MODELS, "model")
        self._validate_gender(vocal_gender)
        self._validate_weights(style_weight, weirdness_constraint, audio_weight)
        return self._post(
            "suno-generate-mashup",
            self._without_none(
                {
                    "audios_list": audio_urls,
                    "prompt": prompt,
                    "style": style,
                    "title": title,
                    "instrumental": instrumental,
                    "model": model,
                    "vocal_gender": vocal_gender,
                    "style_weight": style_weight,
                    "weirdness_constraint": weirdness_constraint,
                    "audio_weight": audio_weight,
                    "webhook_url": webhook_url,
                }
            ),
        )

    def add_instrumental(
        self,
        title: str,
        tags: str,
        *,
        audio_url: Optional[str] = None,
        negative_tags: Optional[str] = None,
        model: str = "V5",
        vocal_gender: Optional[str] = "male",
        style_weight: Optional[float] = 0.65,
        weirdness_constraint: Optional[float] = 0.65,
        audio_weight: Optional[float] = 0.65,
        webhook_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add an instrumental arrangement to a song or vocal track."""
        self._validate_add_on(title, tags, model, vocal_gender, style_weight, weirdness_constraint, audio_weight)
        return self._post(
            "suno-add-instrumental",
            self._without_none(
                {
                    "audio_url": audio_url,
                    "title": title,
                    "tags": tags,
                    "negative_tags": negative_tags,
                    "model": model,
                    "vocal_gender": vocal_gender,
                    "style_weight": style_weight,
                    "weirdness_constraint": weirdness_constraint,
                    "audio_weight": audio_weight,
                    "webhook_url": webhook_url,
                }
            ),
        )

    def voice_clone(
        self,
        audio_url: str,
        *,
        voice_name: Optional[str] = None,
        description: Optional[str] = None,
        style: Optional[str] = None,
        language: str = "en",
        vocal_start_s: int = 0,
        vocal_end_s: int = 10,
        webhook_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Start stage one of Suno's two-stage custom voice-clone flow."""
        self._require_text(audio_url, "audio_url")
        if language not in VOICE_LANGUAGES:
            raise ValueError(f"Unsupported language {language!r}.")
        if vocal_start_s < 0 or vocal_end_s <= vocal_start_s:
            raise ValueError("vocal_end_s must be greater than vocal_start_s.")
        return self._post(
            "suno-voice-clone",
            self._without_none(
                {
                    "audio_url": audio_url,
                    "voice_name": voice_name,
                    "description": description,
                    "style": style,
                    "language": language,
                    "vocal_start_s": vocal_start_s,
                    "vocal_end_s": vocal_end_s,
                    "webhook_url": webhook_url,
                }
            ),
        )

    def confirm_voice_clone(
        self,
        request_id: str,
        audio_url: str,
        *,
        webhook_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Submit the recording of the verification phrase for stage two."""
        self._require_text(request_id, "request_id")
        self._require_text(audio_url, "audio_url")
        return self._post(
            f"suno-voice-clone/{request_id}/confirm",
            self._without_none({"audio_url": audio_url, "webhook_url": webhook_url}),
        )

    def list_voices(self) -> Dict[str, Any]:
        """List the caller's saved custom voices."""
        return self._get("suno-voices")

    def delete_voice(self, voice_db_id: str) -> Dict[str, Any]:
        """Delete a saved custom voice."""
        self._require_text(voice_db_id, "voice_db_id")
        return self._delete(f"suno-voices/{voice_db_id}")

    def check_voice(self, voice_db_id: str) -> Dict[str, Any]:
        """Check whether a saved custom voice is available."""
        self._require_text(voice_db_id, "voice_db_id")
        return self._post(f"suno-voices/{voice_db_id}/check", {})

    def refresh_voice(self, voice_db_id: str) -> Dict[str, Any]:
        """Start a fresh verification cycle for an expired custom voice."""
        self._require_text(voice_db_id, "voice_db_id")
        return self._post(f"suno-voices/{voice_db_id}/refresh", {})

    def get_result(self, request_id: str) -> Dict[str, Any]:
        """Retrieve the current status and output for a submitted job."""
        self._require_text(request_id, "request_id")
        response = self.session.get(
            f"{self.base_url}/predictions/{request_id}/result",
            headers=self.headers,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def wait_for_completion(
        self,
        request_id: str,
        poll_interval: float = 5,
        timeout: float = 900,
    ) -> Dict[str, Any]:
        """Poll until a job completes, fails, or reaches the timeout."""
        if poll_interval < 0:
            raise ValueError("poll_interval must be zero or greater.")
        if timeout <= 0:
            raise ValueError("timeout must be greater than zero.")

        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            result = self.get_result(request_id)
            status = str(result.get("status", "")).lower()
            if status in TERMINAL_SUCCESS_STATUSES:
                return result
            if status in TERMINAL_FAILURE_STATUSES:
                detail = result.get("error") or result.get("message") or result
                raise RuntimeError(f"Suno generation {status}: {detail}")

            remaining = deadline - time.monotonic()
            if remaining > 0:
                time.sleep(min(poll_interval, remaining))

        raise TimeoutError(f"Timed out waiting for Suno job {request_id}.")

    def create_music_and_wait(
        self,
        style: str,
        *,
        poll_interval: float = 5,
        timeout: float = 900,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Create music and block until the completed result is available."""
        submission = self.create_music(style, **kwargs)
        request_id = submission.get("request_id")
        if not request_id:
            raise RuntimeError(f"No request_id in submission response: {submission}")
        return self.wait_for_completion(request_id, poll_interval=poll_interval, timeout=timeout)

    def generate_and_wait(self, style: str, **kwargs: Any) -> Dict[str, Any]:
        """Compatibility alias for :meth:`create_music_and_wait`."""
        return self.create_music_and_wait(style, **kwargs)

    @staticmethod
    def extract_audio_urls(result: Dict[str, Any]) -> List[str]:
        """Extract hosted audio URLs from a completed Suno result."""
        outputs = result.get("outputs")
        if isinstance(outputs, list):
            return [str(item) for item in outputs if item]
        if isinstance(outputs, str) and outputs:
            return [outputs]

        output = result.get("output")
        if isinstance(output, dict):
            audio = output.get("audio") or output.get("audio_url") or output.get("outputs")
            if isinstance(audio, list):
                return [str(item) for item in audio if item]
            if isinstance(audio, str) and audio:
                return [audio]
        if isinstance(output, list):
            return [str(item) for item in output if item]
        if isinstance(output, str) and output:
            return [output]
        audio = result.get("audio")
        if isinstance(audio, str) and audio:
            return [audio]
        return []

    @staticmethod
    def extract_audio_ids(result: Dict[str, Any]) -> List[str]:
        """Extract provider track IDs used by :meth:`convert_to_wav`."""
        audio_ids = result.get("audio_ids")
        if isinstance(audio_ids, list):
            return [str(item) for item in audio_ids if item]
        return []

    def _post(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        response = self.session.post(
            f"{self.base_url}/{endpoint}",
            json=payload,
            headers=self.headers,
            timeout=120,
        )
        response.raise_for_status()
        return response.json()

    def _get(self, endpoint: str) -> Dict[str, Any]:
        response = self.session.get(f"{self.base_url}/{endpoint}", headers=self.headers, timeout=30)
        response.raise_for_status()
        return response.json()

    def _delete(self, endpoint: str) -> Dict[str, Any]:
        response = self.session.delete(f"{self.base_url}/{endpoint}", headers=self.headers, timeout=30)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _music_payload(
        *,
        style: str,
        prompt: Optional[str],
        model: str,
        custom_mode: bool,
        title: Optional[str],
        persona_id: Optional[str],
        persona_model: Optional[str],
        instrumental: bool,
        negative_tags: Optional[str],
        vocal_gender: Optional[str],
        style_weight: Optional[float],
        weirdness_constraint: Optional[float],
        audio_weight: Optional[float],
        webhook_url: Optional[str],
    ) -> Dict[str, Any]:
        return SunoAPI._without_none(
            {
                "prompt": prompt,
                "style": style,
                "model": model,
                "custom_mode": custom_mode,
                "title": title,
                "persona_id": persona_id,
                "persona_model": persona_model,
                "instrumental": instrumental,
                "negative_tags": negative_tags,
                "vocal_gender": vocal_gender,
                "style_weight": style_weight,
                "weirdness_constraint": weirdness_constraint,
                "audio_weight": audio_weight,
                "webhook_url": webhook_url,
            }
        )

    @staticmethod
    def _validate_music(
        style: str,
        *,
        prompt: Optional[str],
        model: str,
        title: Optional[str],
        persona_model: Optional[str],
        vocal_gender: Optional[str],
        instrumental: bool,
        style_weight: Optional[float],
        weirdness_constraint: Optional[float],
        audio_weight: Optional[float],
    ) -> None:
        SunoAPI._require_text(style, "style")
        SunoAPI._validate_model(model, MUSIC_MODELS, "model")
        if not instrumental:
            SunoAPI._require_text(prompt, "prompt when instrumental is false")
        if title is not None and len(title) > 80:
            raise ValueError("title must be 80 characters or fewer.")
        if persona_model not in (None, "style_persona", "voice_persona"):
            raise ValueError("persona_model must be style_persona or voice_persona.")
        if persona_model == "voice_persona" and model not in ("V5", "V5_5"):
            raise ValueError("persona_model='voice_persona' requires model V5 or V5_5.")
        SunoAPI._validate_gender(vocal_gender)
        SunoAPI._validate_weights(style_weight, weirdness_constraint, audio_weight)

    @staticmethod
    def _validate_add_on(
        title: str,
        tags: str,
        model: str,
        vocal_gender: Optional[str],
        style_weight: Optional[float],
        weirdness_constraint: Optional[float],
        audio_weight: Optional[float],
    ) -> None:
        SunoAPI._require_text(title, "title")
        SunoAPI._require_text(tags, "style" if tags == "" else "tags")
        SunoAPI._validate_model(model, ADD_ON_MODELS, "model")
        SunoAPI._validate_gender(vocal_gender)
        SunoAPI._validate_weights(style_weight, weirdness_constraint, audio_weight)
        if len(title) > 80:
            raise ValueError("title must be 80 characters or fewer.")

    @staticmethod
    def _validate_model(model: str, supported: Iterable[str], field_name: str) -> None:
        if model not in supported:
            options = ", ".join(sorted(supported))
            raise ValueError(f"Unsupported {field_name} {model!r}. Choose one of: {options}.")

    @staticmethod
    def _validate_gender(vocal_gender: Optional[str]) -> None:
        if vocal_gender is not None and vocal_gender not in ("male", "female"):
            raise ValueError("vocal_gender must be male or female.")

    @staticmethod
    def _validate_weights(*weights: Optional[float]) -> None:
        for weight in weights:
            if weight is not None and not 0 <= weight <= 1:
                raise ValueError("style_weight, weirdness_constraint, and audio_weight must be between 0 and 1.")

    @staticmethod
    def _require_text(value: Optional[str], field_name: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} must be a non-empty string.")

    @staticmethod
    def _without_none(payload: Dict[str, Any]) -> Dict[str, Any]:
        return {key: value for key, value in payload.items() if value is not None}
