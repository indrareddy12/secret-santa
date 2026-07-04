import os
import subprocess
import tempfile
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from secret_santa import (
    BacktrackingSecretSantaAssigner,
    CSVEmployeeReader,
    CSVPreviousAssignmentReader,
    CSVAssignmentWriter,
    SecretSantaError,
)

app = FastAPI(title="Secret Santa Full-Stack Service")

# Locate static directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Mount static files under /static
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

# Serve index.html at root
@app.get("/", response_class=HTMLResponse)
def serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Secret Santa App</h1><p>Static files are not ready yet.</p>")

@app.post("/api/assign")
async def assign_secret_santa(
    employees_file: UploadFile = File(...),
    previous_file: Optional[UploadFile] = File(None),
    seed: Optional[str] = Form(None)
):
    temp_emp_path = None
    temp_prev_path = None
    temp_out_path = None

    try:
        # Save employees to a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="wb") as f:
            f.write(await employees_file.read())
            temp_emp_path = f.name

        # Save previous assignments to a temp file if provided
        if previous_file and previous_file.filename:
            content = await previous_file.read()
            if content.strip():
                with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="wb") as f:
                    f.write(content)
                    temp_prev_path = f.name

        # Convert seed to integer if valid
        parsed_seed: Optional[int] = None
        if seed and seed.strip():
            try:
                parsed_seed = int(seed)
            except ValueError:
                raise HTTPException(status_code=400, detail="Seed must be an integer value")

        # Run Secret Santa Engine
        employee_reader = CSVEmployeeReader(temp_emp_path)
        previous_reader = CSVPreviousAssignmentReader(temp_prev_path)

        employees = employee_reader.read()
        previous_assignments = previous_reader.read()

        assigner = BacktrackingSecretSantaAssigner(random_seed=parsed_seed)
        assignments = assigner.assign(employees, previous_assignments)

        # Write output to temporary file to generate CSV string
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w", newline="", encoding="utf-8") as f:
            temp_out_path = f.name

        writer = CSVAssignmentWriter(temp_out_path)
        writer.write(assignments)

        # Read the generated CSV content
        with open(temp_out_path, "r", encoding="utf-8-sig") as f:
            csv_content = f.read()

        # Build detailed JSON response for the frontend UI
        assignments_list = []
        for a in assignments:
            assignments_list.append({
                "giver_name": a.giver.name,
                "giver_email": a.giver.email,
                "child_name": a.child.name,
                "child_email": a.child.email
            })

        return {
            "success": True,
            "assignments": assignments_list,
            "csv": csv_content
        }

    except SecretSantaError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(exc)}")
    finally:
        # Clean up temp files
        for path in [temp_emp_path, temp_prev_path, temp_out_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass

@app.post("/api/run-tests")
def run_tests():
    try:
        # Run pytest inside the secret-santa directory
        result = subprocess.run(
            ["python", "-m", "pytest", "-v"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to execute tests: {str(exc)}")

# Mount static directory last so the root path is prioritized
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web_app:app", host="127.0.0.1", port=8085, reload=True)
