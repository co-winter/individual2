import socket
import json

HOST = "127.0.0.1"
PORT = 5000


def send_message(connection, message):
    connection.sendall((json.dumps(message) + "\n").encode("utf-8"))


def receive_message(file):
    line = file.readline()
    if not line:
        return None
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        print("Received an unreadable response from the server.")
        return None


def main():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((HOST, PORT))
            print(f"Connected to Quiz Server at {HOST}:{PORT}")

            with client.makefile("r", encoding="utf-8") as server_file:
                welcome = receive_message(server_file)
                if welcome:
                    print(welcome.get("text", ""))

                while True:
                    print("\nOptions: question | score | quit")
                    choice = input("Enter a request: ").strip().lower()

                    if choice not in ["question", "score", "quit"]:
                        print("Please enter question, score, or quit.")
                        continue

                    if choice == "question":
                        send_message(client, {"action": "question"})
                        response = receive_message(server_file)
                        if response is None:
                            print("The server disconnected.")
                            break

                        if response.get("type") == "question":
                            print("\nQuestion " + str(response["question_number"]))
                            print(response["question"])
                            for option in response["choices"]:
                                print(option)

                            answer = input("Enter the number of your answer: ").strip()
                            send_message(client, {
                                "action": "answer",
                                "answer": int(answer),
                                "question_index": response["question_index"],
                            })
                            result = receive_message(server_file)
                            if result:
                                print(result.get("text", ""))
                                print(
                                    "Score: " + str(result.get("score", 0))
                                    + " / " + str(result.get("questions_answered", 0))
                                )
                        else:
                            print(response.get("text", ""))

                    elif choice == "score":
                        send_message(client, {"action": "score"})
                        response = receive_message(server_file)
                        if response:
                            print(
                                "Your score: " + str(response.get("score", 0))
                                + " / " + str(response.get("questions_answered", 0))
                            )
                            print("Total questions in quiz: " + str(response.get("total_questions", 0)))

                    elif choice == "quit":
                        send_message(client, {"action": "quit"})
                        response = receive_message(server_file)
                        if response:
                            print(response.get("text", "Goodbye!"))
                        break

    except ConnectionRefusedError:
        print("Could not connect. Start quiz_server.py first.")
    except OSError as error:
        print("A network error occurred:", error)


if __name__ == "__main__":
    main()
