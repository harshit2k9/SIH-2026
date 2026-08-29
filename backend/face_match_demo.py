from fastapi import (
    FastAPI,
    UploadFile,
    File,
)

from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
)

from services.face_match import (
    compare_faces,
)


app = FastAPI(
    title="SIH26 Face Verification Demo"
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

    <title>
        SIH26 Face Verification
    </title>


    <style>

        * {
            box-sizing: border-box;
        }


        body {

            margin: 0;

            min-height: 100vh;

            display: flex;

            align-items: center;

            justify-content: center;

            background: #f3f4f6;

            font-family:
                Arial,
                sans-serif;

        }


        .card {

            width: 600px;

            max-width:
                calc(100% - 40px);

            background: white;

            padding: 35px;

            border-radius: 14px;

            box-shadow:
                0 8px 30px
                rgba(0,0,0,0.1);

        }


        h1 {
            margin-top: 0;
        }


        label {

            display: block;

            margin-top: 20px;

            margin-bottom: 8px;

            font-weight: bold;

        }


        input {

            width: 100%;

            padding: 12px;

            border:
                1px solid #d1d5db;

            border-radius: 7px;

        }


        button {

            width: 100%;

            margin-top: 25px;

            padding: 14px;

            border: none;

            border-radius: 7px;

            background: #111827;

            color: white;

            font-size: 16px;

            font-weight: bold;

            cursor: pointer;

        }


        #result {

            margin-top: 25px;

            padding: 16px;

            border-radius: 8px;

            background:
                #f3f4f6;

            text-align: center;

        }


        .success {

            background:
                #dcfce7 !important;

            color:
                #166534;

        }


        .failure {

            background:
                #fee2e2 !important;

            color:
                #991b1b;

        }


        .processing {

            background:
                #dbeafe !important;

            color:
                #1e40af;

        }


        .warning {

            margin-top: 20px;

            padding: 12px;

            border-radius: 7px;

            background:
                #fff7ed;

            color:
                #9a3412;

            font-size: 13px;

            line-height: 1.5;

        }

    </style>

</head>


<body>


<div class="card">


    <h1>
        SIH26 Face Verification
    </h1>


    <p>

        Upload two photographs to test whether
        the system believes they contain the same person.

    </p>


    <form id="faceForm">


        <label>
            Document / ID Photograph
        </label>


        <input
            type="file"
            id="documentImage"
            accept="image/*"
            required
        >


        <label>
            Live / Selfie Photograph
        </label>


        <input
            type="file"
            id="liveImage"
            accept="image/*"
            required
        >


        <button type="submit">

            Compare Faces

        </button>


    </form>


    <div id="result">

        Select two photographs.

    </div>


    <div class="warning">

        Use ordinary dummy/test photographs for now,
        not your real Aadhaar card. This is still a
        development environment.

    </div>


</div>



<script>


    const form =
        document.getElementById(
            "faceForm"
        );


    const documentInput =
        document.getElementById(
            "documentImage"
        );


    const liveInput =
        document.getElementById(
            "liveImage"
        );


    const resultBox =
        document.getElementById(
            "result"
        );


    form.addEventListener(

        "submit",

        async function(event) {


            event.preventDefault();


            if (
                documentInput.files.length === 0
                ||
                liveInput.files.length === 0
            ) {

                resultBox.className =
                    "failure";


                resultBox.innerText =
                    "Select both photographs.";


                return;

            }


            resultBox.className =
                "processing";


            resultBox.innerText =
                "Detecting and comparing faces...";


            const formData =
                new FormData();


            formData.append(

                "document_image",

                documentInput.files[0]

            );


            formData.append(

                "live_image",

                liveInput.files[0]

            );


            try {


                const response =
                    await fetch(

                        "/compare",

                        {

                            method:
                                "POST",

                            body:
                                formData

                        }

                    );


                const result =
                    await response.json();


                console.log(
                    result
                );


                if (!response.ok) {


                    resultBox.className =
                        "failure";


                    resultBox.innerText =
                        result.message
                        ||
                        "Face comparison failed.";


                    return;

                }


                if (result.matched) {


                    resultBox.className =
                        "success";


                    resultBox.innerHTML =

                        "✓ FACE MATCH"

                        + "<br><br>"

                        + "Cosine similarity: "

                        + result.cosine_similarity

                        + "<br>"

                        + "Threshold: "

                        + result.threshold

                        + "<br><br>"

                        + "Document face confidence: "

                        + result.document_face_confidence

                        + "<br>"

                        + "Live face confidence: "

                        + result.live_face_confidence;


                }


                else {


                    resultBox.className =
                        "failure";


                    resultBox.innerHTML =

                        "✗ FACE DOES NOT MATCH"

                        + "<br><br>"

                        + "Cosine similarity: "

                        + result.cosine_similarity

                        + "<br>"

                        + "Threshold: "

                        + result.threshold;

                }


            }


            catch (error) {


                console.error(
                    error
                );


                resultBox.className =
                    "failure";


                resultBox.innerText =
                    "Unable to communicate with the server.";


            }


        }

    );


</script>


</body>

</html>
"""


# ============================================================
# DEMO PAGE
# ============================================================

@app.get(
    "/",
    response_class=HTMLResponse,
)
def home():

    return HTML_PAGE


# ============================================================
# FACE COMPARISON ENDPOINT
# ============================================================

@app.post("/compare")
async def compare(

    document_image: UploadFile = File(...),

    live_image: UploadFile = File(...),

):

    # --------------------------------------------------------
    # BASIC MIME VALIDATION
    # --------------------------------------------------------

    allowed_types = {

        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/webp",

    }


    if (
        document_image.content_type
        not in allowed_types
    ):

        return JSONResponse(

            content={

                "message":
                    "Invalid document image format."

            },

            status_code=400,

        )


    if (
        live_image.content_type
        not in allowed_types
    ):

        return JSONResponse(

            content={

                "message":
                    "Invalid live image format."

            },

            status_code=400,

        )


    # --------------------------------------------------------
    # READ FILES
    # --------------------------------------------------------

    document_bytes = (
        await document_image.read()
    )


    live_bytes = (
        await live_image.read()
    )


    # Maximum 8 MB each

    if len(document_bytes) > 8 * 1024 * 1024:

        return JSONResponse(

            content={
                "message":
                    "Document image is too large."
            },

            status_code=400,

        )


    if len(live_bytes) > 8 * 1024 * 1024:

        return JSONResponse(

            content={
                "message":
                    "Live image is too large."
            },

            status_code=400,

        )


    # --------------------------------------------------------
    # FACE VERIFICATION
    # --------------------------------------------------------

    try:

        result = compare_faces(

            document_bytes,

            live_bytes,

        )


        return JSONResponse(
            content=result
        )


    except ValueError as error:


        return JSONResponse(

            content={

                "message":
                    str(error)

            },

            status_code=400,

        )


    except Exception as error:


        print(
            "FACE MATCH ERROR:",
            repr(error)
        )


        return JSONResponse(

            content={

                "message":
                    "Face comparison failed. "
                    "Check the Python terminal."

            },

            status_code=500,

        )