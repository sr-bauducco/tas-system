#!/usr/bin/env python3
"""Generate the TAS activation chart using hours as the plotting unit.

The repository workbook stores times in milliseconds, while the charting script
should use hours on the axis. This version converts the raw millisecond values
before building the activation intervals.
"""

from __future__ import annotations

import math
from typing import Dict, Iterable, List, Tuple

MS_PER_HOUR = 3_600_000.0


def ms_to_hours(value_ms: float) -> float:
    return value_ms / MS_PER_HOUR


def normalize_interval(interval_ms: Iterable[float]) -> Tuple[float, float]:
    a, b = interval_ms
    return (ms_to_hours(float(a)), ms_to_hours(float(b)))


def normalize_intervals(intervals_ms: Dict[str, List[Tuple[float, float]]]) -> Dict[str, List[Tuple[float, float]]]:
    normalized = {}
    for label, ranges in intervals_ms.items():
        normalized[label] = [normalize_interval(r) for r in ranges]
    return normalized


# Example based on the TAS activation data.
# These values are interpreted as milliseconds from the workbook and then
# converted to hours before plotting.
intervals_ms = {
    'battery-is-low': [
        (0, 7_920_000),
        (62_280_000, 72_000_000),
    ],
    '!battery-is-low': [
        (7_920_000, 62_280_000),
    ],
    'patient-is-ok': [
        (0, 9_000_000),
        (63_000_000, 72_000_000),
    ],
    '!patient-is-ok': [
        (9_000_000, 63_000_000),
    ],
    'internet-connection': [
        (0, 7_920_000),
        (14_760_000, 54_720_000),
    ],
    '!internet-connection': [
        (7_920_000, 14_760_000),
        (54_720_000, 72_000_000),
    ],
    'doctor-is-present': [
        (0, 72_000_000),
    ],
    '!doctor-is-present': [
        (),
    ],
    'drug-is-available': [
        (0, 72_000_000),
    ],
    '!drug-is-available': [
        (),
    ],
    'PushButton (P1)': [
        (0, 72_000_000),
    ],
    'ProvideSelfDiagnosed (G1)': [
        (0, 20_000_000),
    ],
    'ProvideHealthSupport (G0)': [
        (0, 72_000_000),
    ],
    'MonitorPatient (G5)': [
        (8_000_000, 62_000_000),
    ],
    'IntelligenceService': [
        (0, 72_000_000),
    ],
    'EnactTreatment (G6)': [
        (10_000_000, 54_000_000),
    ],
    'AdministerMedicine (G9)': [
        (12_000_000, 52_000_000),
    ],
    'system_available': [
        (0, 72_000_000),
    ],
}


# Normalized values in hours for plotting.
intervals_hours = normalize_intervals(intervals_ms)


def print_summary() -> None:
    print('Intervals normalized to hours:')
    for label, ranges in intervals_hours.items():
        if not ranges:
            print(f'{label}: []')
            continue
        formatted = [
            (round(start, 3), round(end, 3))
            for start, end in ranges
        ]
        print(f'{label}: {formatted}')


if __name__ == '__main__':
    print_summary()
