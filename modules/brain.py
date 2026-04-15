import os
import json
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class ContentBrain:
    
    def __init__(self):
        self.state_file = "stories_state.json"
        self.state = self.load_state()

    def load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "current_story": {"title": "", "genre": "", "part_number": 1, "max_parts": 10, "summary_so_far": "", "characters": []},
            "last_run": ""
        }

    def save_state(self, new_state):
        self.state["current_story"] = new_state
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=4, ensure_ascii=False)

    def generate_script(self):
        print("🎬 Autonomous Movie Story Mode Started...")

        current = self.state["current_story"]

        prompt = f"""
You are an autonomous Cinematic Storyteller AI.

CURRENT STATE:
{json.dumps(current, indent=2)}

Task:
- Agar story nahi hai ya complete ho gayi → Nayi story banao (viral title, random genre, 2-4 characters)
- Agar story chal rahi hai → Sirf next part likho

Rules:
- 100% consistency rakho
- Strong hook + dramatic tone
- 45-60 seconds script
- End with cliffhanger

Return ONLY this JSON format (list with 1 scene):
[
  {{
    "id": 1,
    "text": "Full spoken script here (45-60 seconds)",
    "visual_1": "first scene keywords",
    "visual_2": "second scene keywords"
  }}
]
"""

        # Smart Model Selection (Primary + Backup)
        models = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-3.1-flash"]

        for model_name in models:
            for attempt in range(3):
                try:
                    print(f"🔄 Trying {model_name} (Attempt {attempt+1})")
                    response = client.models.generate_content(model=model_name, contents=prompt)
                    clean = response.text.strip().replace("```json", "").replace("```", "").strip()
                    result = json.loads(clean)

                    # Save state for next part
                    self.save_state(result[0].get("updated_state", current) if isinstance(result, list) and "updated_state" in result[0] else current)

                    print(f"✅ SUCCESS → {result[0]['text'][:60]}...")
                    return result   # ← Important: returning list (audio.py ke liye)

                except Exception as e:
                    err = str(e)
                    print(f"❌ Failed {model_name}: {err[:100]}")
                    if "503" in err or "high demand" in err:
                        time.sleep(10)
                        continue
                    else:
                        break

        print("❌ All models failed")
        return None


if __name__ == "__main__":
    brain = ContentBrain()
    output = brain.generate_script()
    if output:
        with open("latest_script.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
        print("✅ latest_script.json saved")
