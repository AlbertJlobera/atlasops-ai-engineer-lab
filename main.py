from app.rag import ask_rag


def main():
    question = input("Question: ")

    result = ask_rag(question)

    print("\nANSWER:")
    print(result["answer"])

    print("\nSOURCES:")
    for source in result["sources"]:
        print(source)


if __name__ == "__main__":
    main()