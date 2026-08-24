from app.llm import run_agent


def main():

    print()
    print("=" * 50)
    print("MedCore AI")
    print("Hospital Operations Assistant")
    print("=" * 50)
    print()
    print("Type 'exit' to quit.")
    print()

    while True:

        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in [
            "exit",
            "quit",
        ]:
            print()
            print("MedCore AI: Goodbye.")
            break

        try:

            result = run_agent(user_input)

            print()
            print(
                "MedCore AI:",
                result["response"]
            )
            print()

        except Exception as error:

            print()
            print(
                "MedCore AI: An error occurred."
            )

            print(
                "Error:",
                error
            )

            print()


if __name__ == "__main__":
    main()