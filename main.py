import os
import time
import audio_manager
import chatgpt_responder
import database_manager
from dotenv import load_dotenv
from mic_input_manager import MicInputManager

# Load environment variables
load_dotenv()

def transfer_to_representative(user_input, ai_responder):
    print(f"Transferring to human representative. User input: {user_input}")
    ai_responder.end_conversation()

def process_audio(audio_file, audio_controller, ai_responder):
    try:
        prompt = audio_controller.audio2text(audio_file)
        print(f"Transcribed text: {prompt}")

        if prompt.lower() in ["goodbye", "bye", "end call", "hang up"]:
            print("Customer ended the call.")
            ai_responder.end_conversation()
            return False

        response = ai_responder.get_response(prompt)
        print(f"AI response: {response}")

        if "connect you with a representative" in response.lower():
            transfer_to_representative(prompt, ai_responder)
            return False
        else:
            audio_controller.text2audio(response)

        return True
    except Exception as e:
        print(f"Error processing audio: {e}")
        return False

def main():
    audio_controller = audio_manager.AudioManager()
    mic_manager = MicInputManager()

    api_key = os.getenv("OPENAI_API_KEY")
    
    with database_manager.DatabaseManager() as db_manager:
        ai_responder = chatgpt_responder.ChatGPTResponder(api_key, db_manager)

        print("AI Assistant is ready. Say 'goodbye' to end the conversation.")

        while True:
            try:
                start_time = time.time()

                print("Please speak now...")
                input_file = mic_manager.get_input()
                
                continue_conversation = process_audio(input_file, audio_controller, ai_responder)
                
                if input_file:
                    os.remove(input_file)  # Remove temporary mic input file

                end_time = time.time()
                print(f"Response time: {end_time - start_time:.2f} seconds")

                if not continue_conversation:
                    print("Conversation ended. Ready for a new call.")
                    continue

                print("Ready for next input.")

            except KeyboardInterrupt:
                print("\nEnding the current conversation and exiting the AI Assistant.")
                ai_responder.end_conversation()
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                print("Restarting the input process...")

    print("Database connection closed. Exiting program.")

if __name__ == "__main__":
    main()