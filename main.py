from app.graph.workflow import compiled


def main():
    question = input("Question: ")

    result = compiled.invoke({
        "question": question
    })

    print("\nANSWER:")
    print(result["answer"])

    print("\nSOURCES:")
    for source in result.get("sources", []):
        print(source)


if __name__ == "__main__":
    main()