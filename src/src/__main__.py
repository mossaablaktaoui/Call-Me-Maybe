from src.builder import Builder


def main() -> None:
    try:
        Builder()
    except Exception as error:
        print(error)


if __name__ == "__main__":
    main()
