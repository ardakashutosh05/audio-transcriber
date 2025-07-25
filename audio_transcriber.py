import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import speech_recognition as sr
from pydub import AudioSegment
import os
import math

# UI Setup
root = tk.Tk()
root.title("🎤 Audio to Text Converter")
root.geometry("600x500")
root.config(bg="#f4f4f4")

file_path = ""

# Select audio file
def select_file():
    global file_path
    file_path = filedialog.askopenfilename(filetypes=[
        ("Audio Files", "*.wav *.mp3 *.m4a *.flac *.aac *.ogg *.wma *.aiff *.webm *.opus")
    ])
    file_label.config(text=file_path)

# Convert and recognize audio
def convert_audio():
    if not file_path:
        messagebox.showerror("Error", "Please select an audio file.")
        return

    recognizer = sr.Recognizer()

    try:
        # Convert to WAV
        status_label.config(text="🔁 Converting to WAV...")
        audio = AudioSegment.from_file(file_path)
        temp_wav_path = "temp_audio.wav"
        audio.export(temp_wav_path, format="wav")

        audio_duration = len(audio) / 1000.0  # in seconds
        print(f"⏱️ Duration: {audio_duration:.2f} seconds")

        if audio_duration < 1:
            messagebox.showerror("Too Short", "Audio file is too short to recognize.")
            status_label.config(text="Too short ❌")
            return

        # Prepare chunking
        chunk_length_ms = 60 * 1000  # 60 seconds
        num_chunks = math.ceil(len(audio) / chunk_length_ms)
        print(f"🔪 Total chunks: {num_chunks}")

        transcript = ""

        for i in range(num_chunks):
            start_ms = i * chunk_length_ms
            end_ms = min((i + 1) * chunk_length_ms, len(audio))
            chunk = audio[start_ms:end_ms]
            chunk_file = f"chunk_{i}.wav"
            chunk.export(chunk_file, format="wav")

            status_label.config(text=f"🎙️ Transcribing chunk {i+1}/{num_chunks}...")
            root.update()

            with sr.AudioFile(chunk_file) as source:
                audio_data = recognizer.record(source)
                try:
                    text = recognizer.recognize_google(audio_data)
                    transcript += text + " "
                except sr.UnknownValueError:
                    transcript += "[Unrecognized] "
                except sr.RequestError as e:
                    messagebox.showerror("API Error", f"Google API error:\n{e}")
                    status_label.config(text="API error ❌")
                    return

            os.remove(chunk_file)

        # Show transcript
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, transcript.strip())
        status_label.config(text="Done 🎉")

        # Cleanup
        if os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)

    except Exception as e:
        messagebox.showerror("Conversion Failed", f"Error:\n{e}")
        status_label.config(text="Failed ❌")

# Save transcript
def save_text():
    text = text_area.get(1.0, tk.END).strip()
    if not text:
        messagebox.showinfo("Empty", "No text to save.")
        return

    save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(text)
    messagebox.showinfo("Saved", f"Transcript saved to:\n{save_path}")

# UI Components
title_label = tk.Label(root, text="🎧 Audio to Text Converter", font=("Helvetica", 20), bg="#f4f4f4")
title_label.pack(pady=10)

file_btn = tk.Button(root, text="Select Audio File", command=select_file)
file_btn.pack()

file_label = tk.Label(root, text="No file selected", fg="gray", bg="#f4f4f4")
file_label.pack(pady=5)

convert_btn = tk.Button(root, text="Convert to Text", command=convert_audio, bg="#4CAF50", fg="white", padx=10)
convert_btn.pack(pady=10)

status_label = tk.Label(root, text="", fg="blue", bg="#f4f4f4")
status_label.pack()

text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=15, width=70)
text_area.pack(pady=10)

save_btn = tk.Button(root, text="Save Transcript", command=save_text)
save_btn.pack()

root.mainloop()
