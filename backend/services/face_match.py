from pathlib import Path
import os

# OpenCV 5.x dynamic ONNX support
os.environ.setdefault(
    "OPENCV_FORCE_DNN_ENGINE",
    "4"
)

import cv2
import numpy as np


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

FACE_DETECTOR_MODEL = (
    BASE_DIR
    / "models"
    / "face_detection_yunet_2026may.onnx"
)

FACE_RECOGNIZER_MODEL = (
    BASE_DIR
    / "models"
    / "face_recognition_sface_2021dec.onnx"
)


# ============================================================
# SETTINGS
# ============================================================

FACE_DETECTION_THRESHOLD = 0.85

NMS_THRESHOLD = 0.3

TOP_K = 5000


# OpenCV's SFace example threshold.
#
# Same identity:
# cosine similarity >= 0.363
#
# THIS MUST BE CALIBRATED before production deployment.

MATCH_THRESHOLD = 0.363


# ============================================================
# CHECK MODELS
# ============================================================

def check_models():

    missing = []

    if not FACE_DETECTOR_MODEL.exists():

        missing.append(
            str(FACE_DETECTOR_MODEL)
        )

    if not FACE_RECOGNIZER_MODEL.exists():

        missing.append(
            str(FACE_RECOGNIZER_MODEL)
        )

    if missing:

        raise FileNotFoundError(
            "Missing face models: "
            + ", ".join(missing)
        )


# ============================================================
# LOAD IMAGE FROM BYTES
# ============================================================

def decode_image(image_bytes: bytes):

    if not image_bytes:

        raise ValueError(
            "Image file is empty."
        )

    image_array = np.frombuffer(
        image_bytes,
        dtype=np.uint8
    )

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR
    )

    if image is None:

        raise ValueError(
            "Unable to decode image."
        )

    return image


# ============================================================
# CREATE FACE DETECTOR
# ============================================================

def create_detector():

    check_models()

    detector = cv2.FaceDetectorYN.create(

        str(FACE_DETECTOR_MODEL),

        "",

        (320, 320),

        FACE_DETECTION_THRESHOLD,

        NMS_THRESHOLD,

        TOP_K,

    )

    return detector


# ============================================================
# CREATE FACE RECOGNIZER
# ============================================================

def create_recognizer():

    check_models()

    recognizer = cv2.FaceRecognizerSF.create(

        str(FACE_RECOGNIZER_MODEL),

        ""

    )

    return recognizer


# ============================================================
# DETECT FACE
# ============================================================

def detect_single_face(
    image: np.ndarray,
    image_name: str
):

    detector = create_detector()

    height, width = image.shape[:2]


    if width < 50 or height < 50:

        raise ValueError(
            f"{image_name} is too small."
        )


    detector.setInputSize(
        (width, height)
    )


    _, faces = detector.detect(
        image
    )


    # --------------------------------------------------------
    # No faces
    # --------------------------------------------------------

    if faces is None or len(faces) == 0:

        raise ValueError(
            f"No face detected in {image_name}."
        )


    # --------------------------------------------------------
    # Multiple faces
    # --------------------------------------------------------

    if len(faces) > 1:

        raise ValueError(
            f"Multiple faces detected in {image_name}. "
            "Only one face must be visible."
        )


    face = faces[0]


    # YuNet confidence score is last value.

    confidence = float(
        face[-1]
    )


    return face, confidence


# ============================================================
# EXTRACT FACE EMBEDDING
# ============================================================

def extract_embedding(
    image: np.ndarray,
    face
):

    recognizer = create_recognizer()


    # --------------------------------------------------------
    # Align face using YuNet landmarks
    # --------------------------------------------------------

    aligned_face = recognizer.alignCrop(
        image,
        face
    )


    # --------------------------------------------------------
    # Generate SFace feature vector
    # --------------------------------------------------------

    embedding = recognizer.feature(
        aligned_face
    )


    if embedding is None:

        raise ValueError(
            "Unable to generate face embedding."
        )


    return embedding


# ============================================================
# COMPARE TWO FACES
# ============================================================

def compare_faces(
    document_bytes: bytes,
    live_bytes: bytes
):

    # --------------------------------------------------------
    # Decode both images
    # --------------------------------------------------------

    document_image = decode_image(
        document_bytes
    )

    live_image = decode_image(
        live_bytes
    )


    # --------------------------------------------------------
    # Detect face in ID document
    # --------------------------------------------------------

    document_face, document_confidence = (
        detect_single_face(

            document_image,

            "identity document"

        )
    )


    # --------------------------------------------------------
    # Detect face in live selfie
    # --------------------------------------------------------

    live_face, live_confidence = (
        detect_single_face(

            live_image,

            "live photograph"

        )
    )


    # --------------------------------------------------------
    # Create recognizer
    # --------------------------------------------------------

    recognizer = create_recognizer()


    # --------------------------------------------------------
    # Align document face
    # --------------------------------------------------------

    document_aligned = (
        recognizer.alignCrop(

            document_image,

            document_face

        )
    )


    # --------------------------------------------------------
    # Align live face
    # --------------------------------------------------------

    live_aligned = (
        recognizer.alignCrop(

            live_image,

            live_face

        )
    )


    # --------------------------------------------------------
    # Generate embeddings
    # --------------------------------------------------------

    document_embedding = (
        recognizer.feature(
            document_aligned
        )
    )


    live_embedding = (
        recognizer.feature(
            live_aligned
        )
    )


    # --------------------------------------------------------
    # Cosine similarity
    #
    # Higher = more similar.
    #
    # Maximum is approximately 1.
    # --------------------------------------------------------

    cosine_score = recognizer.match(

        document_embedding,

        live_embedding,

        cv2.FaceRecognizerSF_FR_COSINE

    )


    cosine_score = float(
        cosine_score
    )


    # --------------------------------------------------------
    # Decision
    # --------------------------------------------------------

    matched = (
        cosine_score >= MATCH_THRESHOLD
    )


    return {

        "matched": matched,

        "cosine_similarity": round(
            cosine_score,
            4
        ),

        "threshold": MATCH_THRESHOLD,

        "document_face_confidence": round(
            document_confidence,
            4
        ),

        "live_face_confidence": round(
            live_confidence,
            4
        ),

        "decision": (
            "MATCH"
            if matched
            else "NO_MATCH"
        ),

    }