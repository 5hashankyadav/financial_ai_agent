from app.agent.router import QueryRouter


def main():

    router = QueryRouter()

    questions = [
        "What was Apple's net sales in Q1 FY23?",
        "What was Apple's iPhone revenue in Q1 FY25?",
        "What factors affected Apple's performance?",
        "Why did Apple's revenue change?",
        "Compare Apple's revenue in Q1 FY23 and Q1 FY25.",
    ]

    for question in questions:

        route = router.classify(question)

        print()
        print("=" * 70)
        print("Question:", question)
        print("Route:", route)


if __name__ == "__main__":
    main()