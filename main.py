import asyncio
from modules.brain import ContentBrain
from modules.asset_manager import AssetManager
from modules.audio import AudioEngine
from modules.composer import Composer
import os
import shutil

def clean_cache():
    """Safely deletes temporary files"""
    print("🧹 Cleaning up temporary files...")
    folders_to_clean = [
        os.path.join(os.getcwd(), "assets", "audio_clips"),
        os.path.join(os.getcwd(), "assets", "video_clips"),
        os.path.join(os.getcwd(), "assets", "temp")
    ]
    for folder in folders_to_clean:
        if not os.path.exists(folder):
            continue
        if "assets" not in folder:
            continue
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                    print(f"   Deleted: {filename}")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"   Failed to delete {file_path}: {e}")
    print("✅ Workspace cleaned!")


async def main():
    print("🚀 STARTING AUTONOMOUS MOVIE SHORTS...")

    # 1. BRAIN - Story Generate
    brain = ContentBrain()
    try:
        script_data = brain.generate_script()
        if not script_data:
            print("❌ Script generation failed")
            return
    except Exception as e:
        print(f"❌ Brain Error: {e}")
        return

    # 2. AUDIO - Voiceover
    audio_engine = AudioEngine()
    try:
        script_data = await audio_engine.process_script(script_data)
    except Exception as e:
        print(f"❌ Audio Error: {e}")
        return

    # 3. ASSETS - Stock Footage
    asset_manager = AssetManager()
    assets_map = asset_manager.get_videos(script_data)

    # 4. COMPOSER - Final Video
    composer = Composer()
    final_scene_paths = composer.render_all_scenes(script_data, assets_map)

    # 5. Final Video with Transitions
    if final_scene_paths:
        composer.concatenate_with_transitions(final_scene_paths)
        clean_cache()
        print("✅ Short successfully created!")

        # ================== YOUTUBE UPLOAD ==================
        print("📤 Uploading to YouTube...")
        try:
            from modules.uploader import YouTubeUploader
            uploader = YouTubeUploader()

            # Safe title & description
            first_scene = script_data[0] if isinstance(script_data, list) else script_data
            title = f"{first_scene.get('text', 'AI Story')[:60]}... | Part {first_scene.get('id', 1)}"
            description = f"""Autonomous AI Generated Cinematic Story Series
Genre: {first_scene.get('genre', 'Cinematic')}
Part of an ongoing AI mini-movie series.

Made with ❤️ using AI"""

            video_path = "assets/final/final_short.mp4"

            video_id = uploader.upload(
                video_path=video_path,
                title=title[:100],
                description=description,
                tags=["ai", "story", "shorts", "cinematic", "aigenerated", "ai story"],
                privacy="public"
            )

            if video_id:
                print(f"✅ VIDEO UPLOADED SUCCESSFULLY!")
                print(f"🔗 https://youtu.be/{video_id}")
            else:
                print("❌ Upload failed")

        except Exception as e:
            print(f"❌ Upload Error: {e}")
        # ====================================================

    else:
        print("❌ Failed to generate scenes")


if __name__ == "__main__":
    asyncio.run(main())
