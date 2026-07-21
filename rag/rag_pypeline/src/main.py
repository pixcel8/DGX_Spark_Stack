import os
import sys
import io
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd

app = FastAPI(title="Open WebUI AArch64 Advanced RAG Ingestor")

# Initialize the lightweight ONNX engine for native ARM64 processing
try:
    from rapidocr_onnxruntime import RapidOCR
    ocr_engine = RapidOCR()
    print("[Success] RapidOCR engine loaded natively on AArch64.")
except Exception as e:
    print(f"Warning: RapidOCR failed to spin up: {e}", file=sys.stderr)
    ocr_engine = None


def parse_bytes_layout(file_bytes: bytes, file_name: str) -> str:
    ext = os.path.splitext(file_name)[-1].lower()
    print(f"[Processing] {file_name} (Format: {ext})")
    
    # 1. Plain Text / Markdown
    if ext in ['.txt', '.md']:
        return file_bytes.decode('utf-8', errors='ignore')
    
    # 2. Structured Tabular Data (CSV & Excel)
    elif ext in ['.csv', '.xlsx', '.xls']:
        buffer = io.BytesIO(file_bytes)
        df = pd.read_csv(buffer) if ext == '.csv' else pd.read_excel(buffer)
        rows = []
        for idx, row in df.iterrows():
            row_str = " | ".join([f"{col}: {val}" for col, val in row.items()])
            rows.append(row_str)
        return "\n".join(rows)

    # 3. SQL Source Files
    elif ext == '.sql':
        return file_bytes.decode('utf-8', errors='ignore')

    # 4. Complex Unstructured Files (Scanned PDFs, Images, Word Docs)
    elif ext in ['.pdf', '.docx', '.png', '.jpg', '.jpeg']:
        # Unstructured requires physical files to determine layout boundaries
        temp_path = f"/tmp/unstructured_{file_name}"
        with open(temp_path, "wb") as f:
            f.write(file_bytes)
            
        try:
            from unstructured.partition.auto import partition
            # 'hi_res' forces heavy structural processing on layout types
            strategy = "hi_res" if ext in ['.pdf', '.png', '.jpg', '.jpeg'] else "auto"
            elements = partition(filename=temp_path, strategy=strategy)
            
            text_outputs = []
            for element in elements:
                text = element.text
                # If a table grid was detected, capture its full HTML markup
                if hasattr(element, 'metadata') and getattr(element.metadata, 'text_as_html', None):
                    text = element.metadata.text_as_html
                text_outputs.append(text)
                
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return "\n\n".join(text_outputs)
            
        except Exception as e:
            print(f"[Fallback OCR] Unstructured layout parser hit an issue: {e}. Defaulting to RapidOCR.", file=sys.stderr)
            
            if ext in ['.png', '.jpg', '.jpeg', '.pdf'] and ocr_engine:
                try:
                    result, _ = ocr_engine(temp_path)
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    
                    if result:
                        # Extract only the text element from [coordinates, text, confidence]
                        text_lines = [line[1] for line in result if line and len(line) > 1]
                        return "\n".join(text_lines)
                    return ""
                except Exception as ocr_err:
                    print(f"[Fallback OCR Error] RapidOCR pipeline failed: {ocr_err}", file=sys.stderr)
            
            # Clean up the file path if all extraction logic breaks
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise HTTPException(status_code=500, detail=f"AArch64 High-Resolution Extraction failed: {str(e)}")

    else:
        # Graceful fallback for unidentified formats
        return file_bytes.decode('utf-8', errors='ignore')


@app.post("/bypass-parse")
async def bypass_parse(file: UploadFile = File(...)):
    """Receives binary streams from Open WebUI function filter hooks"""
    try:
        file_bytes = await file.read()
        extracted_text = parse_bytes_layout(file_bytes, file.filename)
        return {"filename": file.filename, "extracted_text": extracted_text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
