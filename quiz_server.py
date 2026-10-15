import json
import socket

HOST = "127.0.0.1"
PORT = 5000
QUESTIONS = [
    {"question": "What does IP stand for?", "choices": ["Internet Protocol", "Internal Program", "Input Process"], "answer": 1},
    {"question": "Which protocol creates a reliable connection?", "choices": ["UDP", "TCP", "FTP"], "answer": 2},
    {"question": "What is the server's job?", "choices": ["Draw the window", "Wait for requests and respond", "Install Python"], "answer": 2},
]

def send(connection, data):
    connection.sendall((json.dumps(data) + "\n").encode("utf-8"))

def handle_client(connection, address):
    score = 0
    answered = 0
    asked = set()
    print("Connected:", address)
    send(connection, {"type": "message", "text": "Connected to the quiz server."})
    reader = connection.makefile("r", encoding="utf-8")
    try:
        for line in reader:
            if not line:
                break
            try:
                request = json.loads(line)
            except json.JSONDecodeError:  
                continue
            action = request.get("action")
            if action == "question":
                available = [i for i in range(len(QUESTIONS)) if i not in asked]
                if not available:
                    send(connection, {"type": "finished", "text": "All questions answered.", "score": score, "questions_answered": answered, "total_questions": len(QUESTIONS)})
                else:
                    i = available[0]
                    asked.add(i)
                    q = QUESTIONS[i]
                    send(connection, {"type": "question", "question": q["question"], "choices": q["choices"], "question_number": len(asked), "total_questions": len(QUESTIONS), "question_index": i})
            elif action == "answer":
                i = request.get("question_index")
                answer = request.get("answer")
                if not isinstance(i, int) or i not in asked:
                    send(connection, {"type": "error", "text": "Request a question first."})
                else:
                    correct = answer == QUESTIONS[i]["answer"]
                    if correct:
                        score += 1
                        result = "Correct!"
                    else:
                        correct_text = QUESTIONS[i]["choices"][QUESTIONS[i]["answer"] - 1]
                        result = "Not quite. Correct answer: " + correct_text
                    answered += 1
                    send(connection, {"type": "answer_result", "text": result, "score": score, "questions_answered": answered, "total_questions": len(QUESTIONS)})
            elif action == "score":
                send(connection, {"type": "score", "score": score, "questions_answered": answered, "total_questions": len(QUESTIONS)})
            elif action == "quit":
                send(connection, {"type": "message", "text": "Disconnected from quiz server."})
                break
            else:
                send(connection, {"type": "error", "text": "Unknown request."})
    except (ConnectionResetError, BrokenPipeError):
        print("Client disconnected unexpectedly:", address)
    finally:
        reader.close()
        connection.close()
        print("Disconnected:", address)

def main():
    print(f"Quiz server listening on {HOST}:{PORT}")
    print("Keep this terminal open while using the GUI.")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        while True:
            connection, address = server_socket.accept()
            handle_client(connection, address)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nQuiz server stopped.")
