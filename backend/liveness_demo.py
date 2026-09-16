from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse

from services.liveness import analyze_blink


app = FastAPI(
    title="SIH26 Liveness Test"
)


# ============================================================
# HTML PAGE
# ============================================================

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>SIH26 Liveness Test</title>

    <style>

        * {
            box-sizing: border-box;
        }

        body {
            font-family: Arial, sans-serif;
            background: #f3f4f6;
            margin: 0;
            min-height: 100vh;

            display: flex;
            align-items: center;
            justify-content: center;
        }

        .card {
            width: 650px;
            max-width: calc(100% - 40px);

            background: white;
            padding: 35px;

            border-radius: 14px;

            box-shadow:
                0 8px 30px
                rgba(0, 0, 0, 0.1);
        }

        h1 {
            margin-top: 0;
        }

        video {
            width: 100%;
            background: black;
            border-radius: 10px;

            transform: scaleX(-1);
        }

        .buttons {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }

        button {
            flex: 1;

            padding: 13px;

            border: none;
            border-radius: 7px;

            font-size: 15px;
            font-weight: 600;

            cursor: pointer;
        }

        #startButton {
            background: #2563eb;
            color: white;
        }

        #testButton {
            background: #059669;
            color: white;
        }

        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        #instruction {
            margin-top: 20px;

            padding: 15px;

            border-radius: 8px;

            background: #f3f4f6;

            text-align: center;

            font-size: 18px;
            font-weight: bold;
        }

        .success {
            background: #dcfce7 !important;
            color: #166534;
        }

        .failure {
            background: #fee2e2 !important;
            color: #991b1b;
        }

        .processing {
            background: #dbeafe !important;
            color: #1e40af;
        }

        canvas {
            display: none;
        }

    </style>

</head>


<body>

<div class="card">

    <h1>
        SIH26 Liveness Test
    </h1>

    <p>
        This page tests blink-based liveness detection
        before we connect it to user registration.
    </p>


    <video
        id="camera"
        autoplay
        playsinline
    ></video>


    <canvas id="canvas"></canvas>


    <div class="buttons">

        <button
            id="startButton"
            type="button"
        >
            Start Camera
        </button>


        <button
            id="testButton"
            type="button"
            disabled
        >
            Begin Liveness Test
        </button>

    </div>


    <div id="instruction">
        Start the camera first.
    </div>

</div>


<script>

    const camera =
        document.getElementById("camera");

    const canvas =
        document.getElementById("canvas");

    const startButton =
        document.getElementById("startButton");

    const testButton =
        document.getElementById("testButton");

    const instruction =
        document.getElementById("instruction");


    let stream = null;
    let testRunning = false;


    // ========================================================
    // SLEEP
    // ========================================================

    function sleep(milliseconds) {

        return new Promise(
            resolve => setTimeout(
                resolve,
                milliseconds
            )
        );

    }


    // ========================================================
    // START CAMERA
    // ========================================================

    async function startCamera() {

        try {

            stream =
                await navigator.mediaDevices.getUserMedia({

                    video: {

                        facingMode: "user",

                        width: {
                            ideal: 640
                        },

                        height: {
                            ideal: 480
                        }

                    },

                    audio: false

                });


            camera.srcObject = stream;


            await camera.play();


            startButton.disabled = true;
            testButton.disabled = false;


            instruction.className = "";

            instruction.innerText =
                "Camera ready. Keep your face centered and click Begin Liveness Test.";

        }

        catch (error) {

            console.error(
                "Camera error:",
                error
            );


            instruction.className =
                "failure";


            instruction.innerText =
                "Unable to access the camera. Check browser camera permissions.";

        }

    }


    // ========================================================
    // CAPTURE ONE CAMERA FRAME
    // ========================================================

    function captureFrame() {

        return new Promise((resolve) => {

            if (
                camera.videoWidth === 0 ||
                camera.videoHeight === 0
            ) {

                resolve(null);
                return;

            }


            /*
                Smaller frames are enough for face analysis
                and make uploading much faster.
            */

            canvas.width = 480;
            canvas.height = 360;


            const context =
                canvas.getContext("2d");


            /*
                Flip image to correspond to the
                mirrored webcam preview.
            */

            context.save();

            context.translate(
                canvas.width,
                0
            );

            context.scale(
                -1,
                1
            );


            context.drawImage(
                camera,
                0,
                0,
                canvas.width,
                canvas.height
            );


            context.restore();


            canvas.toBlob(

                (blob) => {

                    resolve(blob);

                },

                "image/jpeg",

                0.75

            );

        });

    }


    // ========================================================
    // CAPTURE MULTIPLE FRAMES
    // ========================================================

    async function collectFrames(
        count,
        delay
    ) {

        const frames = [];


        for (
            let i = 0;
            i < count;
            i++
        ) {

            const frame =
                await captureFrame();


            if (frame) {

                frames.push(frame);

            }


            await sleep(delay);

        }


        return frames;

    }


    // ========================================================
    // LIVENESS TEST
    // ========================================================

    async function runLivenessTest() {

        if (testRunning) {
            return;
        }


        testRunning = true;

        testButton.disabled = true;


        try {

            let allFrames = [];


            // ------------------------------------------------
            // STEP 1: Establish open eyes
            // ------------------------------------------------

            instruction.className =
                "processing";


            instruction.innerText =
                "Keep your eyes OPEN and look directly at the camera...";


            const baselineFrames =
                await collectFrames(
                    8,
                    120
                );


            allFrames =
                allFrames.concat(
                    baselineFrames
                );


            // ------------------------------------------------
            // STEP 2: Tell user to blink
            // ------------------------------------------------

            instruction.className =
                "processing";


            instruction.innerText =
                "BLINK ONCE NOW";


            /*
                Capture for about 3 seconds.

                We should see:

                eyes open
                    ↓
                eyes closed
                    ↓
                eyes open
            */

            const blinkFrames =
                await collectFrames(
                    28,
                    100
                );


            allFrames =
                allFrames.concat(
                    blinkFrames
                );


            // ------------------------------------------------
            // SEND TO FASTAPI
            // ------------------------------------------------

            instruction.className =
                "processing";


            instruction.innerText =
                "Checking liveness...";


            const formData =
                new FormData();


            allFrames.forEach(
                (frame, index) => {

                    formData.append(
                        "frames",
                        frame,
                        `frame_${index}.jpg`
                    );

                }
            );


            const response =
                await fetch(
                    "/api/liveliness/check",
                    {
                        method: "POST",
                        body: formData
                    }
                );


            const result =
                await response.json();


            console.log(
                "Liveness result:",
                result
            );


            // ------------------------------------------------
            // SERVER ERROR
            // ------------------------------------------------

            if (!response.ok) {

                throw new Error(
                    result.message ||
                    "Liveness server error."
                );

            }


            // ------------------------------------------------
            // PASSED
            // ------------------------------------------------

            if (result.passed) {

                instruction.className =
                    "success";


                instruction.innerHTML =

                    "✓ LIVENESS PASSED"

                    + "<br><br>"

                    + result.message

                    + "<br><br>"

                    + "Valid frames: "
                    + result.valid_frames

                    + " / "

                    + result.total_frames

                    + "<br>"

                    + "Strongest blink score: "

                    + (
                        result.strongest_blink ??
                        "N/A"
                    );

            }


            // ------------------------------------------------
            // FAILED
            // ------------------------------------------------

            else {

                instruction.className =
                    "failure";


                instruction.innerHTML =

                    "✗ LIVENESS FAILED"

                    + "<br><br>"

                    + result.message

                    + "<br><br>"

                    + "Valid frames: "
                    + result.valid_frames

                    + " / "

                    + result.total_frames

                    + "<br>"

                    + "Strongest blink score: "

                    + (
                        result.strongest_blink ??
                        "N/A"
                    );

            }

        }

        catch (error) {

            console.error(
                "Liveness test error:",
                error
            );


            instruction.className =
                "failure";


            instruction.innerText =
                "Liveness test failed: "
                + error.message;

        }

        finally {

            testRunning = false;

            testButton.disabled = false;

        }

    }


    // ========================================================
    // EVENTS
    // ========================================================

    startButton.addEventListener(
        "click",
        startCamera
    );


    testButton.addEventListener(
        "click",
        runLivenessTest
    );


    // Stop webcam if page closes

    window.addEventListener(
        "beforeunload",
        () => {

            if (stream) {

                stream
                    .getTracks()
                    .forEach(
                        track => track.stop()
                    );

            }

        }
    );


</script>

</body>

</html>
"""


# ============================================================
# TEST PAGE
# ============================================================

@app.get(
    "/",
    response_class=HTMLResponse
)
def home():

    return HTML_PAGE


# ============================================================
# LIVENESS CHECK API
# ============================================================

@app.post("/check")
async def check_liveness(
    frames: list[UploadFile] = File(...)
):

    # --------------------------------------------------------
    # FRAME COUNT VALIDATION
    # --------------------------------------------------------

    if len(frames) < 12:

        return JSONResponse(
            content={
                "passed": False,
                "message": "Not enough camera frames were received.",
                "valid_frames": 0,
                "total_frames": len(frames),
            },
            status_code=400
        )


    if len(frames) > 50:

        return JSONResponse(
            content={
                "passed": False,
                "message": "Too many camera frames were received.",
                "valid_frames": 0,
                "total_frames": len(frames),
            },
            status_code=400
        )


    # --------------------------------------------------------
    # READ FRAME FILES
    # --------------------------------------------------------

    frame_bytes_list = []


    for frame in frames:

        contents = await frame.read()


        # Ignore empty frames

        if not contents:
            continue


        # Maximum 1 MB per frame

        if len(contents) > 1024 * 1024:
            continue


        frame_bytes_list.append(
            contents
        )


    # --------------------------------------------------------
    # CHECK USABLE FRAME COUNT
    # --------------------------------------------------------

    if len(frame_bytes_list) < 12:

        return JSONResponse(
            content={
                "passed": False,
                "message": "Not enough usable camera frames were received.",
                "valid_frames": 0,
                "total_frames": len(frame_bytes_list),
            },
            status_code=400
        )


    # --------------------------------------------------------
    # RUN MEDIAPIPE
    # --------------------------------------------------------

    try:

        result = analyze_blink(
            frame_bytes_list
        )


        return JSONResponse(
            content=result
        )


    except Exception as error:

        print(
            "LIVENESS ERROR:",
            repr(error)
        )


        return JSONResponse(
            content={
                "passed": False,
                "message": (
                    "Liveness processing failed. "
                    "Check the Python terminal for the error."
                ),
                "valid_frames": 0,
                "total_frames": len(frame_bytes_list),
            },
            status_code=500
        )