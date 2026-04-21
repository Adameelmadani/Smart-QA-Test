"""
ReqTracer, Export Engine
Exports requirements and test cases to Excel and JSON formats.
"""
import json
import os
from typing import List
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from models import Requirement, TestCase


# ─── Style Constants ────────────────────────────────────────────────
HEADER_FILL = PatternFill(start_color="FF6B35", end_color="FF6B35", fill_type="solid")
HEADER_FONT = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
CELL_FONT = Font(name="Calibri", size=10)
HEADER_ALIGN = Alignment(horizontal="center", vertical="center", wrap_text=True)
CELL_ALIGN = Alignment(horizontal="left", vertical="top", wrap_text=True)
THIN_BORDER = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin")
)

# Alternating row colors
ROW_FILL_1 = PatternFill(start_color="FFF5EE", end_color="FFF5EE", fill_type="solid")
ROW_FILL_2 = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

# Type colors
TYPE_COLORS = {
    "functional": PatternFill(start_color="E8F5E9", end_color="E8F5E9", fill_type="solid"),
    "performance": PatternFill(start_color="E3F2FD", end_color="E3F2FD", fill_type="solid"),
    "interface": PatternFill(start_color="FFF3E0", end_color="FFF3E0", fill_type="solid"),
    "security": PatternFill(start_color="FCE4EC", end_color="FCE4EC", fill_type="solid"),
}

PRIORITY_COLORS = {
    "high": Font(name="Calibri", size=10, bold=True, color="D32F2F"),
    "medium": Font(name="Calibri", size=10, color="F57C00"),
    "low": Font(name="Calibri", size=10, color="388E3C"),
}


def export_excel(
    requirements: List[Requirement],
    test_cases: List[TestCase],
    output_path: str,
    doc_name: str = "Document"
) -> str:
    """Export requirements and test cases to a styled Excel file."""
    wb = Workbook()

    # ─── Sheet 1: Requirements ──────────────────────────────
    ws_req = wb.active
    ws_req.title = "Requirements"
    _write_requirements_sheet(ws_req, requirements, doc_name)

    # ─── Sheet 2: Test Cases ────────────────────────────────
    ws_tests = wb.create_sheet("Tests")
    _write_tests_sheet(ws_tests, test_cases, doc_name)

    # ─── Sheet 3: Traceability Matrix ───────────────────────
    ws_trace = wb.create_sheet("Trace")
    _write_trace_sheet(ws_trace, requirements, test_cases, doc_name)

    wb.save(output_path)
    return output_path


def _write_requirements_sheet(ws, requirements: List[Requirement], doc_name: str):
    """Write the requirements sheet."""
    # Title row
    ws.merge_cells('A1:G1')
    title_cell = ws['A1']
    title_cell.value = f"Requirements, {doc_name}"
    title_cell.font = Font(name="Calibri", size=14, bold=True, color="FF6B35")
    title_cell.alignment = Alignment(horizontal="center")
    ws.row_dimensions[1].height = 30

    # Headers
    headers = ["REQ-ID", "Title", "Type", "Priority", "Description", "Source", "Page"]
    col_widths = [12, 30, 15, 12, 50, 20, 8]

    for col, (header, width) in enumerate(zip(headers, col_widths), 1):
        cell = ws.cell(row=3, column=col, value=header)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = HEADER_ALIGN
        cell.border = THIN_BORDER
        ws.column_dimensions[chr(64 + col)].width = width

    # Data rows
    for i, req in enumerate(requirements):
        row = i + 4
        values = [req.req_id, req.title, req.req_type, req.priority,
                  req.description, req.source, req.page]
        fill = ROW_FILL_1 if i % 2 == 0 else ROW_FILL_2

        for col, value in enumerate(values, 1):
            cell = ws.cell(row=row, column=col, value=value)
            cell.font = CELL_FONT
            cell.alignment = CELL_ALIGN
            cell.border = THIN_BORDER
            cell.fill = fill

        # Color-code type column
        type_cell = ws.cell(row=row, column=3)
        if req.req_type in TYPE_COLORS:
            type_cell.fill = TYPE_COLORS[req.req_type]

        # Color-code priority
        prio_cell = ws.cell(row=row, column=4)
        if req.priority in PRIORITY_COLORS:
            prio_cell.font = PRIORITY_COLORS[req.priority]

    ws.auto_filter.ref = f"A3:G{3 + len(requirements)}"


def _write_tests_sheet(ws, test_cases: List[TestCase], doc_name: str):
    """Write the test cases sheet."""
    ws.merge_cells('A1:I1')
    title_cell = ws['A1']
    title_cell.value = f"Test Cases, {doc_name}"
    title_cell.font = Font(name="Calibri", size=14, bold=True, color="FF6B35")
    title_cell.alignment = Alignment(horizontal="center")
    ws.row_dimensions[1].height = 30

    headers = ["TC-ID", "REQ-ID", "Goal", "Prerequisites", "Procedure",
               "Inputs/Signals", "Thresholds/Oracles", "Expected Pass", "Expected Fail"]
    col_widths = [10, 10, 30, 25, 40, 25, 25, 30, 30]

    for col, (header, width) in enumerate(zip(headers, col_widths), 1):
        cell = ws.cell(row=3, column=col, value=header)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = HEADER_ALIGN
        cell.border = THIN_BORDER
        # Handle columns beyond 'I'
        ws.column_dimensions[_col_letter(col)].width = width

    for i, tc in enumerate(test_cases):
        row = i + 4
        values = [tc.tc_id, tc.req_id, tc.goal, tc.prerequisites, tc.procedure,
                  tc.inputs_signals, tc.thresholds_oracles, tc.expected_pass, tc.expected_fail]
        fill = ROW_FILL_1 if i % 2 == 0 else ROW_FILL_2

        for col, value in enumerate(values, 1):
            cell = ws.cell(row=row, column=col, value=value)
            cell.font = CELL_FONT
            cell.alignment = CELL_ALIGN
            cell.border = THIN_BORDER
            cell.fill = fill

    ws.auto_filter.ref = f"A3:{_col_letter(len(headers))}{3 + len(test_cases)}"


def _write_trace_sheet(ws, requirements: List[Requirement], test_cases: List[TestCase], doc_name: str):
    """Write the traceability matrix sheet."""
    ws.merge_cells('A1:D1')
    title_cell = ws['A1']
    title_cell.value = f"Traceability Matrix, {doc_name}"
    title_cell.font = Font(name="Calibri", size=14, bold=True, color="FF6B35")
    title_cell.alignment = Alignment(horizontal="center")
    ws.row_dimensions[1].height = 30

    headers = ["REQ-ID", "Requirement Title", "TC-IDs", "Coverage"]
    col_widths = [12, 40, 30, 15]

    for col, (header, width) in enumerate(zip(headers, col_widths), 1):
        cell = ws.cell(row=3, column=col, value=header)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = HEADER_ALIGN
        cell.border = THIN_BORDER
        ws.column_dimensions[chr(64 + col)].width = width

    # Build trace map
    trace_map = {}
    for tc in test_cases:
        if tc.req_id not in trace_map:
            trace_map[tc.req_id] = []
        trace_map[tc.req_id].append(tc.tc_id)

    for i, req in enumerate(requirements):
        row = i + 4
        tc_ids = trace_map.get(req.req_id, [])
        coverage = "Covered" if tc_ids else "Not Covered"
        fill = ROW_FILL_1 if i % 2 == 0 else ROW_FILL_2

        values = [req.req_id, req.title, ", ".join(tc_ids), coverage]
        for col, value in enumerate(values, 1):
            cell = ws.cell(row=row, column=col, value=value)
            cell.font = CELL_FONT
            cell.alignment = CELL_ALIGN
            cell.border = THIN_BORDER
            cell.fill = fill

        # Color coverage
        cov_cell = ws.cell(row=row, column=4)
        if coverage == "Covered":
            cov_cell.fill = PatternFill(start_color="C8E6C9", end_color="C8E6C9", fill_type="solid")
            cov_cell.font = Font(name="Calibri", size=10, bold=True, color="2E7D32")
        else:
            cov_cell.fill = PatternFill(start_color="FFCDD2", end_color="FFCDD2", fill_type="solid")
            cov_cell.font = Font(name="Calibri", size=10, bold=True, color="C62828")


def _col_letter(col_num: int) -> str:
    """Convert 1-based column number to Excel letter."""
    result = ""
    while col_num > 0:
        col_num, remainder = divmod(col_num - 1, 26)
        result = chr(65 + remainder) + result
    return result


# ─── JSON Export ────────────────────────────────────────────────────
def export_json(
    requirements: List[Requirement],
    test_cases: List[TestCase],
    output_path: str,
    doc_name: str = "Document"
) -> str:
    """Export requirements and test cases to structured JSON."""
    # Build trace map
    trace_map = {}
    for tc in test_cases:
        if tc.req_id not in trace_map:
            trace_map[tc.req_id] = []
        trace_map[tc.req_id].append(tc.tc_id)

    data = {
        "document": doc_name,
        "summary": {
            "total_requirements": len(requirements),
            "total_test_cases": len(test_cases),
            "coverage": f"{sum(1 for r in requirements if r.req_id in trace_map)}/{len(requirements)}"
        },
        "requirements": [r.to_dict() for r in requirements],
        "test_cases": [tc.to_dict() for tc in test_cases],
        "traceability": [
            {
                "req_id": req.req_id,
                "req_title": req.title,
                "test_cases": trace_map.get(req.req_id, []),
                "covered": req.req_id in trace_map
            }
            for req in requirements
        ]
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return output_path
