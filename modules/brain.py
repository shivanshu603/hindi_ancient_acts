import os
import json
from google import genai
from dotenv import load_dotenv

# Load API Key
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY") or "api-key")

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

    def save_state(self):
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=4, ensure_ascii=False)

    def generate_script(self):
        """Fully Autonomous Movie-Style Story Generator"""
        print("🎬 Autonomous Story Mode Running...")

        current = self.state["current_story"]

        # Master Prompt
        prompt = f"""
You are an autonomous Cinematic Storyteller AI running a never-ending YouTube Shorts mini-movie series.

CURRENT STATE:
{json.dumps(current, indent=2)}

RULES:
1. If there is no current story OR current part is completed → Create a **completely new original story**.
   - Give a catchy, viral title
   - Choose any genre randomly: horror, dark fantasy, sci-fi thriller, psychological mystery, romance, motivational, supernatural, action-adventure
   - Create 2-4 memorable characters with short descriptions
   - Decide total parts (6 to 15)

2. If story is ongoing → Write **ONLY the next part** (Part #{current["part_number"]})
   - 100% consistency rakho characters, plot, tone aur previous events ke saath
   - Strong hook se shuru karo
   - Dramatic, emotional aur cinematic rakho
   - Length: 45-60 seconds jab voice mein bole
   - End with a strong cliffhanger

OUTPUT STRICT JSON ONLY:
{{
  "title": "Story Title",
  "genre": "horror",
  "part_number": X,
  "script": "Full spoken script text here...",
  "visual_1": "first visual keywords for stock footage",
  "visual_2": "second visual keywords for stock footage",
  "updated_state": {{ complete updated current_story object here }}
}}
"""

        print("🤖 Generating next part / new story...")
        response = client.models.generate_content(
            model='gemini-3-flash-preview',
            contents=prompt
        )

        clean_text = response.text.replace('```json', '').replace('```', '').strip()

        try:
            result = json.loads(clean_text)
            
            # Update state
            self.state["current_story"] = result["updated_state"]
            self.state["last_run"] = "2026-04-14"  # current date
            self.save_state()

            print(f"✅ Story: {result['title']} | Part {result['part_number']}")
            return result

        except Exception as e:
            print("❌ JSON Parse Error:", e)
            print("Raw output:", clean_text)
            return None


# --- TESTING ---
if __name__ == "__main__":
    brain = ContentBrain()
    script = brain.generate_script()
    
    if script:
        with open("latest_script.json", "w", encoding="utf-8") as f:
            json.dump(script, f, indent=4, ensure_ascii=False)
        print("✅ Script saved to latest_script.json")
