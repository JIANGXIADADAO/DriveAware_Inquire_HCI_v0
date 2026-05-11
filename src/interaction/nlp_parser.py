import os
import config


class NLPParser:
    def __init__(self):
        self.api_key = os.environ.get("DEEPSEEK_API_KEY")
        self.client = None
        if self.api_key:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=config.DEEPSEEK_BASE_URL,
            )
            print("[NLP] DeepSeek API configured.")
        else:
            print("[NLP] No DEEPSEEK_API_KEY set. Using keyword matching.")

    def parse_intent(self, transcript):
        if not transcript:
            return "unknown"

        # Keyword matching FIRST — fast, free, handles 90% of commands
        kw_result = self._keyword_parse(transcript)
        if kw_result != "unknown":
            return kw_result

        # DeepSeek API as fallback for ambiguous phrases only
        if self.client:
            try:
                result = self._api_parse(transcript)
                if result in ("dynamic", "rest"):
                    return result
            except Exception as e:
                print(f"[NLP] DeepSeek API error: {e}")

        return "unknown"

    def _api_parse(self, transcript):
        for attempt in range(3):
            try:
                response = self.client.chat.completions.create(
                    model=config.DEEPSEEK_MODEL,
                    temperature=0.0,
                    max_tokens=10,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                'Classify the user intent as "dynamic", "rest", or "unknown". '
                                '"dynamic" if they want Dynamic/Sport/Active mode or agree to switch to it. '
                                '"rest" if they want Rest/Relax/Comfort/Calm mode or decline a switch. '
                                'Reply with only one word.'
                            ),
                        },
                        {
                            "role": "user",
                            "content": f'User said: "{transcript}"',
                        },
                    ],
                )
                intent = response.choices[0].message.content.strip().lower()
                print(f"[NLP] API response: {intent}")
                if intent in ("dynamic", "rest"):
                    return intent
                return "unknown"
            except Exception as e:
                print(f"[NLP] API error (attempt {attempt+1}/3): {e}")
                if attempt < 2:
                    import time
                    time.sleep(1.0 * (attempt + 1))
        return "unknown"

    def _keyword_parse(self, transcript):
        import string as _string
        t = transcript.lower().strip().rstrip(_string.punctuation)
        # Yes-like → Dynamic Mode
        if t in ("yes", "yeah", "yep", "y", "ok", "okay", "sure",
                 "yes please", "of course", "absolutely", "definitely"):
            return "dynamic"
        # Common Whisper mishearings of "yes" (especially with "small" model)
        if t in ("yinz", "yis", "yass", "yesss", "yees", "yas", "yus", "yiss"):
            return "dynamic"
        if any(w in t for w in ("yes", "yeah", "yep", "dynamic", "sport", "active")):
            return "dynamic"
        # No-like → Rest Mode
        if t in ("no", "nope", "nah", "n", "no thanks"):
            return "rest"
        # Common Whisper mishearings/truncations of "rest" ("small" model drops final 't')
        if t in ("res", "ress", "rest "):
            return "rest"
        if any(w in t for w in ("rest", "res", "relax", "calm", "comfort",
                                "no", "nope", "nah", "stay", "quiet",
                                "peaceful", "chill")):
            return "rest"
        return "unknown"
