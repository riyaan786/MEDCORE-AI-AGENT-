from app.llm import run_agent
from app.evaluation_cases import EVALUATION_CASES


def run_evaluations():

    total = len(EVALUATION_CASES)
    passed = 0

    print("\n==============================")
    print("MEDCORE AI EVALUATION")
    print("==============================")

    for case in EVALUATION_CASES:

        print(f"\nTEST: {case['name']}")
        print(f"REQUEST: {case['request']}")

        try:
            result = run_agent(case["request"])

            actual_tool = result["tool"]
            success = result["success"]
            response = result["response"]

            print(f"ACTUAL TOOL: {actual_tool}")
            print(f"SUCCESS: {success}")
            print(f"RESPONSE: {response}")

            tool_correct = actual_tool == case["expected_tool"]
            success_correct = success == case["expected_success"]

            if tool_correct and success_correct:
                print("RESULT: PASS")
                passed += 1
            else:
                print("RESULT: FAIL")

                if not tool_correct:
                    print(
                        f"Expected tool: {case['expected_tool']}"
                    )

                if not success_correct:
                    print(
                        f"Expected success: {case['expected_success']}"
                    )

        except Exception as error:

            print(f"ERROR: {error}")
            print("RESULT: FAIL")

    accuracy = (passed / total) * 100

    print("\n==============================")
    print(f"PASSED: {passed}/{total}")
    print(f"ACCURACY: {accuracy:.1f}%")
    print("==============================")


if __name__ == "__main__":
    run_evaluations()