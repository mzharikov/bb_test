import pytest
from pydantic import ValidationError
from app.validators import LogRecordSchema
from tests.util.file_reader import read_file


percent_fields = [
    "home_possession_percent",
    "away_home_possession_percent",
    "home_shot_accuracy_percent",
    "away_shot_accuracy_percent",
    "home_pass_accuracy_percent",
    "away_pass_accuracy_percent",
]


@pytest.fixture(scope="module")
def load_test_data():
    return read_file("single_record.json")


def test_validate_correct_input(load_test_data):
    for log_record in load_test_data:
        assert LogRecordSchema.validate(log_record)


def test_validate_incorrect_match_time_minutes_format(load_test_data):
    for log_record in load_test_data:
        log_record["match_time"] = "01:59"
        with pytest.raises(ValidationError) as validation_error:
            LogRecordSchema.validate(log_record)
        assert validation_error


def test_validate_incorrect_match_time_minutes_value(load_test_data):
    for log_record in load_test_data:
        log_record["match_time"] = "1000:59"
        with pytest.raises(ValidationError) as validation_error:
            LogRecordSchema.validate(log_record)
        assert validation_error


def test_validate_incorrect_match_time_seconds_format(load_test_data):
    for log_record in load_test_data:
        log_record["match_time"] = "1:1"
        with pytest.raises(ValidationError) as validation_error:
            LogRecordSchema.validate(log_record)
        assert validation_error


def test_validate_incorrect_match_time_seconds_value(load_test_data):
    for log_record in load_test_data:
        log_record["match_time"] = "1:60"
        with pytest.raises(ValidationError) as validation_error:
            LogRecordSchema.validate(log_record)
        assert validation_error


def test_validate_ball_possessor_incorrect_value(load_test_data):
    for log_record in load_test_data:
        log_record["ball_possessor"] = 2
        with pytest.raises(ValidationError) as validation_error:
            LogRecordSchema.validate(log_record)
        assert validation_error


def test_validate_game_period_incorrect_value(load_test_data):
    for log_record in load_test_data:
        log_record["game_period"] = 2
        with pytest.raises(ValidationError) as validation_error:
            LogRecordSchema.validate(log_record)
        assert validation_error


def test_validate_over_100_percent_values(load_test_data):
    for log_record in load_test_data:
        for field in percent_fields:
            log_record[field] = 101
            with pytest.raises(ValidationError) as validation_error:
                LogRecordSchema.validate(log_record)
            assert validation_error


def test_validate_less_than_0_percent_values(load_test_data):
    for log_record in load_test_data:
        for field in percent_fields:
            log_record[field] = -1
            with pytest.raises(ValidationError) as validation_error:
                LogRecordSchema.validate(log_record)
            assert validation_error
