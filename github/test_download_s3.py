"""
make sure we can download a file on demand
"""
import resources as r
import pyjq
import pytest



@pytest.mark.github_org
@pytest.mark.rationale(
        """
Sanity check for early development
- can we still retrieve the file
- can we still parse the file
- is the data of a size and format we expect
"""
)
@pytest.mark.parametrize(
        "org,date",
        [(r.cur_org(), r.report_date()),],
)
def test_valid_org_file(org, date):
    # all the checks to see if we have sane input before proceeding
    org_data = r.get_data_for_org(org, date)
    assert len(org_data) > 200_000
    assert isinstance(org_data, str)
    # decoding is a pain, as we have one text line per JSON object, thus
    # we have to decode line by line
    org_json = r.parse_data_to_json(org_data)
    assert isinstance(org_json, list)


@pytest.mark.github_org
@pytest.mark.rationale(
        """
Sanity check for early development
- can we still retrieve the secondary files
- can we still parse the file
- is the data of a size and format we expect
"""
)
@pytest.mark.parametrize(
        "file_name",
        r.aux_files.values(),
)
def test_valid_aux_file(file_name):
    data = r.get_data_from_file(file_name)
    assert len(data) < 200_000
    assert isinstance(data, str)
    # decoding is a pain, as we have one text line per JSON object, thus
    # we have to decode line by line
    decoded = r.parse_data_to_json(data)
    assert isinstance(decoded, list)


@pytest.mark.github_org
@pytest.mark.rationale(
        """
Sanity check for early development
- is the pyjq module working okay (has binary files)
"""
)
@pytest.mark.parametrize(
        "file_name",
        [r.aux_files["repos_of_interest"],]
)
def test_pyjq_working(file_name):
    decoded = r.get_json_from_file(file_name)
    data = pyjq.all(".[] | .repo", decoded)
    assert len(data) > 2
    assert isinstance(data[0], str)
