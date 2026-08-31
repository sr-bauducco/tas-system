#!/usr/bin/env python3
"""Generate the TAS activation chart using hours as the plotting unit.

This version follows the repository convention where raw activation data are
stored in milliseconds, but the chart is rendered in hours to match the
visual scale used in the paper and in the historical generator script.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

MS_PER_HOUR = 3_600_000.0


def ms_to_hours(value_ms: float) -> float:
    return value_ms / MS_PER_HOUR


def normalize_interval(interval_ms: Iterable[float]) -> Tuple[float, float]:
    start_ms, end_ms = interval_ms
    return (ms_to_hours(float(start_ms)), ms_to_hours(float(end_ms)))


def normalize_intervals(intervals_ms: Dict[str, List[Tuple[float, float]]]) -> Dict[str, List[Tuple[float, float]]]:
    normalized: Dict[str, List[Tuple[float, float]]] = {}
    for label, ranges in intervals_ms.items():
        normalized[label] = [normalize_interval(rng) for rng in ranges]
    return normalized


# The source workbook stores time in milliseconds. These values are converted to
# hours before plotting so the chart axis is consistent with the historical
# activation graph implementation.
intervals_ms = {
    'battery-is-low': [
        (0, 7_920_000),
        (62_280_000, 72_000_000),
    ],
    '!battery-is-low': [
        (7_920_000, 62_280_000),
    ],
    'patient-is-ok': [
        (0, 6_300_000),
        (62_280_000, 72_000_000),
    ],
    '!patient-is-ok': [
        (6_300_000, 62_280_000),
    ],
    'internet-connection': [
        (0, 7_920_000),
        (15_120_000, 54_720_000),
    ],
    '!internet-connection': [
        (7_920_000, 15_120_000),
        (54_720_000, 72_000_000),
    ],
    'doctor-is-present': [
        (0, 72_000_000),
    ],
    'drug-is-available': [
        (0, 72_000_000),
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
    'AlarmService (P3/P10)': [
        (0, 7_920_000),
        (15_120_000, 54_720_000),
    ],
    'GetSensedData (P4)': [
        (0, 72_000_000),
    ],
    'MonitorPatient (G5)': [
        (8_000_000, 62_000_000),
    ],
    'RemoteAnalysis (P6)': [
        (0, 20_000_000),
    ],
    'ProvideAutomatedLife (G2)': [
        (0, 72_000_000),
    ],
    'SendSMS (P2/P9)': [
        (0, 72_000_000),
    ],
    'LocalAnalysis (P5)': [
        (0, 72_000_000),
    ],
    'EnactTreatment (G6)': [
        (10_000_000, 54_000_000),
    ],
    'AdministerMedicine (G9)': [
        (12_000_000, 52_000_000),
    ],
    'ChangeDrug (P7)': [
        (10_000_000, 30_000_000),
    ],
    'ChangeDose (P8)': [
        (30_000_000, 50_000_000),
    ],
    'system_available': [
        (0, 72_000_000),
    ],
}

intervals_hours = normalize_intervals(intervals_ms)

# Keep the chart order consistent with the historical TAS script.
labels = [
    'battery-is-low',
    'patient-is-ok',
    'internet-connection',
    'doctor-is-present',
    'drug-is-available',
    'PushButton (P1)',
    'ProvideSelfDiagnosed (G1)',
    'ProvideHealthSupport (G0)',
    'AlarmService (P3/P10)',
    'GetSensedData (P4)',
    'MonitorPatient (G5)',
    'RemoteAnalysis (P6)',
    'ProvideAutomatedLife (G2)',
    'SendSMS (P2/P9)',
    'LocalAnalysis (P5)',
    'EnactTreatment (G6)',
    'AdministerMedicine (G9)',
    'ChangeDrug (P7)',
    'ChangeDose (P8)',
    'system_available',
]

# Requested color policy:
# - Labels from battery-is-low through drug-is-available are blue.
# - All remaining labels, except system_available, are black.
# - system_available remains green to visually mark the full system status.
colors = {
    'battery-is-low': '#1f77b4',
    'patient-is-ok': '#1f77b4',
    'internet-connection': '#1f77b4',
    'doctor-is-present': '#1f77b4',
    'drug-is-available': '#1f77b4',
    'PushButton (P1)': '#000000',
    'ProvideSelfDiagnosed (G1)': '#000000',
    'ProvideHealthSupport (G0)': '#000000',
    'AlarmService (P3/P10)': '#000000',
    'GetSensedData (P4)': '#000000',
    'MonitorPatient (G5)': '#000000',
    'RemoteAnalysis (P6)': '#000000',
    'ProvideAutomatedLife (G2)': '#000000',
    'SendSMS (P2/P9)': '#000000',
    'LocalAnalysis (P5)': '#000000',
    'EnactTreatment (G6)': '#000000',
    'AdministerMedicine (G9)': '#000000',
    'ChangeDrug (P7)': '#000000',
    'ChangeDose (P8)': '#000000',
    'system_available': '#2ca02c',
}


def plot_activation_chart(output_path: str = 'activation_chart_hours.png') -> None:
    fig, ax = plt.subplots(figsize=(16, 9))

    y_positions = list(range(len(labels)))
    y_labels = labels

    for idx, label in enumerate(y_labels):
        for start_h, end_h in intervals_hours.get(label, []):
            ax.broken_barh(
                [(start_h, end_h - start_h)],
                (idx - 0.35, 0.7),
                facecolors=colors.get(label, '#777777'),
                edgecolor='none',
                alpha=0.9,
            )

    # The red vertical lines indicate system_unavailable intervals.
    # In the TAS scenario, the system becomes unavailable at 13.0h, 15.2h, 16.2h,
    # and 17.3h, which correspond to the moments of service outage. The values
    # are expressed in hours after conversion from the original ms scale.
    for marker in [13.0, 15.2, 16.2, 17.3]:
        ax.axvline(marker, color='red', linestyle='--', linewidth=1.0, alpha=0.75)

    ax.set_yticks(y_positions)
    ax.set_yticklabels(y_labels, fontsize=9)
    ax.set_xlim(0, 20)
    ax.set_xlabel('Tempo (horas)', fontsize=12)
    ax.set_title('Ativação de componentes do TAS ao longo do tempo', fontsize=14)
    ax.grid(axis='x', linestyle='--', alpha=0.35)
    ax.invert_yaxis()

    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)

    plt.tight_layout()
    output = Path(output_path)
    fig.savefig(output, dpi=300)
    plt.close(fig)
    print(f'Chart saved to {output.resolve()}')


if __name__ == '__main__':
    plot_activation_chart('activation_chart_hours.png')
