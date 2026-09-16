from pathlib import Path

import cv2
import numpy as np
import mediapipe as mp


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "face_landmarker.task"
)


# ============================================================
# BLINK SETTINGS
# ============================================================

# A value near 0 means eye is open.
# A value near 1 means eye is closed.

OPEN_THRESHOLD = 0.30

CLOSED_THRESHOLD = 0.55


# We want enough valid frames to make the
# liveness result meaningful.

MIN_VALID_FRAMES = 12


# ============================================================
# DECODE IMAGE
# ============================================================

def decode_image(image_bytes: bytes):

    image_array = np.frombuffer(
        image_bytes,
        dtype=np.uint8
    )

    frame = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR
    )

    if frame is None:

        raise ValueError(
            "Unable to decode image frame."
        )

    # OpenCV = BGR
    # MediaPipe = RGB

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    return rgb_frame


# ============================================================
# GET BLENDSHAPE SCORE
# ============================================================

def get_blendshape_score(
    categories,
    name: str
):

    for category in categories:

        if category.category_name == name:

            return float(
                category.score
            )

    return 0.0


# ============================================================
# ANALYZE BLINK SEQUENCE
# ============================================================

def analyze_blink(
    frame_bytes_list: list[bytes]
):

    # --------------------------------------------------------
    # Make sure the model exists
    # --------------------------------------------------------

    if not MODEL_PATH.exists():

        return {

            "passed": False,

            "message":
                "Face Landmarker model not found.",

            "valid_frames": 0,

            "total_frames":
                len(frame_bytes_list),

        }


    # --------------------------------------------------------
    # MediaPipe setup
    # --------------------------------------------------------

    BaseOptions = mp.tasks.BaseOptions

    FaceLandmarker = (
        mp.tasks.vision.FaceLandmarker
    )

    FaceLandmarkerOptions = (
        mp.tasks.vision.FaceLandmarkerOptions
    )

    RunningMode = (
        mp.tasks.vision.RunningMode
    )


    options = FaceLandmarkerOptions(

        base_options=BaseOptions(
            model_asset_path=str(
                MODEL_PATH
            )
        ),

        running_mode=RunningMode.VIDEO,

        # Detect up to 2 so that we can reject
        # frames containing multiple people.

        num_faces=2,

        min_face_detection_confidence=0.5,

        min_face_presence_confidence=0.5,

        min_tracking_confidence=0.5,

        output_face_blendshapes=True,
    )


    blink_scores = []

    valid_frames = 0

    multiple_face_frames = 0

    no_face_frames = 0


    # ========================================================
    # PROCESS FRAMES
    # ========================================================

    with FaceLandmarker.create_from_options(
        options
    ) as landmarker:


        for index, image_bytes in enumerate(
            frame_bytes_list
        ):


            # ------------------------------------------------
            # Decode browser JPEG
            # ------------------------------------------------

            try:

                rgb_frame = decode_image(
                    image_bytes
                )

            except ValueError:

                continue


            # ------------------------------------------------
            # Create MediaPipe image
            # ------------------------------------------------

            mp_image = mp.Image(

                image_format=(
                    mp.ImageFormat.SRGB
                ),

                data=rgb_frame,
            )


            # ------------------------------------------------
            # Each video frame requires an increasing
            # timestamp.
            # ------------------------------------------------

            timestamp_ms = (
                index * 100
            )


            result = (
                landmarker.detect_for_video(
                    mp_image,
                    timestamp_ms
                )
            )


            # ------------------------------------------------
            # Check detected faces
            # ------------------------------------------------

            number_of_faces = len(
                result.face_landmarks
            )


            if number_of_faces == 0:

                no_face_frames += 1

                continue


            if number_of_faces > 1:

                multiple_face_frames += 1

                continue


            # ------------------------------------------------
            # Need blendshapes for blink detection
            # ------------------------------------------------

            if not result.face_blendshapes:

                continue


            blendshapes = (
                result.face_blendshapes[0]
            )


            # ------------------------------------------------
            # Eye blink scores
            # ------------------------------------------------

            left_eye = (
                get_blendshape_score(
                    blendshapes,
                    "eyeBlinkLeft"
                )
            )


            right_eye = (
                get_blendshape_score(
                    blendshapes,
                    "eyeBlinkRight"
                )
            )


            blink_scores.append({

                "left": left_eye,

                "right": right_eye,

            })


            valid_frames += 1


    # ========================================================
    # SECURITY CHECK: MULTIPLE PEOPLE
    # ========================================================

    if multiple_face_frames > 0:

        return {

            "passed": False,

            "message":
                "Multiple faces detected. "
                "Only one person may be visible.",

            "valid_frames":
                valid_frames,

            "total_frames":
                len(frame_bytes_list),

        }


    # ========================================================
    # CHECK ENOUGH FACE FRAMES
    # ========================================================

    if valid_frames < MIN_VALID_FRAMES:

        return {

            "passed": False,

            "message":
                "Face was not visible clearly enough. "
                "Keep your face centered and try again.",

            "valid_frames":
                valid_frames,

            "total_frames":
                len(frame_bytes_list),

        }


    # ========================================================
    # BLINK STATE MACHINE
    #
    # We require:
    #
    # OPEN
    #   ↓
    # CLOSED
    #   ↓
    # OPEN
    #
    # ========================================================

    state = "WAITING_FOR_OPEN"

    open_counter = 0

    closed_counter = 0

    reopen_counter = 0


    for score in blink_scores:


        left = score["left"]

        right = score["right"]


        # Both eyes must be open

        both_open = (

            max(
                left,
                right
            )

            <= OPEN_THRESHOLD

        )


        # Both eyes must be closed

        both_closed = (

            min(
                left,
                right
            )

            >= CLOSED_THRESHOLD

        )


        # ----------------------------------------------------
        # STEP 1: Verify eyes started open
        # ----------------------------------------------------

        if state == "WAITING_FOR_OPEN":


            if both_open:

                open_counter += 1

            else:

                open_counter = 0


            if open_counter >= 2:

                state = (
                    "WAITING_FOR_BLINK"
                )


        # ----------------------------------------------------
        # STEP 2: Detect eyes closing
        # ----------------------------------------------------

        elif state == "WAITING_FOR_BLINK":


            if both_closed:

                closed_counter += 1

            else:

                closed_counter = 0


            if closed_counter >= 1:

                state = (
                    "WAITING_FOR_REOPEN"
                )


        # ----------------------------------------------------
        # STEP 3: Verify eyes reopen
        # ----------------------------------------------------

        elif state == "WAITING_FOR_REOPEN":


            if both_open:

                reopen_counter += 1

            else:

                reopen_counter = 0


            if reopen_counter >= 2:

                state = "PASSED"

                break


    # ========================================================
    # DEBUG INFORMATION
    # ========================================================

    strongest_blink = 0.0


    if blink_scores:

        strongest_blink = max(

            min(
                item["left"],
                item["right"]
            )

            for item in blink_scores

        )


    # ========================================================
    # RESULT
    # ========================================================

    if state == "PASSED":

        return {

            "passed": True,

            "message":
                "Liveness verified. Blink detected.",

            "valid_frames":
                valid_frames,

            "total_frames":
                len(frame_bytes_list),

            "strongest_blink":
                round(
                    strongest_blink,
                    3
                ),

        }


    return {

        "passed": False,

        "message":
            "Blink was not detected. "
            "Please blink slowly and try again.",

        "valid_frames":
            valid_frames,

        "total_frames":
            len(frame_bytes_list),

        "strongest_blink":
            round(
                strongest_blink,
                3
            ),

    }