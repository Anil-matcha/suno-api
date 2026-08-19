import unittest
from unittest.mock import Mock

from suno_api import SunoAPI


def response_with(payload):
    response = Mock()
    response.json.return_value = payload
    return response


class SunoAPITest(unittest.TestCase):
    def test_create_music_posts_current_contract(self):
        session = Mock()
        session.post.return_value = response_with({"request_id": "req_music", "status": "processing"})
        api = SunoAPI(api_key="test-key", session=session)

        result = api.create_music(
            style="Hip-Hop",
            prompt="A confident song about winning",
            model="V5",
            instrumental=False,
            title="Winning",
            vocal_gender="male",
            webhook_url="https://example.com/webhook",
        )

        self.assertEqual(result["request_id"], "req_music")
        self.assertEqual(
            session.post.call_args.kwargs["json"],
            {
                "prompt": "A confident song about winning",
                "style": "Hip-Hop",
                "model": "V5",
                "custom_mode": True,
                "title": "Winning",
                "instrumental": False,
                "vocal_gender": "male",
                "webhook_url": "https://example.com/webhook",
            },
        )
        self.assertEqual(session.post.call_args.args[0], "https://api.muapi.ai/api/v1/suno-create-music")

    def test_remix_and_extend_include_audio_inputs(self):
        session = Mock()
        session.post.return_value = response_with({"request_id": "req", "status": "processing"})
        api = SunoAPI(api_key="test-key", session=session)

        api.remix_music("https://example.com/song.mp3", "Lo-fi jazz", prompt="Make it warmer")
        remix_payload = session.post.call_args.kwargs["json"]
        self.assertEqual(remix_payload["audio_url"], "https://example.com/song.mp3")
        self.assertEqual(session.post.call_args.args[0], "https://api.muapi.ai/api/v1/suno-remix-music")

        api.extend_music("https://example.com/song.mp3", "Cinematic pop", continue_at=42)
        extend_payload = session.post.call_args.kwargs["json"]
        self.assertEqual(extend_payload["continue_at"], 42)
        self.assertEqual(session.post.call_args.args[0], "https://api.muapi.ai/api/v1/suno-extend-music")

    def test_utility_endpoints_use_their_current_paths(self):
        session = Mock()
        session.post.return_value = response_with({"request_id": "req", "status": "processing"})
        api = SunoAPI(api_key="test-key", session=session)

        api.generate_sounds("A distant thunderclap", sound_loop=True)
        self.assertIn("suno-generate-sounds", session.post.call_args.args[0])
        api.generate_lyrics("A song about a long train ride")
        self.assertIn("suno-generate-lyrics", session.post.call_args.args[0])
        api.boost_music_style("dark electronic pop")
        self.assertIn("suno-boost-music-style", session.post.call_args.args[0])
        api.generate_mashup(["https://example.com/a.mp3", "https://example.com/b.mp3"])
        self.assertIn("suno-generate-mashup", session.post.call_args.args[0])
        api.add_instrumental("Backing Track", "ambient piano")
        self.assertIn("suno-add-instrumental", session.post.call_args.args[0])

    def test_voice_clone_has_two_stage_contract(self):
        session = Mock()
        session.post.return_value = response_with({"request_id": "voice_req", "status": "processing"})
        api = SunoAPI(api_key="test-key", session=session)

        api.voice_clone("https://example.com/sample.wav", voice_name="My Voice")
        self.assertEqual(session.post.call_args.args[0], "https://api.muapi.ai/api/v1/suno-voice-clone")

        api.confirm_voice_clone("voice_req", "https://example.com/phrase.wav")
        self.assertEqual(
            session.post.call_args.args[0],
            "https://api.muapi.ai/api/v1/suno-voice-clone/voice_req/confirm",
        )

    def test_voice_library_methods_use_expected_http_verbs(self):
        session = Mock()
        session.get.return_value = response_with({"voices": []})
        session.post.return_value = response_with({"status": "ok"})
        session.delete.return_value = response_with({"status": "deleted"})
        api = SunoAPI(api_key="test-key", session=session)

        api.list_voices()
        api.check_voice("voice_db_id")
        api.refresh_voice("voice_db_id")
        api.delete_voice("voice_db_id")

        self.assertEqual(session.get.call_args.args[0], "https://api.muapi.ai/api/v1/suno-voices")
        self.assertEqual(session.delete.call_args.args[0], "https://api.muapi.ai/api/v1/suno-voices/voice_db_id")
        self.assertEqual(session.post.call_args_list[0].args[0], "https://api.muapi.ai/api/v1/suno-voices/voice_db_id/check")
        self.assertEqual(session.post.call_args_list[1].args[0], "https://api.muapi.ai/api/v1/suno-voices/voice_db_id/refresh")

    def test_wait_for_completion_and_extract_audio(self):
        session = Mock()
        session.get.side_effect = [
            response_with({"request_id": "req", "status": "processing"}),
            response_with(
                {
                    "request_id": "req",
                    "status": "completed",
                    "outputs": ["https://example.com/song.mp3"],
                    "audio_ids": ["audio-1"],
                }
            ),
        ]
        api = SunoAPI(api_key="test-key", session=session)

        result = api.wait_for_completion("req", poll_interval=0, timeout=1)

        self.assertEqual(api.extract_audio_urls(result), ["https://example.com/song.mp3"])
        self.assertEqual(api.extract_audio_ids(result), ["audio-1"])
        self.assertEqual(session.get.call_count, 2)

    def test_validation_rejects_missing_vocal_prompt_and_bad_model(self):
        api = SunoAPI(api_key="test-key", session=Mock())

        with self.assertRaises(ValueError):
            api.create_music("Pop", instrumental=False)
        with self.assertRaises(ValueError):
            api.create_music("Pop", model="V2")
        with self.assertRaises(ValueError):
            api.voice_clone("https://example.com/sample.wav", vocal_start_s=5, vocal_end_s=5)
        with self.assertRaises(ValueError):
            api.generate_mashup([])


if __name__ == "__main__":
    unittest.main()
