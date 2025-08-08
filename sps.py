import cv2
import mediapipe as mp
import random
import os
import pickle
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk

# ------------------ Colors ------------------
PALE_PURPLE = "#e3d0d8"         # Background
MOUNTBATTEN_PINK = "#827081"    # Text color (words and numbers)

# Use pale purple for frame backgrounds to keep consistency
FRAME_BG = PALE_PURPLE
PLAYER_BG = "#d9cbd3"  # Slightly lighter pale purple for player bg
AI_BG = "#d9cbd3"      # Same for AI bg (or you can change)

# ------------------ Config ------------------
HIGHSCORE_FILE = "highscore.pkl"
if os.path.exists(HIGHSCORE_FILE):
    with open(HIGHSCORE_FILE, "rb") as f:
        highest_score = pickle.load(f)
else:
    highest_score = 0

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

gestures = {
    'stone': [0, 0, 0, 0, 0],
    'paper': [1, 1, 1, 1, 1],
    'scissors': [0, 1, 1, 0, 0],
}

gesture_images = {
    'stone': cv2.imread("images/stone.jpg"),
    'paper': cv2.imread("images/paper.jpg"),
    'scissors': cv2.imread("images/scissor.jpg")
}
for k, img in gesture_images.items():
    if img is not None:
        gesture_images[k] = cv2.resize(img, (320, 240))
    else:
        gesture_images[k] = np.ones((240, 320, 3), dtype=np.uint8) * 200

cap = cv2.VideoCapture(0)

score = 0
rounds_played = 0
waiting_for_next = False
player_move = ""
ai_move = ""
winner_text = ""
frozen_player_frame = None  # store frozen camera frame


def reset_game():
    global score, rounds_played, waiting_for_next, player_move, ai_move, frozen_player_frame, winner_text, highest_score
    if score > highest_score:
        highest_score = score
        with open(HIGHSCORE_FILE, "wb") as f:
            pickle.dump(highest_score, f)
    score = 0
    rounds_played = 0
    waiting_for_next = False
    player_move = ""
    ai_move = ""
    winner_text = ""
    frozen_player_frame = None
    result_label.config(text="")
    score_label.config(text=f"Score: {score}")
    round_label.config(text=f"Round 1 of 10")
    update_frame()

# ------------------ Functions ------------------
def get_finger_states(hand_landmarks):
    tips_ids = [4, 8, 12, 16, 20]
    fingers = []
    fingers.append(1 if hand_landmarks.landmark[tips_ids[0]].x <
                   hand_landmarks.landmark[tips_ids[0] - 1].x else 0)
    for i in range(1, 5):
        fingers.append(1 if hand_landmarks.landmark[tips_ids[i]].y <
                       hand_landmarks.landmark[tips_ids[i] - 2].y else 0)
    return fingers

def recognize_gesture(finger_states):
    for gesture, pattern in gestures.items():
        if finger_states == pattern:
            return gesture
    return "Unknown"

def decide_winner(player, ai):
    if player == ai:
        return "Draw"
    elif (player == 'stone' and ai == 'scissors') or \
         (player == 'scissors' and ai == 'paper') or \
         (player == 'paper' and ai == 'stone'):
        return "You Win!"
    else:
        return "AI Wins!"


def start_next_round(event=None):
    global waiting_for_next, ai_move, player_move, frozen_player_frame, rounds_played, winner_text
    if rounds_played < 10:
        rounds_played += 1  # Increment round count on Enter press
        waiting_for_next = False
        ai_move = ""
        player_move = ""
        winner_text = ""
        frozen_player_frame = None  # unfreeze camera
        result_label.config(text="")
        round_label.config(text=f"Round {rounds_played + 1} of 10")
        score_label.config(text=f"Score: {score}")


def update_frame():
    global score, highest_score, waiting_for_next, player_move, ai_move, rounds_played, frozen_player_frame, winner_text

    if rounds_played >= 10:
        round_label.config(text=f"Game Over! Final Score: {score}/10")
        result_label.config(text=f"Highest Score: {highest_score}")
        root.after(3000, reset_game)
        return

    current_round = rounds_played + 1  # Displayed round number

    if waiting_for_next and frozen_player_frame is not None:
        player_img_display = frozen_player_frame
    else:
        ret, frame = cap.read()
        if not ret:
            return
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result_hands = hands.process(rgb)

        if not waiting_for_next and result_hands.multi_hand_landmarks:
            finger_states = get_finger_states(result_hands.multi_hand_landmarks[0])
            player_move = recognize_gesture(finger_states)

            if player_move != "Unknown":
                ai_move = random.choice(list(gestures.keys()))
                winner_text = decide_winner(player_move, ai_move)

                # Update score if player wins
                if winner_text == "You Win!":
                    score += 1
                    score_label.config(text=f"Score: {score}")

                frozen_player_frame = ImageTk.PhotoImage(Image.fromarray(cv2.resize(rgb, (320, 240))))
                waiting_for_next = True  # Freeze until Enter pressed
                result_label.config(text=winner_text)

        player_img_display = ImageTk.PhotoImage(Image.fromarray(cv2.resize(rgb, (320, 240))))

    if ai_move:
        ai_img = gesture_images[ai_move]
    else:
        ai_img = np.ones((240, 320, 3), dtype=np.uint8) * 180
    ai_img = cv2.cvtColor(ai_img, cv2.COLOR_BGR2RGB)
    ai_img = ImageTk.PhotoImage(Image.fromarray(ai_img))

    player_label.config(image=frozen_player_frame if waiting_for_next and frozen_player_frame else player_img_display)
    player_label.image = frozen_player_frame if waiting_for_next and frozen_player_frame else player_img_display

    ai_label.config(image=ai_img)
    ai_label.image = ai_img

    round_label.config(text=f"Round {current_round} of 10")

    root.after(20, update_frame)


# ------------------ Tkinter GUI ------------------
root = tk.Tk()
root.title("Smart Stone-Paper-Scissors")
root.configure(bg=PALE_PURPLE)
root.geometry("700x550")
root.resizable(False, False)

title_label = tk.Label(root, text="SMART STONE-PAPER-SCISSORS", font=("Oswald", 24, "bold"),
                       bg=PALE_PURPLE, fg=MOUNTBATTEN_PINK)
title_label.pack(pady=10)

frame_area = tk.Frame(root, bg=PALE_PURPLE)
frame_area.pack()

ai_label = tk.Label(frame_area, bg=AI_BG)
ai_label.grid(row=0, column=0, padx=10, pady=10)

player_label = tk.Label(frame_area, bg=PLAYER_BG)
player_label.grid(row=0, column=1, padx=10, pady=10)

round_label = tk.Label(root, text="Round 1 of 10", font=("Arial", 16, "bold"), bg=PALE_PURPLE, fg=MOUNTBATTEN_PINK)
round_label.pack(pady=10)

result_label = tk.Label(root, text="", font=("Arial", 16, "bold"), bg=PALE_PURPLE, fg=MOUNTBATTEN_PINK)
result_label.pack(pady=5)

score_label = tk.Label(root, text=f"Score: {score}", font=("Arial", 16, "bold"), bg=PALE_PURPLE, fg=MOUNTBATTEN_PINK)
score_label.pack(pady=5)

footer_label = tk.Label(root, text="Made by Suraksha Jain", font=("Oswald", 10, "italic"),
                        bg=PALE_PURPLE, fg=MOUNTBATTEN_PINK)
footer_label.pack(side="bottom", pady=5)

root.bind("<Return>", start_next_round)
root.bind("<Escape>", lambda e: root.destroy())

update_frame()
root.mainloop()
cap.release()
