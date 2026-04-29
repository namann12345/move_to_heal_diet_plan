from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import base64
import mediapipe as mp
import json
import os
from pydantic import BaseModel
from engine import SquatState, calculate_angle

app = FastAPI(title="Move To Heal AI Core")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

@app.get("/")
def read_root():
    return {"message": "AI Pose Estimation Service is running!"}

@app.websocket("/ws/pose/stream/{exercise_type}")
async def pose_stream(websocket: WebSocket, exercise_type: str):
    await websocket.accept()
    
    # Initialize state per connection
    if exercise_type.lower() == "squat":
        state_machine = SquatState()
    else:
        # Default fallback
        state_machine = SquatState()
        
    try:
        while True:
            # Receive base64 image from React
            data = await websocket.receive_text()
            
            # Decode image
            encoded_data = data.split(',')[1] if ',' in data else data
            nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                continue

            # Process with MediaPipe
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)
            
            feedback_json = {
                "status": "active",
                "rep_count": state_machine.counter,
                "feedback": [],
                "landmarks": []
            }

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                
                # Extract landmarks for JSON
                for lm in landmarks:
                    feedback_json["landmarks"].append({"x": lm.x, "y": lm.y, "z": lm.z, "visibility": lm.visibility})

                # Calculate specific angles for Squats
                try:
                    # Let's use the Left side (11: shoulder, 23: hip, 25: knee, 27: ankle)
                    hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                           landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                    knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                    ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                             landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
                    shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                    
                    knee_angle = calculate_angle(hip, knee, ankle)
                    hip_angle = calculate_angle(shoulder, hip, knee)
                    
                    # Update State Machine
                    rep_completed = state_machine.update(hip_angle, knee_angle)
                    
                    feedback_json["rep_count"] = state_machine.counter
                    feedback_json["feedback"] = state_machine.form_errors
                    
                    if rep_completed:
                        feedback_json["rep_trigger"] = True
                        
                except Exception as e:
                    feedback_json["error"] = str(e)
            else:
                feedback_json["status"] = "No human detected"

            # Send back the results
            await websocket.send_text(json.dumps(feedback_json))
            
    except WebSocketDisconnect:
        print(f"Client disconnected from {exercise_type} stream.")
    except Exception as e:
        print(f"Error: {e}")
        try:
            await websocket.close()
        except:
            pass

class ChatRequest(BaseModel):
    message: str
    profileContext: str = "TDEE: 2000, Goal: General Fitness"

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    # Mocking AI if API Key doesn't exist to ensure demo safety
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key or api_key == "YOUR_GROQ_API_KEY_HERE":
        msg_lower = req.message.lower()
        if "diet" in msg_lower or "tiffin" in msg_lower or "eat" in msg_lower:
            reply = f"Since your profile says '{req.profileContext}', I recommend a protein-rich Paneer wrap lunch with 350 kcal. Focus on a 300 kcal deficit."
        elif "form" in msg_lower or "squat" in msg_lower:
            reply = "I checked your last session logs. Make sure to keep your back straight and weight on your heels to avoid knee strain!"
        else:
            reply = "I'm FitHeal AI! I'm running in demo mode without the Groq active key. Try asking me for 'diet plans' or 'squat form tips'!"
            
        return {"reply": reply}
        
    try:
        from openai import OpenAI
        # Using the OpenAI SDK but pointing it to Groq API
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        
        system_prompt = f"""You are FitHeal AI, an elite AI health, fitness, and nutrition assistant.
        You are not a doctor. Return concise answers. No large markdown blocks. 
        USER CONTEXT: {req.profileContext}"""
        
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": req.message}
            ]
        )
        return {"reply": response.choices[0].message.content}
    except Exception as e:
        return {"reply": f"Error reaching Groq API: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
