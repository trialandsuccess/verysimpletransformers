import os
from pathlib import Path

from src.verysimpletransformers.drive import to_drive, from_drive
from src.verysimpletransformers.types import DummyModel

from drive_in import DriveSingleton
from drive_in.helpers import extract_google_id


def _drive_integration(file_ids: list[str]):
    # mut file_ids
    model = DummyModel()

    file_id = to_drive(model, "dummy.vst", folder="1zQoUrPpKQ7eTr4e3obwubrx1pSKun__t")
    file_ids.append(
        file_id
    )

    fp = Path("/tmp/vst") / extract_google_id(file_id)
    fp.unlink(missing_ok=True)

    assert from_drive(file_id)
    assert fp.exists()
    assert from_drive(file_id)
    fp.unlink(missing_ok=True)

    new_model = from_drive(file_id, save_to="pytest-dummy.vst")

    assert os.path.exists("pytest-dummy.vst")

    assert new_model.predict(["test"])[0][0] == model.predict(["test"])[0][0]

    # now just upload a file:
    file_ids.append(
        to_drive("pytest-dummy.vst", "dummy2.vst", folder="1zQoUrPpKQ7eTr4e3obwubrx1pSKun__t")
    )


def test_drive_with_cleanup():
    file_ids = []
    try:
        _drive_integration(file_ids)
    finally:
        # clean up local
        os.unlink("pytest-dummy.vst")

        # clean up remote
        drive = DriveSingleton()
        for file_id in file_ids:
            resource = drive.endpoint("files") / extract_google_id(file_id)
            assert drive.delete(resource).success
