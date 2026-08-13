from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DemoOption:
    id: str
    name: str
    description: str


@dataclass(frozen=True)
class Demo:
    id: str
    name: str
    description: str
    options: tuple[DemoOption, ...]


# Placeholder catalog — persona roster and dataset options are finalized in
# the cycles that build each demo's actual logic.
DEMOS: tuple[Demo, ...] = (
    Demo(
        id="opendemo",
        name="Open Day Q&A",
        description=(
            "Ask Furhat about courses, curriculum, and the School of Computing and "
            "Information Systems."
        ),
        options=(
            DemoOption(
                id="guide",
                name="Course Guide",
                description="General Open Day and curriculum questions.",
            ),
        ),
    ),
    Demo(
        id="facevis",
        name="FaceVis",
        description="See how Furhat's face can visualize live Melbourne/Victoria data.",
        options=(
            DemoOption(
                id="air-quality",
                name="Air Quality",
                description="Visualize live air quality data on Furhat's face.",
            ),
        ),
    ),
)


def find_demo(demo_id: str) -> Demo | None:
    return next((demo for demo in DEMOS if demo.id == demo_id), None)


def find_option(demo: Demo, option_id: str) -> DemoOption | None:
    return next((option for option in demo.options if option.id == option_id), None)
