from app.llm import run_agent


TEST_CASES = [
    {
        "name": "Cardiology appointment",
        "request": "Find the earliest available cardiology appointment.",
        "expected_values": [
            "August 26, 2026",
            "10:30",
        ],
    },
    {
        "name": "Patient lookup",
        "request": "Look up patient P1001.",
        "expected_values": [
            "P1001",
            "Arjun Mehta",
        ],
    },
]


def evaluate_response(response, expected_values):
    return all(
        value.lower() in response.lower()
        for value in expected_values
    )


def run_evaluations():
    passed = 0

    for test in TEST_CASES:
        print(f"\nRunning: {test['name']}")

        response = run_agent(test["request"])

        print(f"Response: {response}")

        if evaluate_response(response, test["expected_values"]):
            print("PASS")
            passed += 1
        else:
            print("FAIL")

    total = len(TEST_CASES)

    print(f"\nPassed: {passed}/{total}")
    print(f"Accuracy: {(passed / total) * 100:.1f}%")


if __name__ == "__main__":
    run_evaluations()