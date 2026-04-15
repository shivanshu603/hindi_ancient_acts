import os
import json
from dotenv import load_dotenv
from google import genai   # New official SDK

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
            "current_story": {
                "title": "",
                "genre": "",
                "part_number": 1,
                "max_parts": 10,
                "summary_so_far": "",
                "characters": []
            },
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
You are an autonomous Cinematic Storyteller AI running a never-ending YouTube Shorts mini-movie series.

CURRENT STATE:
{json.dumps(current, indent=2)}

Task:
- Agar story nahi hai ya complete ho gayi → Nayi original story banao (viral title, random genre, 2-4 characters)
- Agar story chal rahi hai → Sirf next part likho (Part #{current.get('part_number', 1)})

Rules:
- Characters aur plot 100% consistent rakho
- Strong dramatic hook se shuru karo
- 45-60 seconds ka script
- End with powerful cliffhanger

Return ONLY valid JSON:
{{
  "title": "Story Title",
  "genre": "horror",
  "part_number": number,
  "script": "Full spoken script text here...",
  "visual_1": "first scene stock footage keywords",
  "visual_2": "second scene stock footage keywords",
  "updated_state": {{full updated current_story object}}
}}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",          # ← Yeh current best working model hai (April 2026)
            contents=prompt
        )

        clean = response.text.strip().replace("```json", "").replace("```", "").strip()

        try:
            result = json.loads(clean)
            self.save_state(result["updated_state"])
            print(f"✅ Generated: {result['title']} | Part {result['part_number']}")
            return result
        except Exception as e:
            print("❌ JSON Error:", e)
            print("Raw output:", clean[:500])
            return None


# Local testing
if __name__ == "__main__":
    brain = ContentBrain()
    output = brain.generate_script()
    if output:
        with open("latest_script.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
        print("✅ latest_script.json saved")
