import face_recognition
import os
import pickle

dataset_path = "dataset"

known_encodings = []
known_names = []

print("Training started...")

for student in os.listdir(dataset_path):

    student_folder = os.path.join(dataset_path, student)

    # Skip anything that isn't a folder
    if not os.path.isdir(student_folder):
        continue

    print("Processing:", student)

    for image_name in os.listdir(student_folder):

        image_path = os.path.join(student_folder, image_name)

        # Skip anything that isn't a file
        if not os.path.isfile(image_path):
            continue

        image = face_recognition.load_image_file(image_path)

        encodings = face_recognition.face_encodings(image)

        if len(encodings) > 0:
            known_encodings.append(encodings[0])
            known_names.append(student)

    print(f"Processing {student}")

    for image_name in os.listdir(student_folder):

        image_path = os.path.join(student_folder, image_name)

        image = face_recognition.load_image_file(image_path)

        encodings = face_recognition.face_encodings(image)

        if len(encodings) > 0:

            known_encodings.append(encodings[0])

            known_names.append(student)

print("Saving model...")

with open("model/encodings.pkl", "wb") as f:

    pickle.dump(
        {
            "encodings": known_encodings,
            "names": known_names
        },
        f
    )

print("Training completed successfully!")
print("Total Faces:", len(known_names))