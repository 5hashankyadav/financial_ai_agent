from app.agent.query_parser import FinancialQueryParser


def main():

    parser = FinancialQueryParser()

    questions = [
        "What was Apple's net sales in Q1 FY23?",

        "What was Apple's iPhone revenue in Q1 FY25?",

        "What was Apple's services revenue in Q2 FY24?",

        "What was Apple's Mac revenue in FY23 Q3?",

        "Compare Apple's revenue in Q1 FY23 and Q1 FY25.",

        "Compare Apple's iPhone revenue in FY23 Q1 and FY24 Q1.",
    ]

    for question in questions:

        result = parser.parse(question)

        print()
        print("=" * 80)
        print(question)
        print("=" * 80)

        print(result)


if __name__ == "__main__":
    main()