from app.llm import run_agent
from app.hospital_data import reset_data
from app.evaluation_cases import EVALUATION_CASES


def run_evaluations():

    total = len(EVALUATION_CASES)
    passed = 0

    print()
    print("=" * 30)
    print("MEDCORE AI EVALUATION")
    print("=" * 30)

    # Reset data to original state before running tests
    reset_data()

    for case in EVALUATION_CASES:

        print()
        print(f"TEST: {case['name']}")
        print(f"REQUEST: {case['request']}")

        # Reset data before each stateful test
        if case.get("stateful", False):
            reset_data()

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

            response_correct = True
            if "expected_response" in case:
                expected = case["expected_response"]
                response_correct = (
                    expected.lower() in response.lower()
                )
                if not response_correct:
                    print(
                        f"Expected response to "
                        f"contain: {expected}"
                    )

            if (
                tool_correct
                and success_correct
                and response_correct
            ):
                print("RESULT: PASS")
                passed += 1
            else:
                print("RESULT: FAIL")

                if not tool_correct:
                    print(
                        f"Expected tool: "
                        f"{case['expected_tool']}"
                    )

                if not success_correct:
                    print(
                        f"Expected success: "
                        f"{case['expected_success']}"
                    )

        except Exception as error:

            print(f"ERROR: {error}")
            print("RESULT: FAIL")

    accuracy = (passed / total) * 100

    print()
    print("=" * 30)
    print(f"PASSED: {passed}/{total}")
    print(f"ACCURACY: {accuracy:.1f}%")
    print("=" * 30)
    print()


if __name__ == "__main__":
    run_evaluations()
