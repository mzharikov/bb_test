import pytest
from app.processor import EventProcessor
from tests.util.file_reader import read_file


@pytest.fixture(scope="module")
def load_test_data():
    return read_file("valid_event_chain.json")


def test_successfully_updated(capsys, load_test_data):
    sport_event_id = load_test_data[0]["event_id"]
    event_processer = EventProcessor(sport_event_id)
    for event in load_test_data:
        event_processer.update(event)

    captured = capsys.readouterr()
    assert "'status': 1" in captured.out
    assert "'match_time': '92:08'" in captured.out


# Joke name, I know
def test_successfully_failed(capsys):
    event_processer = EventProcessor("0")
    event_processer.fail("test_fail_reason")

    captured = capsys.readouterr()
    assert "test_fail_reason" in captured.out


def test_incorrect_event_id(capsys, load_test_data):
    event_processer = EventProcessor("1")
    for event in load_test_data:
        event_processer.update(event)

    captured = capsys.readouterr()
    assert (
        "[ERR] Match failed due to following error: event_id_missmatch"
        in captured.out
    )


def update_with(
    test_data: dict, field: str, value: str | int, chain_index: int
) -> None:
    sport_event_id = test_data[0]["event_id"]
    event_processer = EventProcessor(sport_event_id)
    count = 0
    for event in test_data:
        if count == chain_index:
            event_processer.update({**event, field: value})
        event_processer.update(event)
        count += 1


def test_incorrect_match_time(capsys, load_test_data):
    field = "match_time"

    update_with(load_test_data, field, "0:01", 2)

    captured = capsys.readouterr()
    assert (
        f"[ERR] Match failed due to following error: events_chain_corrupted: {field} cannot decrease"
        in captured.out
    )


def test_incorrect_status(capsys, load_test_data):
    field = "status"

    update_with(load_test_data, field, "start_game", 2)

    captured = capsys.readouterr()
    assert (
        f"[ERR] Match failed due to following error: events_chain_corrupted: {field} cannot decrease"
        in captured.out
    )


def test_incorrect_game_period(capsys, load_test_data):
    field = "game_period"

    update_with(load_test_data, field, 0, 3)

    captured = capsys.readouterr()
    assert (
        f"[ERR] Match failed due to following error: events_chain_corrupted: {field} cannot decrease"
        in captured.out
    )


def test_incorrect_home_score(capsys, load_test_data):
    field = "home_score"

    update_with(load_test_data, field, 0, 4)

    captured = capsys.readouterr()
    assert (
        f"[ERR] Match failed due to following error: events_chain_corrupted: {field} cannot decrease"
        in captured.out
    )


def test_incorrect_away_score(capsys, load_test_data):
    field = "away_score"

    update_with(load_test_data, field, 0, 5)

    captured = capsys.readouterr()
    assert (
        f"[ERR] Match failed due to following error: events_chain_corrupted: {field} cannot decrease"
        in captured.out
    )
