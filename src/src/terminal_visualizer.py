import time


class Visualizer:

    BOLD = "\033[1m"
    RESET = "\033[0m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"

    def __init__(self) -> None:
        self.start_time: float | None = None
        self.run()

    def notify_new_prompt(self, prompt: str, index: int, total: int) -> None:
        header = f"\n[{index}/{total}] Prompt"
        print(f"\n{self.BOLD}{self.CYAN}{header}:{self.RESET} {prompt}")
        print(f"\n{self.BOLD}{self.RED}Model Generation:{self.RESET}")

    def notify_new_token(self, token: str) -> None:
        print(token, end="", flush=True)

    def notify_result(self, formatted_json: str) -> None:
        print(f"\n\n{self.BOLD}{self.GREEN}Result:{self.RESET}")
        print(formatted_json)

    def notify_complete(self) -> None:
        if self.start_time is None:
            print(f"\n{self.BOLD}{self.GREEN}Done.{self.RESET}")
            return

        elapsed = time.time() - self.start_time
        minutes = int(elapsed // 60)
        seconds = elapsed % 60
        elapsed_text = f"{minutes:02d}:{seconds:04.1f}"
        print(f"\n{self.BOLD}{self.YELLOW}Time elapsed: "
              f"{elapsed_text}{self.RESET}")

        print(f"{self.BOLD}{self.GREEN}Done.{self.RESET}")

    def run(self) -> None:
        self.start_time = time.time()
