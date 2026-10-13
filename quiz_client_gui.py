import json
import queue
import socket
import threading
import tkinter as tk
from tkinter import messagebox

HOST = "127.0.0.1"
PORT = 5000

class QuizGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Networking Quiz")
        self.root.geometry("620x500")
        self.root.minsize(560, 460)
        self.root.configure(bg="#f3f6fb")
        self.connection = None
        self.reader = None
        self.question_index = None
        self.waiting = False
        self.events = queue.Queue()

        tk.Label(root, text="Networking Quiz", font=("Segoe UI", 22, "bold"),
                 bg="#f3f6fb", fg="#17365d").pack(pady=(20, 4))
        tk.Label(root, text="A small quiz that talks to a Python server",
                 font=("Segoe UI", 10), bg="#f3f6fb", fg="#526579").pack(pady=(0, 12))
        self.status = tk.Label(root, text="Not connected to server",
                               font=("Segoe UI", 10, "bold"), bg="#f3f6fb", fg="#a33b32")
        self.status.pack(pady=(0, 10))

        card = tk.Frame(root, bg="white", padx=22, pady=18)
        card.pack(fill="both", expand=True, padx=26, pady=(0, 16))
        self.question = tk.Label(card, text="Click Connect to begin.",
                                 font=("Segoe UI", 15, "bold"), bg="white",
                                 fg="#203040", wraplength=500, justify="left")
        self.question.pack(anchor="w", pady=(4, 16))
        self.answers = []
        for number in range(1, 4):
            button = tk.Button(card, text=f"Answer {number}", font=("Segoe UI", 11),
                               anchor="w", padx=12, pady=9, bg="#eaf1fb", fg="#17365d",
                               relief="flat", state="disabled",
                               command=lambda choice=number: self.answer(choice))
            button.pack(fill="x", pady=4)
            self.answers.append(button)
        self.feedback = tk.Label(card, text="", font=("Segoe UI", 10), bg="white",
                                 fg="#2f6b4f", wraplength=500, justify="left")
        self.feedback.pack(anchor="w", pady=(10, 2))
        self.score = tk.Label(card, text="Score: 0 / 0", font=("Segoe UI", 10, "bold"),
                              bg="white", fg="#526579")
        self.score.pack(anchor="w", pady=(5, 0))

        bottom = tk.Frame(root, bg="#f3f6fb")
        bottom.pack(fill="x", padx=26, pady=(0, 16))
        self.connect_button = tk.Button(bottom, text="Connect", command=self.connect,
                                        font=("Segoe UI", 10, "bold"), bg="#2459a9",
                                        fg="white", relief="flat", padx=16, pady=8)
        self.connect_button.pack(side="left")
        self.next_button = tk.Button(bottom, text="Next Question", command=self.next_question,
                                     state="disabled", bg="#dce7f7", fg="#17365d",
                                     relief="flat", padx=14, pady=8)
        self.next_button.pack(side="left", padx=8)
        self.score_button = tk.Button(bottom, text="Check Score", command=self.check_score,
                                      state="disabled", bg="#e4e9f0", fg="#203040",
                                      relief="flat", padx=12, pady=8)
        self.score_button.pack(side="left")
        root.protocol("WM_DELETE_WINDOW", self.close)
        root.after(100, self.check_events)

    def connect(self):
        self.connect_button.config(state="disabled", text="Connecting...")
        threading.Thread(target=self.open_connection, daemon=True).start()

    def open_connection(self):
        try:
            connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connection.settimeout(5)
            connection.connect((HOST, PORT))
            connection.settimeout(None)
            reader = connection.makefile("r", encoding="utf-8")
            self.events.put(("connected", connection, reader))
        except OSError as error:
            self.events.put(("connect_error", str(error)))

    def request(self, data):
        threading.Thread(target=self.send_request, args=(data,), daemon=True).start()

    def send_request(self, data):
        try:
            self.connection.sendall((json.dumps(data) + "\\n").encode("utf-8"))
            line = self.reader.readline()
            if not line:
                self.events.put(("disconnected", "The server closed the connection."))
            else:
                self.events.put(("response", json.loads(line)))
        except (OSError, json.JSONDecodeError) as error:
            self.events.put(("disconnected", str(error)))

    def next_question(self):
        if self.connection is not None:
            self.question_index = None
            self.disable_answers()
            self.next_button.config(state="disabled")
            self.feedback.config(text="")
            self.question.config(text="Getting a question...")
            self.request({"action": "question"})

    def answer(self, choice):
        if self.connection is not None and self.question_index is not None and not self.waiting:
            self.waiting = True
            self.disable_answers()
            self.feedback.config(text="Checking your answer...")
            self.request({"action": "answer", "answer": choice, "question_index": self.question_index})

    def check_score(self):
        if self.connection is not None:
            self.request({"action": "score"})

    def check_events(self):
        while not self.events.empty():
            event = self.events.get()
            if event[0] == "connected":
                self.connection, self.reader = event[1], event[2]
                self.status.config(text="Connected to server", fg="#2f6b4f")
                self.connect_button.config(text="Connected", state="disabled")
                self.next_button.config(state="normal")
                self.score_button.config(state="normal")
                self.question.config(text="You're connected. Click Next Question.")
            elif event[0] == "connect_error":
                self.connect_button.config(text="Connect", state="normal")
                self.status.config(text="Could not connect to server", fg="#a33b32")
                messagebox.showerror("Connection failed",
                    "Start the server in another VS Code terminal with:\n\npython quiz_server.py\n\n"
                    "Then click Connect again.\n\nDetails: " + event[1])
            elif event[0] == "disconnected":
                self.status.config(text="Disconnected from server", fg="#a33b32")
                self.disable_answers()
                self.next_button.config(state="disabled")
                self.score_button.config(state="disabled")
                self.question.config(text="The connection ended. Close this window and reconnect.")
                self.feedback.config(text=event[1])
            elif event[0] == "response":
                self.show_response(event[1])
        self.root.after(100, self.check_events)

    def show_response(self, data):
        kind = data.get("type")
        if kind == "question":
            self.question_index = data["question_index"]
            self.question.config(text=f"Question {data['question_number']} of {data['total_questions']}\n\n{data['question']}")
            for i, button in enumerate(self.answers):
                button.config(text=f"{i + 1}. {data['choices'][i]}", state="normal")
            self.feedback.config(text="Choose an answer above.", fg="#526579")
            self.waiting = False
        elif kind == "answer_result":
            self.feedback.config(text=data["text"], fg="#2f6b4f")
            self.score.config(text=f"Score: {data['score']} / {data['questions_answered']}")
            self.waiting = False
            if data["questions_answered"] >= data["total_questions"]:
                self.question.config(text="Quiz complete! Nice work.")
                self.feedback.config(text=f"{data['text']}\n\nFinal score: {data['score']} / {data['total_questions']}")
                self.next_button.config(state="disabled")
            else:
                self.next_button.config(state="normal")
        elif kind == "score":
            self.score.config(text=f"Score: {data['score']} / {data['questions_answered']}")
            self.feedback.config(text=f"You have answered {data['questions_answered']} of {data['total_questions']} questions.")
        elif kind == "finished":
            self.question.config(text="Quiz complete!")
            self.feedback.config(text=f"{data['text']}\nFinal score: {data['score']} / {data['total_questions']}")
            self.score.config(text=f"Score: {data['score']} / {data['questions_answered']}")
            self.disable_answers()
            self.next_button.config(state="disabled")
        elif kind in ("error", "message"):
            self.feedback.config(text=data.get("text", "Server response received."))
            self.waiting = False

    def disable_answers(self):
        for button in self.answers:
            button.config(state="disabled")

    def close(self):
        if self.connection is not None:
            try:
                self.connection.sendall((json.dumps({"action": "quit"}) + "\\n").encode("utf-8"))
                self.reader.close()
                self.connection.close()
            except OSError:
                pass
        self.root.destroy()

def main():
    root = tk.Tk()
    QuizGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
