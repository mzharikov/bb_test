from enum import Enum


class STATUS(Enum):
    PREMATCH = 0
    LIVE = 1
    ENDED = 2
    FAILED = 3


class MATCH_STATUS(Enum):
    PREMATCH = 0
    FIRST_HALF = 1
    SECOND_HALF = 2
    ENDED = 3


class EventProcessor:
    __status_incoming_to_internal = {
        "start_game": STATUS.PREMATCH,
        "game_play": STATUS.LIVE,
        "game_end": STATUS.ENDED,
    }

    def __init__(self, sport_event_id: str):
        self.sport_event_id = sport_event_id
        self.__status = STATUS.PREMATCH
        self.__prev_status = STATUS.PREMATCH
        self.__match_status = MATCH_STATUS.PREMATCH
        self.__match_time = 0
        self.__fail_reason = ""
        self.__period = 0
        self.__home_score = 0
        self.__away_score = 0
        self.__first_period_home_score = 0
        self.__first_period_away_score = 0
        self.__second_period_home_score = 0
        self.__second_period_away_score = 0

    @classmethod
    def __convert_time_to_int(cls, match_time: str) -> int:
        match_minutes, match_seconds = match_time.split(":")
        return int(match_minutes) * 60 + int(match_seconds)

    @classmethod
    def __convert_time_to_str(cls, match_time: int) -> str:
        minutes, seconds = divmod(match_time, 60)
        return f"{minutes}:{seconds:02d}"

    def __validate(self, new_event: dict):
        if self.sport_event_id != new_event["event_id"]:
            self.fail("event_id_missmatch")
        elif (
            self.__convert_time_to_int(new_event["match_time"])
            < self.__match_time
        ):
            self.__validation_fail("match_time")
        elif new_event["game_period"] < self.__period:
            self.__validation_fail("game_period")
        elif new_event["home_score"] < self.__home_score:
            self.__validation_fail("home_score")
        elif new_event["away_score"] < self.__away_score:
            self.__validation_fail("away_score")
        elif (
            EventProcessor.__status_incoming_to_internal[
                new_event["status"]
            ].value
            < self.__status.value
        ):
            self.__validation_fail("status")

    def __validation_fail(self, field: str):
        self.fail(f"events_chain_corrupted: {field} cannot decrease")

    def __serialize(self) -> dict:
        status_to_log = (
            self.__status
            if self.__status != STATUS.FAILED
            else self.__prev_status
        )

        return {
            "match_state": {
                "status": status_to_log.value,
                "match_status": self.__match_status.value,
                "match_time": self.__convert_time_to_str(self.__match_time),
            },
            "match_score": {
                "score": {
                    "home_score": self.__home_score,
                    "away_score": self.__away_score,
                },
                "period_scores": [
                    {
                        "number": 1,
                        "home_score": self.__first_period_home_score,
                        "away_score": self.__first_period_away_score,
                    },
                    {
                        "number": 2,
                        "home_score": self.__second_period_home_score,
                        "away_score": self.__second_period_away_score,
                    },
                ],
            },
        }

    def __log_state(self):
        print(self.__serialize())

    def __log_error(self):
        print(
            f"[ERR] Match failed due to following error: {self.__fail_reason}"
        )
        print("Last correct state was: ")
        self.__log_state()
        print("Press Ctrl+C to exit...")

    def get_status(self) -> int:
        return self.__status.value

    def update(self, new_event: dict):
        if self.__status != STATUS.FAILED:
            self.__validate(new_event)

        if self.__status == STATUS.FAILED:
            return

        self.__period = new_event["game_period"]
        self.__status = EventProcessor.__status_incoming_to_internal[
            new_event["status"]
        ]

        if (
            EventProcessor.__status_incoming_to_internal[new_event["status"]]
            == STATUS.LIVE
        ):
            if self.__period == 0:
                self.__match_status = MATCH_STATUS.FIRST_HALF
            else:
                self.__match_status = MATCH_STATUS.SECOND_HALF
        else:
            self.__match_status = EventProcessor.__status_incoming_to_internal[
                new_event["status"]
            ]

        self.__match_time = self.__convert_time_to_int(new_event["match_time"])

        self.__home_score = new_event["home_score"]
        self.__away_score = new_event["away_score"]

        if self.__period == 0:
            self.__first_period_home_score = self.__home_score
            self.__first_period_away_score = self.__away_score
        else:
            self.__second_period_home_score = self.__home_score
            self.__second_period_away_score = self.__away_score

        self.__log_state()

    def fail(self, reason: str):
        self.__prev_status = self.__status
        self.__status = STATUS.FAILED
        self.__fail_reason = reason
        self.__log_error()
