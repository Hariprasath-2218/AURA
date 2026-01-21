from dotenv import load_dotenv
import time
import os

# ===== PPT imports =====
from app.llm import generate_slides
from app.ppt import create_ppt

# ===== AURA imports =====
from aura.stt import deepgram_listen, offline_listen
from aura.llm_chat import ask_online_llm, ask_llamacpp
from aura.tts import speak
from aura.net import internet_available

load_dotenv()


# =====================================================
# MODE SWITCH DETECTION
# =====================================================
def detect_mode_switch(text):
    if not isinstance(text, str):
        return None

    text = text.strip().lower()

    if not text:
        return None

    if "ppt" in text or "presentation" in text or "one" in text or "1" in text:
        return "ppt"

    if "conversation" in text or "chat" in text or "two" in text or "2" in text:
        return "conversation"

    return None


# =====================================================
# CONVERSATION MODE (DEFAULT)
# =====================================================
def conversation_mode():
    print("\n🗣️ CONVERSATION MODE (Say 'PPT Generator Mode' to switch)\n")
    speak("Conversation mode activated")

    while True:
        try:
            # ---- STT ----
            if internet_available():
                print("\n🌐 ONLINE MODE")
                user_text = deepgram_listen(5)
            else:
                print("\n📴 OFFLINE MODE")
                user_text = offline_listen()

            if not user_text:
                continue

            print("🧑 You:", user_text)

            # ---- MODE SWITCH ----
            switch = detect_mode_switch(user_text)
            if switch == "ppt":
                print("🔄 Switching to PPT Generator Mode")
                speak("Switching to PPT Generator Mode")
                ppt_generator_mode()
                return

            # ---- LLM ----
            if internet_available():
                ai = ask_online_llm(user_text)
            else:
                ai = ask_llamacpp(user_text)

            print("🤖 AI:", ai)
            speak(ai)

            time.sleep(0.05)

        except KeyboardInterrupt:
            print("\n👋 Conversation Mode stopped")
            break
        except Exception as e:
            print("⚠️ Conversation Error:", e)
            time.sleep(1)


# =====================================================
# PPT GENERATOR MODE
# =====================================================
def ppt_generator_mode():
    print("\n📊 PPT GENERATOR MODE (Say 'Conversation Mode' to switch)\n")
    speak("PPT Generator mode activated. Please say the topic.")

    while True:
        try:
            topic = offline_listen()

            if not topic:
                continue

            print("🧑 You:", topic)

            # ---- MODE SWITCH ----
            switch = detect_mode_switch(topic)
            if switch == "conversation":
                print("🔄 Switching to Conversation Mode")
                speak("Switching to Conversation Mode")
                conversation_mode()
                return

            # ---- PPT GENERATION ----
            print("📌 Topic:", topic)
            slides = generate_slides(topic)

            output_file = "output.pptx"
            create_ppt(slides)

            print("✅ PPT generated successfully!")
            speak("Your presentation has been generated successfully")

            # ✅ AUTO OPEN PPT
            if os.path.exists(output_file):
                os.startfile(output_file)

            time.sleep(0.1)

        except KeyboardInterrupt:
            print("\n👋 PPT Generator Mode stopped")
            break
        except Exception as e:
            print("❌ PPT Error:", e)
            speak("There was an error generating the presentation")
            time.sleep(1)


# =====================================================
# ENTRY POINT — DEFAULT MODE
# =====================================================
if __name__ == "__main__":
    print("\n🤖 AURA READY")
    speak("Aura is ready. Conversation mode activated.")
    conversation_mode()
