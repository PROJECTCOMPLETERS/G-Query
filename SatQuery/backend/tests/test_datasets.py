
from bson import ObjectId
from fastapi.testclient import TestClient

from app.main import app
from app.storage.mongodb import database


client = TestClient(app)


def test_create_dataset():
    response = client.post(
        "/api/v1/datasets",
        json={
            "name": "Test Dataset",
            "dataset_type": "single",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert "dataset_id" in data
    assert data["name"] == "Test Dataset"
    assert data["dataset_type"] == "single"
    assert data["processing"]["status"] == "uploading"
    assert data["observations"] == []


def test_get_dataset():
    create_response = client.post(
        "/api/v1/datasets",
        json={
            "name": "Get Test Dataset",
            "dataset_type": "temporal",
        },
    )

    assert create_response.status_code == 201

    dataset_id = create_response.json()["dataset_id"]

    response = client.get(
        f"/api/v1/datasets/{dataset_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["dataset_id"] == dataset_id
    assert data["name"] == "Get Test Dataset"
    assert data["dataset_type"] == "temporal"
    assert data["processing"]["status"] == "uploading"
    assert data["observations"] == []


def test_list_datasets():
    create_response = client.post(
        "/api/v1/datasets",
        json={
            "name": "List Test Dataset",
            "dataset_type": "multimodal",
        },
    )

    assert create_response.status_code == 201

    response = client.get(
        "/api/v1/datasets",
        params={
            "page": 1,
            "page_size": 100,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "items" in data
    assert "page" in data
    assert "page_size" in data
    assert "total" in data

    assert data["page"] == 1
    assert data["page_size"] == 100
    assert data["total"] >= 1


def test_delete_dataset():
    create_response = client.post(
        "/api/v1/datasets",
        json={
            "name": "Delete Test Dataset",
            "dataset_type": "single",
        },
    )

    assert create_response.status_code == 201

    dataset_id = create_response.json()["dataset_id"]

    delete_response = client.delete(
        f"/api/v1/datasets/{dataset_id}"
    )

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_response = client.get(
        f"/api/v1/datasets/{dataset_id}"
    )

    assert get_response.status_code == 404

    error = get_response.json()["error"]

    assert error["code"] == "DATASET_NOT_FOUND"
    assert error["message"] == "Dataset was not found."


def test_upload_file():
    create_response = client.post(
        "/api/v1/datasets",
        json={
            "name": "Upload Test Dataset",
            "dataset_type": "single",
        },
    )

    assert create_response.status_code == 201

    dataset_id = create_response.json()["dataset_id"]

    with open("tests/sample.tif", "rb") as file:
        upload_response = client.post(
            f"/api/v1/datasets/{dataset_id}/files",
            files={
                "file": (
                    "sample.tif",
                    file,
                    "image/tiff",
                )
            },
        )

    assert upload_response.status_code == 200

    data = upload_response.json()

    assert data["dataset_id"] == dataset_id
    assert "file_id" in data
    assert data["status"] == "uploaded"


def test_get_file():
    create_response = client.post(
        "/api/v1/datasets",
        json={
            "name": "Retrieval Test Dataset",
            "dataset_type": "single",
        },
    )

    assert create_response.status_code == 201

    dataset_id = create_response.json()["dataset_id"]

    with open("tests/sample.tif", "rb") as file:
        upload_response = client.post(
            f"/api/v1/datasets/{dataset_id}/files",
            files={
                "file": (
                    "sample.tif",
                    file,
                    "image/tiff",
                )
            },
        )

    assert upload_response.status_code == 200

    file_id = upload_response.json()["file_id"]

    response = client.get(
        f"/api/v1/datasets/{dataset_id}/files/{file_id}"
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/tiff"
    assert response.headers["content-disposition"].startswith(
        'attachment; filename="sample.tif"'
    )
    assert len(response.content) > 0


def test_delete_file():
    create_response = client.post(
        "/api/v1/datasets",
        json={
            "name": "File Delete Test Dataset",
            "dataset_type": "single",
        },
    )

    assert create_response.status_code == 201

    dataset_id = create_response.json()["dataset_id"]

    with open("tests/sample.tif", "rb") as file:
        upload_response = client.post(
            f"/api/v1/datasets/{dataset_id}/files",
            files={
                "file": (
                    "sample.tif",
                    file,
                    "image/tiff",
                )
            },
        )

    assert upload_response.status_code == 200

    file_id = upload_response.json()["file_id"]

    delete_response = client.delete(
        f"/api/v1/datasets/{dataset_id}/files/{file_id}"
    )

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    dataset_response = client.get(
        f"/api/v1/datasets/{dataset_id}"
    )

    assert dataset_response.status_code == 200

    observations = dataset_response.json()["observations"]

    assert all(
        observation["file"]["file_id"] != file_id
        for observation in observations
    )

    file_response = client.get(
        f"/api/v1/datasets/{dataset_id}/files/{file_id}"
    )

    assert file_response.status_code == 404

    error = file_response.json()["error"]

    assert error["code"] == "FILE_NOT_FOUND"


def test_get_dataset_invalid_id():
    response = client.get(
        "/api/v1/datasets/not-a-valid-id"
    )

    assert response.status_code == 400

    error = response.json()["error"]

    assert error["code"] == "INVALID_DATASET_ID"
    assert error["message"] == "Invalid dataset ID."


def test_get_dataset_not_found():
    response = client.get(
        "/api/v1/datasets/507f1f77bcf86cd799439011"
    )

    assert response.status_code == 404

    error = response.json()["error"]

    assert error["code"] == "DATASET_NOT_FOUND"
    assert error["message"] == "Dataset was not found."


def test_create_dataset_validation_error():
    response = client.post(
        "/api/v1/datasets",
        json={
            "name": "",
            "dataset_type": "single",
        },
    )

    assert response.status_code == 422

    error = response.json()["error"]

    assert error["code"] == "VALIDATION_ERROR"


def test_upload_unsupported_file_type():
    create_response = client.post(
        "/api/v1/datasets",
        json={
            "name": "Unsupported File Test",
            "dataset_type": "single",
        },
    )

    assert create_response.status_code == 201

    dataset_id = create_response.json()["dataset_id"]

    upload_response = client.post(
        f"/api/v1/datasets/{dataset_id}/files",
        files={
            "file": (
                "test.txt",
                b"this is not a raster",
                "text/plain",
            )
        },
    )

    assert upload_response.status_code == 404

    error = upload_response.json()["error"]

    assert error["code"] == "UNSUPPORTED_FILE_TYPE"
    assert error["message"] == "Unsupported file type."


def test_upload_to_nonexistent_dataset():
    response = client.post(
        "/api/v1/datasets/507f1f77bcf86cd799439011/files",
        files={
            "file": (
                "sample.tif",
                b"fake data",
                "image/tiff",
            )
        },
    )

    assert response.status_code == 404

    error = response.json()["error"]

    assert error["code"] == "DATASET_NOT_FOUND"


def test_delete_dataset_removes_gridfs_files():
    create_response = client.post(
        "/api/v1/datasets",
        json={
            "name": "Dataset Storage Cleanup Test",
            "dataset_type": "single",
        },
    )

    assert create_response.status_code == 201

    dataset_id = create_response.json()["dataset_id"]

    with open("tests/sample.tif", "rb") as file:
        upload_response = client.post(
            f"/api/v1/datasets/{dataset_id}/files",
            files={
                "file": (
                    "sample.tif",
                    file,
                    "image/tiff",
                )
            },
        )

    assert upload_response.status_code == 200

    file_id = upload_response.json()["file_id"]

    file_response = client.get(
        f"/api/v1/datasets/{dataset_id}/files/{file_id}"
    )

    assert file_response.status_code == 200

    delete_response = client.delete(
        f"/api/v1/datasets/{dataset_id}"
    )

    assert delete_response.status_code == 204

    gridfs_file = database.fs.files.find_one(
        {"_id": ObjectId(file_id)}
    )

    assert gridfs_file is None

    dataset_response = client.get(
        f"/api/v1/datasets/{dataset_id}"
    )

    assert dataset_response.status_code == 404

    file_response = client.get(
        f"/api/v1/datasets/{dataset_id}/files/{file_id}"
    )

    assert file_response.status_code == 404

def test_get_file_not_found():
    create_response = client.post(
        "/api/v1/datasets",
        json={
            "name": "Missing File Test Dataset",
            "dataset_type": "single",
        },
    )

    assert create_response.status_code == 201

    dataset_id = create_response.json()["dataset_id"]

    file_id = "507f1f77bcf86cd799439011"

    response = client.get(
        f"/api/v1/datasets/{dataset_id}/files/{file_id}"
    )

    assert response.status_code == 404

    error = response.json()["error"]

    assert error["code"] == "FILE_NOT_FOUND"
    assert error["message"] == "File was not found."


def test_delete_file_not_found():
    create_response = client.post(
        "/api/v1/datasets",
        json={
            "name": "Missing Delete File Test",
            "dataset_type": "single",
        },
    )

    assert create_response.status_code == 201

    dataset_id = create_response.json()["dataset_id"]

    file_id = "507f1f77bcf86cd799439011"

    response = client.delete(
        f"/api/v1/datasets/{dataset_id}/files/{file_id}"
    )

    assert response.status_code == 404

    error = response.json()["error"]

    assert error["code"] == "FILE_NOT_FOUND"
    assert error["message"] == "File was not found."
