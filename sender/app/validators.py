from datetime import datetime
from pydantic import BaseModel, validator, Field
from enum import Enum
import re


class MATCH_STATUS(str, Enum):
    START_GAME = "start_game"
    GAME_PLAY = "game_play"
    GAME_END = "game_end"


class LogRecordSchema(BaseModel):
    home_fouls_penalty: int
    away_fouls_penalty: int
    home_shots: int
    away_shots: int
    home_shots_on_target: int
    away_shots_on_target: int
    home_yellow_cards: int
    away_yellow_cards: int
    home_red_cards: int
    away_red_cards: int
    home_offsides: int
    away_offsides: int
    home_corners: int
    away_corners: int
    home_possession_percent: int
    away_home_possession_percent: int
    home_tackles: int
    away_tackles: int
    home_shot_accuracy_percent: int
    away_shot_accuracy_percent: int
    home_pass_accuracy_percent: int
    away_pass_accuracy_percent: int
    ball_possessor: int
    ball_pos_x: float
    ball_pos_y: float
    ball_pos_z: float
    id: str = Field(regex=r"^\d+$")
    node_id: str = Field(regex=r"^\d+$")
    node_time: datetime
    sport_id: int
    event_id: str = Field(regex=r"^\d+$")
    time: datetime
    status: MATCH_STATUS
    home_team: str
    away_team: str
    match_time: str
    game_minute: int
    game_period: int
    home_score: int
    away_score: int
    home_fouls: int
    away_fouls: int

    @validator("match_time")
    def validate_time(cls, value):
        minute_pattern = re.compile(r"^(?:[1-9]\d{0,2}|0)$")
        second_pattern = re.compile(r"^(?:[0-5]\d)$")
        minutes, seconds = value.split(":")
        if not minute_pattern.match(minutes) or not second_pattern.match(
            seconds
        ):
            raise ValueError(
                "Invalid time format. Should be from 0:00 to 999:59"
            )
        return value

    @validator("ball_possessor", "game_period")
    def validate_pseudo_bool(cls, value):
        if value not in (0, 1):
            raise ValueError("Invalid value. Should be 0 or 1")
        return value

    @validator(
        "home_possession_percent",
        "away_home_possession_percent",
        "home_shot_accuracy_percent",
        "away_shot_accuracy_percent",
        "home_pass_accuracy_percent",
        "away_pass_accuracy_percent",
    )
    def validate_percents(cls, value):
        if value > 100 or value < 0:
            raise ValueError(
                "Not a valid percent value. Should be from 0 to 100"
            )
        return value
