import os
import json
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class ContentBrain:
    
    def generate_script(self):
        print("🎬 Generating Hindi 'Did You Know' Short...")

        prompt = """
You are a top Hindi YouTube Shorts creator specializing in "क्या आप जानते हैं" और "प्राचीन रहस्य" type videos.

एक engaging, mind-blowing, educational short banao (45-60 seconds).

Rules:
- Script **pure Hindi** mein ho (simple, spoken, YouTube Shorts jaisa)
- Shuruaat strong hook se karo jaise "क्या आप जानते हैं...", "प्राचीन काल में...", "वैज्ञानिक भी हैरान रह गए जब..."
- End mein ek powerful line ya sawal ke saath khatam karo
- Interesting ancient history, lost knowledge, mysterious facts pe focus karo

Return ONLY this exact JSON format:

[
  {
    "id": 1,
    "text": "Full spoken Hindi script here (45-60 seconds)",
    "visual_1": "first scene stock footage keywords in English",
    "visual_2": "second scene stock footage keywords in English"
  }
]
"""

        models = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-3.1-flash"]

        for model_name in models:
            for attempt in range(3):
                try:
                    print(f"🔄 Trying {model_name} (Attempt {attempt+1}/3)")
                    
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config={"response_mime_type": "application/json"}
                    )

                    clean = response.text.strip().replace("```json", "").replace("```", "").strip()
                    result = json.loads(clean)

                    print(f"✅ SUCCESS with {model_name} → Hindi Did You Know Short Generated")
                    return result

                except Exception as e:
                    err = str(e)
                    print(f"❌ Failed {model_name}: {err[:120]}")
                    if "503" in err or "high demand" in err or "UNAVAILABLE" in err:
                        print("⏳ High demand, waiting 10 seconds...")
                        time.sleep(10)
                        continue
                    else:
                        break

        print("❌ All models failed. Try again after some time.")
        return None


# For testing
if __name__ == "__main__":
    brain = ContentBrain()
    output = brain.generate_script()
    if output:
        with open("latest_script.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
        print("✅ latest_script.json saved")
