"""
ReqTracer, Test Case Generator
Generates structured test cases from requirements with traceability.
"""
import re
from typing import List
from models import Requirement, TestCase


def generate_test_cases(requirements: List[Requirement]) -> List[TestCase]:
    """Generate test cases from a list of requirements."""
    test_cases: List[TestCase] = []
    tc_counter = 1

    for req in requirements:
        # Generate 1-2 test cases per requirement depending on complexity
        cases = _generate_cases_for_requirement(req, tc_counter)
        test_cases.extend(cases)
        tc_counter += len(cases)

    return test_cases


def _generate_cases_for_requirement(req: Requirement, start_id: int) -> List[TestCase]:
    """Generate test case(s) for a single requirement."""
    cases = []

    # Main positive test case
    tc = _create_positive_test(req, start_id)
    cases.append(tc)

    # For performance/security requirements, add a boundary/negative test
    if req.req_type in ("performance", "security"):
        tc_neg = _create_boundary_test(req, start_id + 1)
        cases.append(tc_neg)

    return cases


def _create_positive_test(req: Requirement, tc_id_num: int) -> TestCase:
    """Create a positive/nominal test case."""
    desc = req.description.lower()

    # Extract thresholds if present
    thresholds = _extract_thresholds(req.description)
    inputs = _extract_inputs(req.description)

    # Build procedure based on requirement type
    if req.req_type == "performance":
        procedure = _perf_procedure(req)
    elif req.req_type == "security":
        procedure = _security_procedure(req)
    elif req.req_type == "interface":
        procedure = _interface_procedure(req)
    else:
        procedure = _functional_procedure(req)

    goal = f"Verify that {req.title}"
    prerequisites = _generate_prerequisites(req)

    return TestCase(
        tc_id=f"TC-{tc_id_num:03d}",
        req_id=req.req_id,
        goal=goal,
        prerequisites=prerequisites,
        procedure=procedure,
        inputs_signals=inputs or "Nominal operating conditions",
        thresholds_oracles=thresholds or "As specified in requirement",
        expected_pass=_generate_pass_criteria(req),
        expected_fail=_generate_fail_criteria(req)
    )


def _create_boundary_test(req: Requirement, tc_id_num: int) -> TestCase:
    """Create a boundary/negative test case."""
    goal = f"Verify boundary/failure behavior for {req.title}"
    prerequisites = _generate_prerequisites(req)
    thresholds = _extract_thresholds(req.description)

    if req.req_type == "performance":
        procedure = (
            "1. Set up system in nominal conditions.\n"
            "2. Apply input values at specification boundary limits.\n"
            "3. Exceed specification thresholds progressively.\n"
            "4. Record system response at each step.\n"
            "5. Verify graceful degradation or proper error handling."
        )
        inputs = "Boundary and out-of-range values"
        expected_pass = "System handles boundary conditions correctly; no crash or undefined behavior"
        expected_fail = "System crashes, produces incorrect output, or fails silently at boundary"
    elif req.req_type == "security":
        procedure = (
            "1. Attempt unauthorized access to the protected function.\n"
            "2. Provide invalid credentials or tokens.\n"
            "3. Attempt injection or bypass attacks.\n"
            "4. Verify all access attempts are logged.\n"
            "5. Confirm system remains in safe state."
        )
        inputs = "Invalid credentials, malformed tokens, injection payloads"
        expected_pass = "All unauthorized attempts are blocked and logged"
        expected_fail = "Unauthorized access is granted or attack is not logged"
    else:
        procedure = (
            "1. Set up system in nominal conditions.\n"
            "2. Apply boundary or invalid inputs.\n"
            "3. Verify system handles edge cases correctly."
        )
        inputs = "Edge case and invalid values"
        expected_pass = "System handles edge cases properly"
        expected_fail = "System fails to handle edge cases"

    return TestCase(
        tc_id=f"TC-{tc_id_num:03d}",
        req_id=req.req_id,
        goal=goal,
        prerequisites=prerequisites,
        procedure=procedure,
        inputs_signals=inputs,
        thresholds_oracles=thresholds or "Boundary values of specification",
        expected_pass=expected_pass,
        expected_fail=expected_fail
    )


# ─── Procedure Generators ──────────────────────────────────────────
def _functional_procedure(req: Requirement) -> str:
    desc = req.description
    steps = [
        "1. Set up the system under test (SUT) in initial conditions.",
        "2. Configure the SUT according to requirement preconditions.",
        f"3. Execute the functionality: {_extract_action(desc)}.",
        "4. Observe and record the system response.",
        "5. Compare actual behavior against expected behavior from specification."
    ]
    return "\n".join(steps)


def _perf_procedure(req: Requirement) -> str:
    thresholds = _extract_thresholds(req.description)
    steps = [
        "1. Set up the system under test with measurement instruments.",
        "2. Establish nominal operating conditions.",
        f"3. Execute the performance scenario: {_extract_action(req.description)}.",
        f"4. Measure and record values against thresholds: {thresholds}.",
        "5. Repeat measurement 3 times for statistical validity.",
        "6. Calculate mean and verify against specification limits."
    ]
    return "\n".join(steps)


def _security_procedure(req: Requirement) -> str:
    steps = [
        "1. Set up the system in secured operational mode.",
        "2. Prepare valid and invalid authentication credentials.",
        f"3. Test security function: {_extract_action(req.description)}.",
        "4. Verify access control is enforced correctly.",
        "5. Check audit logs for proper event recording.",
        "6. Verify no information leakage occurs."
    ]
    return "\n".join(steps)


def _interface_procedure(req: Requirement) -> str:
    steps = [
        "1. Set up both communicating systems/components.",
        "2. Configure interface parameters as per specification.",
        f"3. Initiate communication: {_extract_action(req.description)}.",
        "4. Send test data through the interface.",
        "5. Verify data integrity and format at receiving end.",
        "6. Measure timing/latency if applicable."
    ]
    return "\n".join(steps)


# ─── Helpers ────────────────────────────────────────────────────────
def _extract_thresholds(text: str) -> str:
    """Extract numeric thresholds from requirement text."""
    # Find patterns like "X dB", "X Hz", "X ms", "X%", etc.
    patterns = re.findall(
        r'(\d+(?:\.\d+)?)\s*(?:dB|Hz|kHz|MHz|ms|s|sec|%|V|A|W|°C|km/h|mph|m/s|mm|cm|m)',
        text, re.IGNORECASE
    )
    if patterns:
        # Reconstruct with units
        thresholds = re.findall(
            r'\d+(?:\.\d+)?\s*(?:dB|Hz|kHz|MHz|ms|s|sec|%|V|A|W|°C|km/h|mph|m/s|mm|cm|m)(?:\s*(?:SPL|RMS|peak|min|max))?',
            text, re.IGNORECASE
        )
        return "; ".join(thresholds[:5]) if thresholds else ""

    # Check for ranges
    ranges = re.findall(r'(?:between|from)\s+(\d+)\s*(?:to|and|-)\s*(\d+)', text, re.IGNORECASE)
    if ranges:
        return "; ".join([f"{a} to {b}" for a, b in ranges])

    return ""


def _extract_inputs(text: str) -> str:
    """Extract input signals/conditions from requirement text."""
    lower = text.lower()

    inputs = []
    # Look for speed/velocity
    speed = re.findall(r'\d+(?:\.\d+)?\s*(?:km/h|mph|m/s)', text, re.IGNORECASE)
    if speed:
        inputs.append(f"Speed: {', '.join(speed)}")

    # Look for frequency
    freq = re.findall(r'\d+(?:\.\d+)?\s*(?:Hz|kHz|MHz)', text, re.IGNORECASE)
    if freq:
        inputs.append(f"Frequency: {', '.join(freq)}")

    # Look for voltage/current
    elec = re.findall(r'\d+(?:\.\d+)?\s*(?:V|A|W)', text, re.IGNORECASE)
    if elec:
        inputs.append(f"Electrical: {', '.join(elec)}")

    # Look for temperature
    temp = re.findall(r'\d+(?:\.\d+)?\s*°?C', text, re.IGNORECASE)
    if temp:
        inputs.append(f"Temperature: {', '.join(temp)}")

    return "; ".join(inputs) if inputs else ""


def _extract_action(text: str) -> str:
    """Extract the main action/verb phrase from a requirement."""
    # Try to find "shall <verb>" pattern
    match = re.search(r'shall\s+(.{10,60}?)(?:\.|,|;|$)', text, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    match = re.search(r'must\s+(.{10,60}?)(?:\.|,|;|$)', text, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Fallback: first 60 chars
    clean = text.strip()
    if len(clean) > 60:
        return clean[:57] + "..."
    return clean


def _generate_prerequisites(req: Requirement) -> str:
    """Generate prerequisites based on requirement type."""
    base = "System under test is powered and initialized."

    type_prereqs = {
        "performance": f"{base} Measurement instruments calibrated and connected.",
        "security": f"{base} Authentication system configured. Test credentials prepared.",
        "interface": f"{base} All interface connections established. Protocol configured.",
        "functional": f"{base} All dependent subsystems operational."
    }

    return type_prereqs.get(req.req_type, base)


def _generate_pass_criteria(req: Requirement) -> str:
    """Generate pass criteria from requirement."""
    thresholds = _extract_thresholds(req.description)
    action = _extract_action(req.description)

    if thresholds:
        return f"System correctly performs: {action}. Measured values within specification: {thresholds}."
    return f"System correctly performs: {action}. Behavior matches requirement specification."


def _generate_fail_criteria(req: Requirement) -> str:
    """Generate fail criteria from requirement."""
    thresholds = _extract_thresholds(req.description)

    if thresholds:
        return f"Measured values outside specification limits ({thresholds}) OR system does not respond as expected."
    return "System does not perform as specified OR produces unexpected behavior/errors."
