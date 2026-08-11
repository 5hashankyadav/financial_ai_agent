from app.agent.financial_agent import FinancialAgent


def main():

    agent = FinancialAgent()

    questions = [
        "What was Apple's net sales in Q1 FY23?",
        "What factors affected Apple's performance?",
        "Why did Apple's revenue change?",
        "Compare Apple's revenue in Q1 FY23 and Q1 FY25.",
    ]

    for question in questions:

        print()
        print("=" * 80)
        print("QUESTION")
        print("=" * 80)
        print(question)

        result = agent.ask(question)

        print("\nROUTE:")
        print(result["route"])

        print("\nANSWER:")
        print(result["answer"])


if __name__ == "__main__":
    main()
