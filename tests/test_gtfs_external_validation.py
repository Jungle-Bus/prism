import json
import subprocess
import pytest


@pytest.mark.xfail(
    reason="To run this test, you need to install https://github.com/etalab/transport-validator"
)
def test_output_gtfs_does_not_have_error(gtfs_as_zipfile):
    run_external_validator = subprocess.run(
        ["etalab_transport_validator", "-i", gtfs_as_zipfile],
        capture_output=True,
        text=True,
    )

    result = json.loads(run_external_validator.stdout)

    assert result["metadata"]["has_shapes"], "The output GTFS should contain shapes"

    gtfs_issues_types = [elem for elem in result["validations"]]
    for issue_type in gtfs_issues_types:
        gtfs_issues = [elem for elem in result["validations"][issue_type]]
        for issue in gtfs_issues:
            assert issue["severity"] not in ["Fatal", "Error"], "{} : {}".format(
                issue["issue_type"], issue["object_id"]
            )
