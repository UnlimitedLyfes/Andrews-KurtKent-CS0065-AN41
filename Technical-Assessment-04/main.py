def initFacts():
    facts = {
        # Category 1: Context
        "scope": "School",              # Fact 1: Environment/setting
        "user_type": "Student",         # Fact 2: User profile

        # Category 2: Task Characteristics
        "task_type": "Essay Writing",   # Fact 3: What needs to be done
        "difficulty": "Medium",         # Fact 4: Task complexity level

        # Category 3: Requirements
        "budget": "Free",               # Fact 5: Cost constraint
        "deadline_days": 2,
        "needs_sources": True,
    }
    return facts


def display_facts(facts):
    print("Initial Facts:")
    for key, value in facts.items():
        print(key + ":", value)


# PART 2: Rule-Based Reasoning
def rule_schoolwork_ai(facts):
    school_tasks = ["Essay Writing", "Group Report", "Presentation"]

    if (
        facts["scope"] == "School"
        and facts["user_type"] == "Student"
        and facts["budget"] == "Free"
        and facts["task_type"] in school_tasks
    ):
        return {
            "field": "ai_type",
            "value": "Gemini",
            "reason": "Because this is free schoolwork for a student, use Gemini.",
        }


def rule_professional_software_ai(facts):
    professional_tasks = ["Software Development", "Professional Work"]

    if facts["task_type"] in professional_tasks:
        return {
            "field": "ai_type",
            "value": "ChatGPT/Codex",
            "reason": "Because this is professional or software work, use ChatGPT/Codex.",
        }


def rule_web_personal_coding_ai(facts):
    if facts["task_type"] == "Personal Web Coding":
        return {
            "field": "ai_type",
            "value": "Claude",
            "reason": "Because this is web or personal coding, use Claude.",
        }


def rule_estimated_minutes(facts):
    estimated_minutes = 30

    if facts["difficulty"] == "Medium":
        estimated_minutes += 15
    elif facts["difficulty"] in ["Hard", "High"]:
        estimated_minutes += 30

    if facts["needs_sources"]:
        estimated_minutes += 15

    if facts["deadline_days"] <= 2:
        estimated_minutes += 10

    return {
        "field": "estimated_minutes",
        "value": estimated_minutes,
        "reason": "Because the task difficulty, source requirement, and deadline need about "
        + str(estimated_minutes)
        + " minutes.",
    }


def rule_ai_level(facts):
    level_score = 1

    if facts["difficulty"] == "Medium":
        level_score += 1
    elif facts["difficulty"] in ["Hard", "High"]:
        level_score += 2

    if facts["needs_sources"]:
        level_score += 1

    if facts["deadline_days"] <= 2:
        level_score += 1

    if level_score <= 1:
        ai_level = "Low"
    elif level_score <= 3:
        ai_level = "Medium"
    else:
        ai_level = "High"

    return {
        "field": "ai_level",
        "value": ai_level,
        "reason": "Because the difficulty is "
        + facts["difficulty"]
        + ", needs_sources is "
        + str(facts["needs_sources"])
        + ", and deadline_days is "
        + str(facts["deadline_days"])
        + ", AI level is "
        + ai_level
        + ".",
    }


def inference_engine(facts, rules):
    solution = {}
    matched_steps = []

    for rule in rules:
        result = rule(facts)
        if result is not None:
            solution[result["field"]] = result["value"]
            matched_steps.append(result["reason"])

    return solution, matched_steps


def RBR():
    facts = initFacts()
    rules = [
        rule_schoolwork_ai,
        rule_professional_software_ai,
        rule_web_personal_coding_ai,
        rule_estimated_minutes,
        rule_ai_level,
    ]
    solution, matched_steps = inference_engine(facts, rules)

    print("Rule-Based Reasoning Matched Steps:")
    for step in matched_steps:
        print("-", step)

    print("\nRule-Based Reasoning Solution:")
    display_solution(solution)


# PART 3: Case-Based Reasoning
def initCaseBase():
    case_base = [
        {
            "problem": {
                "scope": "School",
                "user_type": "Student",
                "task_type": "Essay Writing",
                "difficulty": "Medium",
                "budget": "Free",
                "deadline_days": 2,
                "needs_sources": True,
            },
            "solution": {
                "estimated_minutes": 70,
                "ai_type": "Gemini",
                "ai_level": "High",
            },
        },
        {
            "problem": {
                "scope": "School",
                "user_type": "Student",
                "task_type": "Group Report",
                "difficulty": "Hard",
                "budget": "Free",
                "deadline_days": 5,
                "needs_sources": True,
            },
            "solution": {
                "estimated_minutes": 90,
                "ai_type": "Gemini",
                "ai_level": "High",
            },
        },
        {
            "problem": {
                "scope": "School",
                "user_type": "Student",
                "task_type": "Presentation",
                "difficulty": "Easy",
                "budget": "Low",
                "deadline_days": 3,
                "needs_sources": False,
            },
            "solution": {
                "estimated_minutes": 30,
                "ai_type": "Gemini",
                "ai_level": "Low",
            },
        },
        {
            "problem": {
                "scope": "Professional",
                "user_type": "Software Developer",
                "task_type": "Software Development",
                "difficulty": "Hard",
                "budget": "Paid",
                "deadline_days": 7,
                "needs_sources": False,
            },
            "solution": {
                "estimated_minutes": 120,
                "ai_type": "ChatGPT/Codex",
                "ai_level": "High",
            },
        },
        {
            "problem": {
                "scope": "Personal",
                "user_type": "Coder",
                "task_type": "Personal Web Coding",
                "difficulty": "Medium",
                "budget": "Free",
                "deadline_days": 4,
                "needs_sources": False,
            },
            "solution": {
                "estimated_minutes": 60,
                "ai_type": "Claude",
                "ai_level": "Medium",
            },
        },
    ]
    return case_base


def similarity_score(new_problem, old_problem):
    score = 0

    for feature, value in new_problem.items():
        if feature in old_problem and old_problem[feature] == value:
            score += 1

    return score


def retrieve_most_similar_case(new_problem, case_base):
    best_case = case_base[0]
    best_score = similarity_score(new_problem, best_case["problem"])
    case_scores = []

    for case in case_base:
        score = similarity_score(new_problem, case["problem"])
        similarity_percent = (score / len(new_problem)) * 100
        case_scores.append(similarity_percent)

        if score > best_score:
            best_case = case
            best_score = score

    return best_case, best_score, case_scores


def display_solution(solution):
    print("Estimated minutes:", solution["estimated_minutes"])
    print("Type of AI to use:", solution["ai_type"])
    print("Level of AI:", solution["ai_level"])


def revise_solution(solution):
    print("\nSuggested CBR Solution:")
    display_solution(solution)

    try:
        revised_minutes = input(
            "Revise estimated minutes or press Enter to keep it unchanged: "
        ).strip()
        revised_ai_type = input(
            "Revise type of AI or press Enter to keep it unchanged: "
        ).strip()
        revised_ai_level = input(
            "Revise AI level (Low, Medium, High) or press Enter to keep it unchanged: "
        ).strip()
    except EOFError:
        revised_minutes = ""
        revised_ai_type = ""
        revised_ai_level = ""

    revised_solution = solution.copy()

    if revised_minutes:
        try:
            revised_solution["estimated_minutes"] = int(revised_minutes)
        except ValueError:
            print("Invalid number entered. Keeping estimated minutes unchanged.")

    if revised_ai_type:
        revised_solution["ai_type"] = revised_ai_type

    if revised_ai_level in ["Low", "Medium", "High"]:
        revised_solution["ai_level"] = revised_ai_level
    elif revised_ai_level:
        print("Invalid AI level entered. Keeping AI level unchanged.")

    return revised_solution


def retain_case(case_base, problem, solution):
    new_case = {
        "problem": problem,
        "solution": solution,
    }
    case_base.append(new_case)
    return case_base


def CBR():
    facts = initFacts()
    case_base = initCaseBase()

    new_problem = {
        "scope": facts["scope"],
        "user_type": facts["user_type"],
        "task_type": facts["task_type"],
        "difficulty": facts["difficulty"],
        "budget": facts["budget"],
        "deadline_days": facts["deadline_days"],
        "needs_sources": facts["needs_sources"],
    }

    matched_case, score, case_scores = retrieve_most_similar_case(new_problem, case_base)

    print("\nCase-Based Reasoning Similarity Scores:")
    for index, similarity_percent in enumerate(case_scores):
        print("Case", index + 1, "similarity:", str(round(similarity_percent, 2)) + "%")

    final_solution = revise_solution(matched_case["solution"])
    retain_case(case_base, new_problem, final_solution)

    print("\nCase-Based Reasoning Result:")
    print("Most similar case score:", score, "out of", len(new_problem))
    print("Final solution:")
    display_solution(final_solution)
    print("Total cases after retain step:", len(case_base))


def main():
    facts = initFacts()
    display_facts(facts)
    print()

    RBR()
    CBR()


if __name__ == "__main__":
    main()
