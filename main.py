import requests
import tkinter as tk
from PIL import ImageGrab
from io import BytesIO
import json
import base64

CANVAS_WIDTH = 300
CANVAS_HEIGHT = 300


def on_canvas_click(event):
    canvas.create_oval(event.x - 5, event.y - 5, event.x + 5, event.y + 5, fill="black", width=0)
    canvas.bind("<B1-Motion>", on_canvas_drag)


def on_canvas_drag(event):
    canvas.create_oval(event.x - 5, event.y - 5, event.x + 5, event.y + 5, fill="black", width=0)
    recognize_drawing()


def recognize_drawing():
    # Capture the canvas and convert it to a data URL.
    image_data = BytesIO()
    ImageGrab.grab(bbox=(root.winfo_rootx() + canvas.winfo_x(),
                         root.winfo_rooty() + canvas.winfo_y(),
                         root.winfo_rootx() + canvas.winfo_x() + canvas.winfo_width(),
                         root.winfo_rooty() + canvas.winfo_y() + canvas.winfo_height())).save(image_data, format="PNG")
    image_data = base64.b64encode(image_data.getvalue()).decode("utf-8")

    # Make a request to the character recognition API (replace `API_URL` and `API_KEY` with your API details)
    API_URL = "https://your-api-url.com"
    API_KEY = "your-api-key"
    headers = {"Content-Type": "application/json", "apikey": API_KEY}
    data = {"image": f"data:image/png;base64,{image_data}", "language": "ja"}
    r = requests.post(API_URL, headers=headers, data=json.dumps(data))

    if r.status_code == 200:
        results = r.json()["output"]
        suggestions = [result["name"] for result in results]
        word_entry.delete(0, tk.END)
        word_entry.insert(tk.END, ", ".join(suggestions))
    else:
        word_entry.delete(0, tk.END)
        word_entry.insert(tk.END, f"Error: {r.status_code}")

def get_translations():
    word = word_entry.get()
    url = f"https://jisho.org/api/v1/search/words?keyword={word}"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()["data"]
        translations = []
        for result in data:
            for japanese_word in result["japanese"]:
                translations.append(f"Japanese word: {japanese_word['word']}")
            for english_meaning in result["senses"]:
                translations.append(f"English meaning: {', '.join(english_meaning['english_definitions'])}")
            translations.append("\n")
        translations_text.delete(1.0, tk.END)
        translations_text.insert(tk.END, "\n".join(translations))
    else:
        translations_text.delete(1.0, tk.END)
        translations_text.insert(tk.END, f"Error: {r.status_code}")

def clear_canvas():
    canvas.delete("all")

def save_canvas():
    x = root.winfo_rootx() + canvas.winfo_x()
    y = root.winfo_rooty() + canvas.winfo_y()
    x1 = x + canvas.winfo_width()
    y1 = y + canvas.winfo_height()
    ImageGrab.grab().crop((x, y, x1, y1)).save("canvas.png")

root = tk.Tk()
root.title("Jisho.org Word Translator")

canvas_label = tk.Label(root, text="Draw or type a kanji:")
canvas_label.pack()

canvas_frame = tk.Frame(root)
canvas_frame.pack()

canvas = tk.Canvas(canvas_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white", highlightthickness=1, highlightbackground="black")
canvas.pack(side=tk.LEFT)
canvas.bind("<1>", on_canvas_click)

canvas_buttons_frame = tk.Frame(canvas_frame)
canvas_buttons_frame.pack(side=tk.LEFT, padx=10)

clear_button = tk.Button(canvas_buttons_frame, text="Clear", command=clear_canvas)
clear_button.pack(pady=5)

save_button = tk.Button(canvas_buttons_frame, text="Save", command=save_canvas)
save_button.pack(pady=5)

word_entry_frame = tk.Frame(root)
word_entry_frame.pack()

word_label = tk.Label(word_entry_frame, text="Or enter the word you want to translate (enter verbs in infinitive):")
word_label.pack(side=tk.LEFT)

word_entry = tk.Entry(word_entry_frame)
word_entry.pack(side=tk.LEFT)

translate_button = tk.Button(root, text="Translate", command=get_translations)
translate_button.pack()

translations_label = tk.Label(root, text="Translations:")
translations_label.pack()

translations_text = tk.Text(root, height=10)
translations_text.pack()

root.mainloop()