from app.agent.hybrid import HybridContextBuilder


def main():

    builder = HybridContextBuilder()

    question = (
        "Compare Apple's revenue in "
        "Q2 FY25 and Q3 FY25."
    )

    context = builder.build(
        question,
        rag_results=[]
    )

    print("=" * 80)
    print("HYBRID DRIVER CONTEXT TEST")
    print("=" * 80)

    print(context)


if __name__ == "__main__":
    main()