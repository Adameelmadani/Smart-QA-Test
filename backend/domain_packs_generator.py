"""
ReqTracer, Domain Pack Generator
Creates synthetic specification documents for demo purposes.
"""
import os
import sys


def create_automotive_avas():
    """Create Automotive AVAS (Acoustic Vehicle Alerting System) specification."""
    from docx import Document
    from docx.shared import Pt, Inches, Cm, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()

    # Style
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(11)

    # Title
    title = doc.add_heading('AVAS, Acoustic Vehicle Alerting System', level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph('Specification Document, Automotive Domain')
    doc.add_paragraph('Version 1.0 | Classification: Internal')
    doc.add_paragraph('')

    # Section 1: Scope
    doc.add_heading('1. Scope', level=1)
    doc.add_paragraph(
        'This specification defines the requirements for the Acoustic Vehicle Alerting System (AVAS) '
        'installed in electric and hybrid vehicles. The AVAS shall generate artificial sounds to alert '
        'pedestrians and other road users of the vehicle\'s presence at low speeds, in accordance with '
        'UN Regulation No. 138.'
    )

    # Section 2: Applicable Standards
    doc.add_heading('2. Applicable Standards', level=1)
    doc.add_paragraph('• UN ECE Regulation No. 138, Quiet road transport vehicles (QRTV)')
    doc.add_paragraph('• ISO 26262, Functional Safety for road vehicles')
    doc.add_paragraph('• ISO 16254, Sound level measurement of AVAS')

    # Section 3: Functional Requirements
    doc.add_heading('3. Functional Requirements', level=1)

    doc.add_heading('3.1 Sound Generation', level=2)
    doc.add_paragraph(
        'REQ-001: The AVAS shall generate a continuous sound when the vehicle speed is between 0 km/h and 20 km/h in forward gear.'
    )
    doc.add_paragraph(
        'REQ-002: The AVAS shall generate a continuous sound when the vehicle is in reverse gear, regardless of speed.'
    )
    doc.add_paragraph(
        'REQ-003: The sound frequency shall vary proportionally with vehicle speed to provide auditory cues about vehicle velocity.'
    )

    doc.add_heading('3.2 Sound Level', level=2)
    doc.add_paragraph(
        'REQ-004: The minimum sound pressure level shall be 56 dB SPL at 2 meters distance when the vehicle is stationary.'
    )
    doc.add_paragraph(
        'REQ-005: The maximum sound pressure level shall not exceed 75 dB SPL at 2 meters distance at any vehicle speed.'
    )
    doc.add_paragraph(
        'REQ-006: The sound level shall increase by at least 3 dB for every 5 km/h increase in speed between 0 and 20 km/h.'
    )

    doc.add_heading('3.3 Frequency Requirements', level=2)
    doc.add_paragraph(
        'REQ-007: The generated sound shall contain frequency components in two mandatory bands: '
        '160 Hz to 400 Hz (low band) and 800 Hz to 5000 Hz (high band).'
    )
    doc.add_paragraph(
        'REQ-008: The frequency shift between stationary and 20 km/h shall be at least one-third octave band.'
    )

    # Section 4: Performance Requirements
    doc.add_heading('4. Performance Requirements', level=1)
    doc.add_paragraph(
        'REQ-009: The AVAS shall activate within 500 ms of the vehicle entering the applicable speed range.'
    )
    doc.add_paragraph(
        'REQ-010: The sound generation latency from speed change to corresponding frequency change shall not exceed 200 ms.'
    )
    doc.add_paragraph(
        'REQ-011: The system shall operate correctly in temperature range from -40°C to +85°C.'
    )

    # Section 5: Interface Requirements
    doc.add_heading('5. Interface Requirements', level=1)
    doc.add_paragraph(
        'REQ-012: The AVAS ECU shall communicate with the vehicle CAN bus to receive speed data at minimum 100 Hz update rate.'
    )
    doc.add_paragraph(
        'REQ-013: The AVAS shall interface with the vehicle speaker system through a dedicated analog audio output (line level, 1V RMS).'
    )
    doc.add_paragraph(
        'REQ-014: The AVAS ECU shall provide a diagnostic interface via UDS protocol (ISO 14229) for fault reporting.'
    )

    # Section 6: Safety Requirements
    doc.add_heading('6. Safety Requirements', level=1)
    doc.add_paragraph(
        'REQ-015: The AVAS shall implement a fail-safe mode that generates a default alert sound if the primary sound generation fails.'
    )
    doc.add_paragraph(
        'REQ-016: The AVAS must not be deactivatable by the driver except via a temporary pause function limited to a single ignition cycle.'
    )
    doc.add_paragraph(
        'REQ-017: The system shall perform a self-diagnostic check at each ignition cycle and report faults to the vehicle diagnostic system within 2 seconds.'
    )

    # Table: Requirements Summary
    doc.add_heading('7. Requirements Summary', level=1)
    table = doc.add_table(rows=1, cols=5)
    table.style = 'Table Grid'
    headers = ['REQ-ID', 'Type', 'Priority', 'Title', 'Threshold']
    for i, h in enumerate(headers):
        table.rows[0].cells[i].text = h

    reqs_data = [
        ['REQ-001', 'Functional', 'High', 'Forward sound generation', '0-20 km/h'],
        ['REQ-002', 'Functional', 'High', 'Reverse sound generation', 'All speeds'],
        ['REQ-003', 'Functional', 'High', 'Speed-proportional frequency', 'Proportional'],
        ['REQ-004', 'Performance', 'High', 'Minimum SPL stationary', '56 dB SPL'],
        ['REQ-005', 'Performance', 'High', 'Maximum SPL limit', '75 dB SPL'],
        ['REQ-006', 'Performance', 'Medium', 'SPL increase rate', '3 dB / 5 km/h'],
        ['REQ-007', 'Performance', 'High', 'Frequency bands', '160-400 Hz, 800-5000 Hz'],
        ['REQ-008', 'Performance', 'Medium', 'Frequency shift range', '1/3 octave'],
        ['REQ-009', 'Performance', 'High', 'Activation time', '500 ms'],
        ['REQ-010', 'Performance', 'Medium', 'Latency', '200 ms'],
        ['REQ-011', 'Performance', 'High', 'Temperature range', '-40°C to +85°C'],
        ['REQ-012', 'Interface', 'High', 'CAN bus interface', '100 Hz'],
        ['REQ-013', 'Interface', 'Medium', 'Audio output', '1V RMS'],
        ['REQ-014', 'Interface', 'Medium', 'Diagnostic interface', 'UDS'],
        ['REQ-015', 'Security', 'High', 'Fail-safe mode', 'Default sound'],
        ['REQ-016', 'Security', 'High', 'Non-deactivatable', 'Ignition cycle'],
        ['REQ-017', 'Security', 'High', 'Self-diagnostic', '2 seconds'],
    ]
    for row_data in reqs_data:
        row = table.add_row()
        for i, val in enumerate(row_data):
            row.cells[i].text = val

    return doc


def create_energy_grid():
    """Create Energy Smart Grid Monitoring specification."""
    from docx import Document
    from docx.shared import Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)

    title = doc.add_heading('Smart Grid Monitoring System', level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph('Specification Document, Energy Domain')
    doc.add_paragraph('Version 1.0 | Classification: Internal')
    doc.add_paragraph('')

    doc.add_heading('1. Scope', level=1)
    doc.add_paragraph(
        'This document specifies the requirements for a Smart Grid Monitoring System (SGMS) '
        'designed to monitor electrical grid parameters in real-time, detect anomalies, and '
        'generate automated alerts for grid operators.'
    )

    doc.add_heading('2. Functional Requirements', level=1)

    doc.add_heading('2.1 Data Acquisition', level=2)
    doc.add_paragraph(
        'REQ-001: The system shall acquire voltage, current, and power measurements from each monitored node at a minimum sampling rate of 1 kHz.'
    )
    doc.add_paragraph(
        'REQ-002: The system shall support simultaneous monitoring of up to 500 grid nodes.'
    )
    doc.add_paragraph(
        'REQ-003: The system shall store measurement data for a minimum retention period of 365 days.'
    )

    doc.add_heading('2.2 Anomaly Detection', level=2)
    doc.add_paragraph(
        'REQ-004: The system shall detect voltage sags exceeding 10% of nominal voltage within 100 ms of occurrence.'
    )
    doc.add_paragraph(
        'REQ-005: The system shall detect frequency deviations greater than 0.5 Hz from the nominal 50 Hz grid frequency.'
    )
    doc.add_paragraph(
        'REQ-006: The system shall detect power factor values below 0.85 and generate a warning alert.'
    )

    doc.add_heading('2.3 Alerting', level=2)
    doc.add_paragraph(
        'REQ-007: The system shall generate real-time alerts via email and SMS within 5 seconds of anomaly detection.'
    )
    doc.add_paragraph(
        'REQ-008: The system shall classify alerts into three severity levels: Critical, Warning, and Informational.'
    )

    doc.add_heading('3. Performance Requirements', level=1)
    doc.add_paragraph(
        'REQ-009: The system data processing latency shall not exceed 50 ms from measurement to dashboard display.'
    )
    doc.add_paragraph(
        'REQ-010: The system shall maintain 99.95% uptime availability over any 30-day period.'
    )

    doc.add_heading('4. Interface Requirements', level=1)
    doc.add_paragraph(
        'REQ-011: The system shall provide a REST API for third-party integration with response time under 200 ms.'
    )
    doc.add_paragraph(
        'REQ-012: The system shall support Modbus TCP/IP and IEC 61850 communication protocols for sensor data acquisition.'
    )

    doc.add_heading('5. Security Requirements', level=1)
    doc.add_paragraph(
        'REQ-013: All data transmission between sensors and the central system shall be encrypted using TLS 1.3.'
    )
    doc.add_paragraph(
        'REQ-014: The system shall enforce role-based access control with a minimum of three roles: Operator, Engineer, and Administrator.'
    )

    return doc


def create_railway_signaling():
    """Create Railway Signaling System specification."""
    from docx import Document
    from docx.shared import Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)

    title = doc.add_heading('Railway Signaling Control System', level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph('Specification Document, Railway Domain')
    doc.add_paragraph('Version 1.0 | Classification: Internal')
    doc.add_paragraph('')

    doc.add_heading('1. Scope', level=1)
    doc.add_paragraph(
        'This specification defines the requirements for an electronic interlocking system '
        'for railway signaling, covering signal control, point management, track section monitoring, '
        'and route-setting logic. The system shall comply with CENELEC EN 50129 (SIL 4).'
    )

    doc.add_heading('2. Functional Requirements', level=1)

    doc.add_heading('2.1 Signal Control', level=2)
    doc.add_paragraph(
        'REQ-001: The system shall control three-aspect color light signals with states: Red (stop), Yellow (caution), and Green (proceed).'
    )
    doc.add_paragraph(
        'REQ-002: The system shall ensure that a signal can only display Green when the entire route ahead is clear and locked.'
    )
    doc.add_paragraph(
        'REQ-003: The system shall automatically set any signal to Red if the track section immediately ahead becomes occupied.'
    )

    doc.add_heading('2.2 Point/Switch Control', level=2)
    doc.add_paragraph(
        'REQ-004: The system shall control railway points (switches) with detection of Normal and Reverse positions.'
    )
    doc.add_paragraph(
        'REQ-005: The system shall lock points in position once a route is set and shall prevent movement until the route is released.'
    )
    doc.add_paragraph(
        'REQ-006: Point movement shall complete within 6 seconds. If detection is not confirmed within 8 seconds, the system shall declare a point failure.'
    )

    doc.add_heading('2.3 Route Setting', level=2)
    doc.add_paragraph(
        'REQ-007: The system shall support automatic route-setting from an origin signal to a destination signal.'
    )
    doc.add_paragraph(
        'REQ-008: The system must verify that all track sections in a route are unoccupied before setting the route.'
    )

    doc.add_heading('3. Performance Requirements', level=1)
    doc.add_paragraph(
        'REQ-009: The system shall process all interlocking logic within a cycle time of 500 ms maximum.'
    )
    doc.add_paragraph(
        'REQ-010: The system shall detect track occupation changes within 200 ms of an axle counter event.'
    )

    doc.add_heading('4. Safety Requirements', level=1)
    doc.add_paragraph(
        'REQ-011: The system shall implement a fail-safe design: any detected failure shall result in signals defaulting to the most restrictive aspect (Red).'
    )
    doc.add_paragraph(
        'REQ-012: The system shall prevent conflicting routes from being set simultaneously (flank protection).'
    )
    doc.add_paragraph(
        'REQ-013: The system shall maintain a safety integrity level of SIL 4 as per EN 50129, with a tolerable hazard rate of 10^-9 per hour.'
    )
    doc.add_paragraph(
        'REQ-014: All safety-critical state transitions must be logged with timestamps for audit purposes, stored for a minimum of 10 years.'
    )

    doc.add_heading('5. Interface Requirements', level=1)
    doc.add_paragraph(
        'REQ-015: The system shall interface with the traffic management system via a standardized RaSTA (Rail Safe Transport Application) protocol.'
    )
    doc.add_paragraph(
        'REQ-016: The system shall provide a local control panel interface for manual override operations in emergency situations.'
    )

    return doc


def generate_all_packs(output_dir: str):
    """Generate all domain pack documents."""
    os.makedirs(output_dir, exist_ok=True)

    packs = [
        ("automotive_avas.docx", create_automotive_avas),
        ("energy_smartgrid.docx", create_energy_grid),
        ("railway_signaling.docx", create_railway_signaling),
    ]

    for filename, creator in packs:
        filepath = os.path.join(output_dir, filename)
        doc = creator()
        doc.save(filepath)
        print(f"  Created: {filepath}")

    print(f"\nAll {len(packs)} domain packs generated in {output_dir}")


if __name__ == "__main__":
    output = os.path.join(os.path.dirname(os.path.dirname(__file__)), "domain_packs")
    generate_all_packs(output)
