# Stone, Paper, Scissor game with mediapipe, OpenCV

This project implements a real-time **Rock-Paper-Scissors** game using **Python**, **OpenCV**, and **MediaPipe**. It utilizes computer vision techniques to detect hand gestures through a webcam and allows the player to compete against a randomly acting AI. The core of the gesture recognition lies in **MediaPipe's hand landmarks model**, which tracks the position of key points on a user’s hand. By analyzing the relative positions of finger tips and joints, the code determines whether the user is showing a “rock,” “paper,” or “scissors” gesture.

The game flow is simple and interactive. Once the webcam is active, the user is prompted to press the **Enter key** to begin a round. The script then detects the hand gesture made by the user and randomly selects a move for the AI. Based on both moves, the outcome (win, lose, or draw) is determined using classic Rock-Paper-Scissors rules and displayed in real-time over the video feed using **OpenCV's GUI functions**.

The application is built using **Python 3.10**, and depends on the following libraries: `opencv-python` for video capture and display, `mediapipe` for hand landmark detection, and `random` for generating AI moves. It also includes utility functions to interpret hand gestures into binary finger states and compare them to predefined patterns for each move.

This project demonstrates how **gesture recognition** and **real-time video processing** can be integrated into an intuitive and fun game, making it a great starting point for computer vision-based human-computer interaction applications.

Requirements to run the program
1. Download all the required modules using pip install -r requirements.txt
2. To run the game script create a virtual environment in thge folder and download python 3.10.x

This is how the interface looks like.
![Alt text](images/Interface.png)
"# STONE_PAPER_SCISSOR_GAME" 
