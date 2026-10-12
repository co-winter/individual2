# Quiz Server

## Project Description

Quiz Server is a small Python networking project. A client connects to a server over a TCP socket, sends requests, and receives responses. The server asks quiz questions and keeps track of the client's score.

The project uses Python's built-in `socket` library for networking and JSON to format messages sent between the client and server.

## Requirements Demonstrated

1. The server listens on `127.0.0.1`, port `5000`.
2. The client connects to the waiting server.
3. The client sends requests such as `question`, `score`, and `quit`.
4. The server processes each request and sends a JSON response.
5. The server handles a client disconnecting and then waits for another client.

## Stretch Challenge

The server supports multiple request types: `question`, `score`, and `quit`. It also processes `answer` messages as part of answering a question.

## Files

- `quiz_server.py`: Waits for client connections, sends quiz questions, checks answers, and tracks scores.
- `quiz_client.py`: Connects to the server and lets the user play the quiz.
- `README.md`: Project information and instructions.

## How to Run

You need Python 3 installed.

1. Open a terminal in this project folder.
2. Start the server:

   ```bash
   python quiz_server.py
   ```

3. Open a second terminal in the same folder.
4. Start the client:

   ```bash
   python quiz_client.py
   ```

5. Use `question` to get a quiz question, `score` to see your score, or `quit` to disconnect.

Start the server before starting the client. Both programs use `127.0.0.1`, so they run on the same computer. To connect from another computer, the host address and network settings must be changed.

## Message Format

The client and server exchange JSON messages. Each message is sent on its own line so the receiving program knows where one message ends.

## Notes

This project is for learning basic networking. It is designed for local testing and is not intended as a public internet service.
