import cv2
import os
import sys


# Enter student's roll number
roll = sys.argv[1]

# Create folder for the student
folder = f"dataset/{roll}"

if not os.path.exists(folder):
    os.makedirs(folder)

camera = cv2.VideoCapture(0)

face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

count = 0

print("Press 'q' to quit.")

while True:

    ret, frame = camera.read()

    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.3,
        minNeighbors=5
    )

    for (x, y, w, h) in faces:

        count += 1

        face = frame[y:y+h, x:x+w]

        filename = os.path.join(folder, f"{count}.jpg")

        cv2.imwrite(filename, face)

        cv2.rectangle(
            frame,
            (x, y),
            (x+w, y+h),
            (0,255,0),
            2
        )

        cv2.putText(
            frame,
            f"Images: {count}",
            (10,30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255,0,0),
            2
        )

    cv2.imshow("Capture Faces", frame)

    if cv2.waitKey(1) == ord('q') or count >= 30:
        break

camera.release()
cv2.destroyAllWindows()

print("Face images captured successfully.")