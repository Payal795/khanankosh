import os
import uuid
import traceback

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from chunks import index_pdf_for_rag
from pdf_to_docx import convert_pdf_to_docx
from projectsih import process_and_rewrite_document


router = APIRouter(
    prefix="/api",
    tags=["Report Generation"]
)


# ============================================================
# CONFIGURATION
# ============================================================

WORK_DIR = "./work"
CHROMA_DIR = "./chroma_db"
SQLITE_PATH = "./tables.db"
COLLECTION_NAME = "coal_ministry_docs"

os.makedirs(WORK_DIR, exist_ok=True)


# ============================================================
# REPORT GENERATION
# ============================================================

@router.post("/report")
async def generate_report(
    file: UploadFile = File(...),
    topic: str = Form(...),
    description: str = Form(""),
):

    # --------------------------------------------------------
    # Validate upload
    # --------------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided"
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    # --------------------------------------------------------
    # Create unique job directory
    # --------------------------------------------------------

    job_id = str(uuid.uuid4())

    job_dir = os.path.join(
        WORK_DIR,
        job_id
    )

    os.makedirs(
        job_dir,
        exist_ok=True
    )

    pdf_path = os.path.join(
        job_dir,
        file.filename
    )

    converted_docx_path = os.path.join(
        job_dir,
        "converted.docx"
    )

    final_output_path = os.path.join(
        job_dir,
        "final_report.docx"
    )

    print("\n")
    print("=" * 70)
    print("STARTING REPORT GENERATION")
    print("=" * 70)
    print(f"Job ID       : {job_id}")
    print(f"Input PDF    : {pdf_path}")
    print(f"Converted    : {converted_docx_path}")
    print(f"Final report : {final_output_path}")
    print(f"Topic        : {topic}")
    print(f"Description  : {description}")
    print("=" * 70)

    try:

        # ====================================================
        # STEP 1
        # SAVE UPLOADED PDF
        # ====================================================

        print("\n")
        print("=" * 60)
        print("STEP 1: SAVING PDF")
        print("=" * 60)

        file_data = await file.read()

        if not file_data:
            raise RuntimeError(
                "Uploaded PDF is empty."
            )

        with open(
            pdf_path,
            "wb"
        ) as buffer:
            buffer.write(file_data)

        print(f"PDF saved successfully.")
        print(f"Size: {len(file_data)} bytes")


        # ====================================================
        # STEP 2
        # PDF -> DOCX
        # ====================================================

        print("\n")
        print("=" * 60)
        print("STEP 2: CONVERTING PDF TO DOCX")
        print("=" * 60)

        conversion_result = convert_pdf_to_docx(
            input_path=pdf_path,
            output_path=converted_docx_path
        )

        print("Conversion result:")
        print(conversion_result)

        if not conversion_result.success:

            raise RuntimeError(
                "PDF conversion failed: "
                f"{conversion_result.error}"
            )

        if not os.path.exists(
            conversion_result.output_path
        ):

            raise RuntimeError(
                "PDF conversion reported success, "
                "but converted DOCX does not exist."
            )

        print(
            f"DOCX created successfully: "
            f"{conversion_result.output_path}"
        )


        # ====================================================
        # STEP 3
        # INDEX PDF FOR RAG
        # ====================================================

        print("\n")
        print("=" * 60)
        print("STEP 3: INDEXING PDF FOR RAG")
        print("=" * 60)

        print(f"Collection: {COLLECTION_NAME}")
        print(f"Chroma DB : {CHROMA_DIR}")
        print(f"SQLite DB : {SQLITE_PATH}")

        index_result = index_pdf_for_rag(
            pdf_path=pdf_path,
            collection_name=COLLECTION_NAME,
            persist_directory=CHROMA_DIR,
            sqlite_path=SQLITE_PATH
        )

        print("PDF indexing completed.")

        # Some implementations return a result.
        # Print it if they do.
        if index_result is not None:
            print("Index result:")
            print(index_result)


        # ====================================================
        # STEP 4
        # REWRITE DOCUMENT
        # ====================================================

        print("\n")
        print("=" * 60)
        print("STEP 4: REWRITING DOCX")
        print("=" * 60)

        print(
            f"Input DOCX : "
            f"{conversion_result.output_path}"
        )

        print(
            f"Output DOCX: "
            f"{final_output_path}"
        )

        print(
            f"Topic      : "
            f"{topic}"
        )

        print(
            f"Description: "
            f"{description}"
        )

        rewrite_result = process_and_rewrite_document(
            input_path=conversion_result.output_path,
            output_path=final_output_path,
            user_topic=topic,
            user_description=description,
        )

        print("Document rewriting completed.")

        if rewrite_result is not None:
            print("Rewrite result:")
            print(rewrite_result)


        # ====================================================
        # STEP 5
        # VERIFY FINAL FILE
        # ====================================================

        print("\n")
        print("=" * 60)
        print("STEP 5: VERIFYING FINAL REPORT")
        print("=" * 60)

        if not os.path.exists(
            final_output_path
        ):

            raise RuntimeError(
                "process_and_rewrite_document() completed, "
                "but final_report.docx was not created."
            )

        final_size = os.path.getsize(
            final_output_path
        )

        if final_size == 0:

            raise RuntimeError(
                "final_report.docx was created but is empty."
            )

        print(
            f"Final report created successfully."
        )

        print(
            f"Path: {final_output_path}"
        )

        print(
            f"Size: {final_size} bytes"
        )


        # ====================================================
        # SUCCESS
        # ====================================================

        print("\n")
        print("=" * 70)
        print("REPORT GENERATION SUCCESSFUL")
        print("=" * 70)
        print(f"Job ID: {job_id}")
        print("=" * 70)

        return {
            "status": "success",
            "job_id": job_id,
            "message": "Report generated successfully.",
            "download_url": (
                f"/api/report/download/{job_id}"
            ),
        }


    # ========================================================
    # PRESERVE INTENTIONAL HTTP ERRORS
    # ========================================================

    except HTTPException:
        raise


    # ========================================================
    # CATCH REAL UNEXPECTED ERRORS
    # ========================================================

    except Exception as e:

        print("\n")
        print("=" * 70)
        print("REPORT GENERATION FAILED")
        print("=" * 70)

        print(
            f"Exception type: {type(e).__name__}"
        )

        print(
            f"Exception message: {str(e)}"
        )

        print("\nFULL TRACEBACK:")
        print("-" * 70)

        traceback.print_exc()

        print("-" * 70)
        print("=" * 70)
        print("\n")

        raise HTTPException(
            status_code=500,
            detail=(
                f"{type(e).__name__}: {str(e)}"
            )
        )


# ============================================================
# DOWNLOAD GENERATED REPORT
# ============================================================

@router.get(
    "/report/download/{job_id}"
)
def download_report(
    job_id: str
):

    job_dir = os.path.join(
        WORK_DIR,
        job_id
    )

    # --------------------------------------------------------
    # Check job directory
    # --------------------------------------------------------

    if not os.path.exists(job_dir):

        raise HTTPException(
            status_code=404,
            detail="Report job not found"
        )

    # --------------------------------------------------------
    # Find final report
    # --------------------------------------------------------

    final_report = os.path.join(
        job_dir,
        "final_report.docx"
    )

    if not os.path.exists(final_report):

        raise HTTPException(
            status_code=404,
            detail="Generated report not found"
        )

    # --------------------------------------------------------
    # Return DOCX
    # --------------------------------------------------------

    return FileResponse(
        final_report,
        filename="final_report.docx",
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        )
    )