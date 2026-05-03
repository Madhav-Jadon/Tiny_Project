import os
import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis

# ── Init InsightFace (ArcFace model, RetinaFace detector) ──────────────────
_app = None

def get_face_app():
    global _app
    if _app is None:
        _app = FaceAnalysis(
            name="buffalo_l",          # ArcFace model (best accuracy)
            providers=["CPUExecutionProvider"]
        )
        # det_size controls detection resolution — larger = finds smaller faces
        _app.prepare(ctx_id=0, det_size=(640, 640))
    return _app


# ── Build database of face encodings from face_data/ folder ───────────────
def build_encodings(face_data_dir="face_data"):
    """
    Reads each student's folder, extracts face embeddings from all their images.
    Returns: { "StudentName": [embedding1, embedding2, ...], ... }
    """
    app = get_face_app()
    database = {}

    if not os.path.exists(face_data_dir):
        raise FileNotFoundError(f"face_data directory not found: {face_data_dir}")

    for student_name in os.listdir(face_data_dir):
        student_dir = os.path.join(face_data_dir, student_name)
        if not os.path.isdir(student_dir):
            continue

        embeddings = []
        for img_file in os.listdir(student_dir):
            if not img_file.lower().endswith((".jpg", ".jpeg", ".png")):
                continue

            img_path = os.path.join(student_dir, img_file)
            img = cv2.imread(img_path)
            if img is None:
                continue

            faces = app.get(img)
            if faces:
                # Take the largest/most confident face from each registration photo
                best = max(faces, key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]))
                embeddings.append(best.normed_embedding)

        if embeddings:
            database[student_name] = embeddings

    return database


def cosine_similarity(a, b):
    return float(np.dot(a, b))  # embeddings are already L2-normalised


# ── Main recognition function ─────────────────────────────────────────────
def recognize_faces(image_path, face_data_dir="face_data", threshold=0.4):
    """
    Given a group photo path:
    1. Detects ALL faces using RetinaFace
    2. Matches each face against the student database
    3. Returns (present_list, absent_list)

    threshold: cosine similarity cutoff (0.4 is strict & accurate)
    """
    app = get_face_app()

    # Load the uploaded group photo
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image: {image_path}")

    # Upscale small images so RetinaFace detects distant faces better
    h, w = img.shape[:2]
    if max(h, w) < 1200:
        scale = 1200 / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)))

    # Build student encoding database
    database = build_encodings(face_data_dir)
    all_students = set(database.keys())

    # Detect all faces in the group photo
    detected_faces = app.get(img)

    recognized_students = set()

    for face in detected_faces:
        query_embedding = face.normed_embedding
        best_match = None
        best_score = -1

        for student_name, embeddings in database.items():
            # Compare against all stored photos of this student, take best score
            for stored_embedding in embeddings:
                score = cosine_similarity(query_embedding, stored_embedding)
                if score > best_score:
                    best_score = score
                    best_match = student_name

        if best_score >= threshold and best_match:
            recognized_students.add(best_match)

    present_list = sorted(recognized_students)
    absent_list = sorted(all_students - recognized_students)

    return present_list, absent_list