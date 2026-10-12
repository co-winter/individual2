import socket
import json

HOST = "127.0.0.1"
PORT = 5000

QUESTIONS = [
    {"question": "What is 2 + 2?", "choices": ["1. 3", "2. 4", "3. 5"], "answer": "2"},
    {"question": "Which language is this server written in?", "choices": ["1. Python", "2. Java", "3. C++"], "answer": "1"},
    {"question": "Which device connects computers in a local network?", "choices": ["1. Keyboard", "2. Monitor", "3. Switch"], "answer": "3"},
]


def send_message(connection, message):
    connection.sendall((json.dumps(message) + "\n").encode("utf-8"))


def receive_message(file):
    line = file.readline()
    if not line:
        return None
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return {"type": "invalid"}


def handle_client(connection, address):
    print(f"Client connected: {address}")
    score = 0
    asked_questions = []

    with connection:
        with connection.makefile("r", encoding="utf-8") as client_file:
            send_message(connection, {
                "type": "message",
                "text": "Welcome to the Quiz Server! Type question, score, or quit."
            })

            while True:
                request = receive_message(client_file)
                if request is None:
                    print(f"Client disconnected: {address}")
                    break

                request_type = request.get("type", "").lower()

                if request_type == "question":
                    available = [
                        index for index in range(len(QUESTIONS))
                        if index not in asked_questions
                    ]
                    if not available:
                        send_message(connection, {
                            "type": "message",
                            "text": "You have answered all the questions. Type score to see your results."
                        })
                        continue

                    question_index = available[0]
                    asked_questions.append(question_index)
                    question = QUESTIONS[question_index]
                    send_message(connection, {
                        "type": "question",
                        "question": question["question"],
                        "choices": question["choices"],
                        "question_number": len(asked_questions),
                        "total_questions": len(QUESTIONS),
                        "question_index": question_index,
                    })

                elif request_type == "answer":
                    answer = request.get("answer", "").strip()
                    question_index = request.get("question_index")

                    if not isinstance(question_index, int) or question_index not in asked_questions:
                        send_message(connection, {
                            "type": "message",
                            "text": "Please request a question before answering."
                        })
                        continue

                    question = QUESTIONS[question_index]
                    if answer == question["answer"]:
                        score += 1
                        response_text = "Correct!"
                    else:
                        response_text = "Not quite. The correct answer was " + question["answer"] + "."

                    send_message(connection, {
                        "type": "answer_result",
                        "text": response_text,
                        "score": score,
                        "questions_answered": len(asked_questions),
                    })

                elif request_type == "score":
                    send_message(connection, {
                        "type": "score",
                        "score": score,
                        "questions_answered": len(asked_questions),
                        "total_questions": len(QUESTIONS),
                    })

                elif request_type == "quit":
                    send_message(connection, {
                        "type": "message",
                        "text": "Thanks for playing. Goodbye!"
                    })
                    break

                else:
                    send_message(connection, {
                        "type": "message",
                        "text": "Unknown request. Use question, score, or quit."
                    })

    print(f"Ready for another client. Previous client: {address}")


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f"Quiz Server listening on {HOST}:{PORT}")
        print("Start quiz_client.py in another terminal to connect.")

        while True:
            connection, address = server.accept()
            handle_client(connection, address)


if __name__ == "__main__":
    main()
