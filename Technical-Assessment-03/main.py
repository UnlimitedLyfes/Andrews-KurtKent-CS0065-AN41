# ==============================================================================
# CS0065 - INTELLIGENT SYSTEMS: TECHNICAL ASSESSMENT 3 (CBR SYSTEM)
# CASE STUDY 2: AI-BASED LEGAL DECISION SUPPORT SYSTEM
# ==============================================================================

import math

# ------------------------------------------------------------------------------
# STEP 0: INITIALIZE CASE BASE (KNOWLEDGE REPRESENTATION)
# ------------------------------------------------------------------------------
# Storing 4 past legal cases with structured 'problem' and 'solution' attributes.
past_cases = [
    {
        "case_id": "LEGAL_2021_01",
        "problem": {
            "charge": "unauthorized_bank_transfer",
            "amount_stolen": 50000,
            "evidence_type": "IP_address_logs",
            "is_repeat_offender": False
        },
        "solution": {
            "primary_defense": "Challenge IP attribution and argue lack of physical connection to device.",
            "bail_recommendation": 30000,
            "applicable_statute": "Cybercrime Prevention Act - Sec 4(a)(1) Illegal Access"
        }
    },
    {
        "case_id": "LEGAL_2022_05",
        "problem": {
            "charge": "online_identity_theft",
            "amount_stolen": 200000,
            "evidence_type": "phishing_site_logs",
            "is_repeat_offender": True
        },
        "solution": {
            "primary_defense": "File motion to suppress digital evidence due to chain-of-custody gaps.",
            "bail_recommendation": 120000,
            "applicable_statute": "Cybercrime Prevention Act - Sec 4(b)(2) Computer-related Identity Theft"
        }
    },
    {
        "case_id": "LEGAL_2023_12",
        "problem": {
            "charge": "digital_fraud",
            "amount_stolen": 300000,
            "evidence_type": "wire_transfer_records",
            "is_repeat_offender": True
        },
        "solution": {
            "primary_defense": "Argue absence of intent to defraud and misidentification by financial institution.",
            "bail_recommendation": 180000,
            "applicable_statute": "Revised Penal Code - Art. 315 (Estafa via Cybercrime)"
        }
    },
    {
        "case_id": "LEGAL_2024_03",
        "problem": {
            "charge": "unauthorized_bank_transfer",
            "amount_stolen": 80000,
            "evidence_type": "session_cookie_hijack",
            "is_repeat_offender": False
        },
        "solution": {
            "primary_defense": "Assert third-party malware infection without client awareness or intent.",
            "bail_recommendation": 45000,
            "applicable_statute": "Cybercrime Prevention Act - Sec 4(a)(1) Illegal Access"
        }
    }
]

# ------------------------------------------------------------------------------
# NEW UNRESOLVED PROBLEM (NEW CLIENT CASE)
# ------------------------------------------------------------------------------
new_problem = {
    "charge": "unauthorized_bank_transfer",
    "amount_stolen": 150000,
    "evidence_type": "2FA_bypass_logs",
    "is_repeat_offender": False
}


# ------------------------------------------------------------------------------
# STEP 1: RETRIEVAL PHASE (SIMILARITY ASSESSMENT)
# ------------------------------------------------------------------------------
def calculate_legal_similarity(new_p, past_p):
    """
    Calculates weighted similarity score between a new problem and a past case.
    Weights: Charge (0.50), Amount Stolen (0.30), Offender History (0.20)
    """
    # 1. Charge Similarity (Exact Categorical Match)
    charge_sim = 1.0 if new_p["charge"] == past_p["charge"] else 0.0

    # 2. Financial Amount Difference (Normalized linear metric, max range PHP 300,000)
    max_range = 300000.0
    amount_diff = abs(new_p["amount_stolen"] - past_p["amount_stolen"]) / max_range
    amount_sim = max(0.0, 1.0 - amount_diff)

    # 3. Offender History Match (Exact Boolean Match)
    offender_sim = 1.0 if new_p["is_repeat_offender"] == past_p["is_repeat_offender"] else 0.0

    # Weighted composite score calculation
    total_score = (0.50 * charge_sim) + (0.30 * amount_sim) + (0.20 * offender_sim)
    return total_score


def retrieve_best_case(new_p, cases):
    """Iterates over the case base and returns the highest scoring case."""
    best_case = None
    highest_score = -1.0

    print("\n" + "=" * 70)
    print(" 1. RETRIEVAL PHASE: EVALUATING PRECEDENT SIMILARITY")
    print("=" * 70)

    for case in cases:
        score = calculate_legal_similarity(new_p, case["problem"])
        print(f" -> Comparing with {case['case_id']}: Similarity Score = {score * 100:.2f}%")
        if score > highest_score:
            highest_score = score
            best_case = case

    print("-" * 70)
    print(f" RETRIEVED PRECEDENT : {best_case['case_id']} ({highest_score * 100:.2f}% Match)")
    return best_case, highest_score


# ------------------------------------------------------------------------------
# STEPS 2 & 3: REUSE & REVISE PHASES (ADAPTATION LOGIC)
# ------------------------------------------------------------------------------
def adapt_legal_solution(new_p, retrieved_c):
    retrieved_sol = retrieved_c["solution"]
    past_p = retrieved_c["problem"]

    # 1. Base Bail Proportional Scaling (by stolen amount)
    amount_ratio = new_p["amount_stolen"] / past_p["amount_stolen"]
    adapted_bail = round(retrieved_sol["bail_recommendation"] * amount_ratio)

    # 2. DIRECT ADAPTATION RULE: Offender History Penalty
    # If the new client is a repeat offender, increase bail by 50%
    if new_p["is_repeat_offender"]:
        adapted_bail = round(adapted_bail * 1.5)

    # 3. Contextual Evidence Adaptation
    base_defense = retrieved_sol["primary_defense"]
    if new_p["evidence_type"] != past_p["evidence_type"]:
        adapted_defense = (
            f"{base_defense} [ADAPTED: Specifically contest validity of "
            f"'{new_p['evidence_type']}' via forensic integrity audit]."
        )
    else:
        adapted_defense = base_defense

    # 4. DIRECT ADAPTATION RULE: Legal Strategy Note for Recidivism
    if new_p["is_repeat_offender"] and not past_p["is_repeat_offender"]:
        adapted_defense += " [NOTE: Prepare counter-arguments for prosecution's motion to deny bail based on prior record.]"

    return {
        "primary_defense": adapted_defense,
        "bail_recommendation": adapted_bail,
        "applicable_statute": retrieved_sol["applicable_statute"]
    }


# ------------------------------------------------------------------------------
# STEP 4: RETAIN PHASE (LEARNING & STORAGE)
# ------------------------------------------------------------------------------
def retain_new_case(new_p, final_sol, cases):
    """Saves the new case into the existing case base for future reasoning[cite: 2]."""
    new_case_id = f"LEGAL_2026_{len(cases) + 1:02d}"
    new_case = {
        "case_id": new_case_id,
        "problem": new_p,
        "solution": final_sol
    }
    cases.append(new_case)
    return new_case_id


# ==============================================================================
# MAIN EXECUTION WORKFLOW
# ==============================================================================
if __name__ == "__main__":
    # Display Input
    print("=" * 70)
    print(" NEW CLIENT CASE INPUT (PROBLEM)")
    print("=" * 70)
    print(f" Charge             : {new_problem['charge']}")
    print(f" Amount Stolen      : PHP {new_problem['amount_stolen']:,}")
    print(f" Evidence Type      : {new_problem['evidence_type']}")
    print(f" Repeat Offender    : {new_problem['is_repeat_offender']}")

    # 1. Retrieve
    matched_case, similarity = retrieve_best_case(new_problem, past_cases)

    # 2 & 3. Reuse & Revise
    adapted_sol = adapt_legal_solution(new_problem, matched_case)

    print("\n" + "=" * 70)
    print(" 2 & 3. REUSE & REVISE PHASES: ADAPTED LEGAL STRATEGY")
    print("=" * 70)
    print(f" Primary Defense    : {adapted_sol['primary_defense']}")
    print(f" Recommended Bail   : PHP {adapted_sol['bail_recommendation']:,}")
    print(f" Applicable Statute : {adapted_sol['applicable_statute']}")

    # 4. Retain
    new_id = retain_new_case(new_problem, adapted_sol, past_cases)

    print("\n" + "=" * 70)
    print(" 4. RETAIN PHASE: KNOWLEDGE BASE UPDATE")
    print("=" * 70)
    print(f" Status             : New case successfully retained into Case Base[cite: 2].")
    print(f" Assigned Case ID   : {new_id}")
    print(f" Total Case Base    : {len(past_cases)} cases stored.")
    print("=" * 70)