from src.builder import Builder
from src.visualizer import Visualizer


def main():
    try:
        builder = Builder()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()

