from llm import run_agent


def main():
    result = run_agent(
        "hows the weather today"
    )

    print(result)


if __name__ == "__main__":
    main()