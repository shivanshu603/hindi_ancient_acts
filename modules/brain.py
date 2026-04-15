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

        # Smart Model Selection Logic
        primary_model = "gemini-2.5-flash"          # Best quality (pehle isko try karega)
        backup_models = ["gemini-2.5-flash-lite", "gemini-3.1-flash", "gemini-2.0-flash-exp"]

        models_to_try = [primary_model] + backup_models

        for model_name in models_to_try:
            for attempt in range(3):   # Har model ko 3 baar try karega
                try:
                    print(f"🔄 Trying Model: {model_name} (Attempt {attempt+1}/3)")
                    
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt
                    )

                    clean = response.text.strip().replace("```json", "").replace("```", "").strip()
                    result = json.loads(clean)

                    self.save_state(result["updated_state"])
                    print(f"✅ SUCCESS with {model_name} → {result['title']} | Part {result['part_number']}")
                    return result

                except Exception as e:
                    error_str = str(e)
                    print(f"❌ Failed with {model_name}: {error_str[:100]}")

                    if "503" in error_str or "high demand" in error_str or "UNAVAILABLE" in error_str:
                        print("⏳ High demand detected, waiting 10 seconds...")
                        time.sleep(10)
                        continue
                    else:
                        break  # koi aur error hai toh agle model pe jaao

        print("❌ All models failed. Please try again after 10-15 minutes.")
        return None


# Local testing
if __name__ == "__main__":
    brain = ContentBrain()
    output = brain.generate_script()
    if output:
        with open("latest_script.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
        print("✅ latest_script.json saved")
