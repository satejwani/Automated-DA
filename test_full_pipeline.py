import requests
import time
from pathlib import Path

API_URL = "http://127.0.0.1:8000/api"
sample_dir = Path("d:/Automate DA/samples")

def test_pipeline():
    print("--- 1. Testing GET /dashboard/stats ---")
    res = requests.get(f"{API_URL}/dashboard/stats")
    print("Initial Stats:", res.json())
    assert res.status_code == 200

    print("\n--- 2. Uploading CSV Dataset ---")
    csv_path = sample_dir / "sample_sales_data.csv"
    with open(csv_path, "rb") as f:
        res = requests.post(f"{API_URL}/upload", files={"file": (csv_path.name, f, "text/csv")})
    print("Upload Response:", res.status_code)
    dataset = res.json()
    dataset_id = dataset["id"]
    print(f"Uploaded Dataset ID #{dataset_id}: {dataset['original_filename']} ({dataset['row_count']} rows, {dataset['column_count']} cols)")
    assert res.status_code == 201

    print("\n--- 3. Running Automated Analysis ---")
    res = requests.post(f"{API_URL}/analyze/{dataset_id}")
    assert res.status_code == 201
    analysis = res.json()
    print(f"Analysis Complete! Quality Score: {analysis['quality_score']}%")
    print("Data Quality Summary:", analysis['data_quality_json'])

    print("\n--- 4. Fetching Generated Charts ---")
    res = requests.get(f"{API_URL}/charts/{dataset_id}")
    assert res.status_code == 200
    charts = res.json()
    print(f"Generated {len(charts)} chart(s):")
    for c in charts:
        print(f"  - [{c['chart_type']}] {c['chart_title']} -> {c['storage_path']}")

    print("\n--- 5. Generating ReportLab PDF Report ---")
    res = requests.post(f"{API_URL}/report/{dataset_id}")
    assert res.status_code == 201
    report = res.json()
    print(f"PDF Report Generated! Title: {report['report_title']}, File Size: {report['file_size_bytes']} bytes")

    print("\n--- 6. Verifying Downloadable PDF Endpoint ---")
    res = requests.get(f"{API_URL}/report/{dataset_id}/download")
    assert res.status_code == 200
    assert len(res.content) > 1000
    print(f"Downloaded PDF Bytes Received: {len(res.content)} bytes.")

    print("\n--- 7. Updated Dashboard Stats ---")
    res = requests.get(f"{API_URL}/dashboard/stats")
    print("Updated Stats:", res.json())

    print("\n--- ALL PIPELINE TESTS PASSED SUCCESSFULLY! ---")

if __name__ == "__main__":
    test_pipeline()
