import pytest

import os

from great_expectations.exceptions import DataContextError

def test_file_kwargs_generator(data_context, filesystem_csv):
    base_dir = filesystem_csv

    datasource = data_context.add_datasource("default", "pandas", base_directory=str(base_dir))
    generator = datasource.get_generator("default")
    known_data_asset_names = datasource.get_available_data_asset_names()

    assert known_data_asset_names["default"] == set([
        "f1", "f2", "f3"
    ])

    f1_batches = [batch_kwargs for batch_kwargs in generator.get_iterator("f1")]
    assert len(f1_batches) == 1
    assert "timestamp" in f1_batches[0]
    del f1_batches[0]["timestamp"]
    assert f1_batches[0] == {
            "path": os.path.join(base_dir, "f1.csv")
        }

    f3_batches = [batch_kwargs["path"] for batch_kwargs in generator.get_iterator("f3")]
    expected_batches = [
        {
            "path": os.path.join(base_dir, "f3", "f3_20190101.csv")
        },
        {
            "path": os.path.join(base_dir, "f3", "f3_20190102.csv")
        }
    ]
    for batch in expected_batches:
        assert batch["path"] in f3_batches
    assert len(f3_batches) == 2

def test_file_kwargs_generator_error(data_context, filesystem_csv):
    base_dir = filesystem_csv
    data_context.add_datasource("default", "pandas", base_directory=str(base_dir))

    with pytest.raises(DataContextError) as exc:
        data_context.get_batch("f4")
        assert "f4" in exc.message