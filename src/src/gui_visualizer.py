from collections.abc import Callable
from typing import Any
import queue
import threading
import time
import tkinter as tk
from tkinter import ttk


class Visualizer:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Token Generation Visualizer")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)

        self.event_queue: queue.Queue[tuple[Any, ...]] = queue.Queue()
        self.start_time: float | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill="x", padx=10, pady=5)

        self.timer_label = ttk.Label(
            top_frame,
            text="Time: 00:00.0",
            font=("Consolas", 14, "bold"),
        )
        self.timer_label.pack(side="left")

        self.progress_label = ttk.Label(
            top_frame,
            text="Prompt: -/-",
            font=("Consolas", 12),
        )
        self.progress_label.pack(side="right")

        prompt_frame = ttk.LabelFrame(self.root, text="Prompts")
        prompt_frame.pack(fill="both", padx=10, pady=5, expand=False)

        prompt_grid = ttk.Frame(prompt_frame)
        prompt_grid.pack(fill="both", expand=True, padx=5, pady=5)
        prompt_grid.rowconfigure(0, weight=1)
        prompt_grid.columnconfigure(0, weight=1)

        self.prompt_text = tk.Text(
            prompt_grid,
            height=6,
            wrap="word",
            state="disabled",
            bg="#1e1e1e",
            fg="white",
            font=("Consolas", 10),
            insertbackground="white",
            relief="flat",
        )
        prompt_scroll = ttk.Scrollbar(
            prompt_grid,
            orient="vertical",
            command=self.prompt_text.yview,
        )
        self.prompt_text.configure(yscrollcommand=prompt_scroll.set)

        self.prompt_text.grid(row=0, column=0, sticky="nsew")
        prompt_scroll.grid(row=0, column=1, sticky="ns")

        self.prompt_text.tag_configure(
            "current",
            foreground="#4EC9B0",
            font=("Consolas", 10, "bold"),
        )
        self.prompt_text.tag_configure(
            "old",
            foreground="white",
            font=("Consolas", 10),
        )

        output_frame = ttk.LabelFrame(self.root, text="Output")
        output_frame.pack(fill="both", expand=True, padx=10, pady=5)

        output_grid = ttk.Frame(output_frame)
        output_grid.pack(fill="both", expand=True, padx=5, pady=5)
        output_grid.rowconfigure(0, weight=1)
        output_grid.columnconfigure(0, weight=1)

        self.output_text = tk.Text(
            output_grid,
            wrap="word",
            font=("Consolas", 11),
            state="disabled",
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="white",
            relief="flat",
        )
        output_scroll = ttk.Scrollbar(
            output_grid,
            orient="vertical",
            command=self.output_text.yview,
        )
        self.output_text.configure(yscrollcommand=output_scroll.set)

        self.output_text.grid(row=0, column=0, sticky="nsew")
        output_scroll.grid(row=0, column=1, sticky="ns")

        self.output_text.tag_configure(
            "title",
            foreground="#569CD6",
            font=("Consolas", 11, "bold"),
        )
        self.output_text.tag_configure(
            "error",
            foreground="#F44747",
            font=("Consolas", 11, "bold"),
        )

    def _process_events(self) -> None:
        try:
            while True:
                event = self.event_queue.get_nowait()
                event_type = event[0]

                if event_type == "new_prompt":
                    _, prompt, index, total = event
                    self.progress_label.config(text=f"Prompt: {index}/{total}")

                    self.prompt_text.config(state="normal")
                    self.prompt_text.tag_remove("current", "1.0", "end")
                    self.prompt_text.insert("end", f"> {prompt}\n", "current")
                    self.prompt_text.config(state="disabled")
                    self.prompt_text.see("end")

                    self.output_text.config(state="normal")
                    self.output_text.insert(
                        "end",
                        "Model Generation:\n",
                        "title",
                    )
                    self.output_text.config(state="disabled")
                    self.output_text.see("end")

                elif event_type == "new_token":
                    _, token = event
                    self.output_text.config(state="normal")
                    self.output_text.insert("end", token)
                    self.output_text.config(state="disabled")
                    self.output_text.see("end")

                elif event_type == "result":
                    _, formatted_json = event
                    self.output_text.config(state="normal")
                    self.output_text.insert("end", "\n\nResult:\n", "title")
                    self.output_text.insert("end", formatted_json + "\n\n")
                    self.output_text.config(state="disabled")
                    self.output_text.see("end")

                elif event_type == "validation_error":
                    _, error_msg = event
                    self.output_text.config(state="normal")
                    self.output_text.insert(
                        "end",
                        f"\n[ERROR: {error_msg}]\n",
                        "error",
                    )
                    self.output_text.insert(
                        "end",
                        "\nModel Generation:\n",
                        "title",
                    )
                    self.output_text.config(state="disabled")
                    self.output_text.see("end")

                elif event_type == "complete":
                    if self.start_time:
                        elapsed = time.time() - self.start_time
                        mins = int(elapsed // 60)
                        secs = elapsed % 60
                        self.timer_label.config(
                            text=f"Time: {mins:02d}:{secs:04.1f} (Done)",
                        )
                    self.progress_label.config(text="All prompts completed")
                    self.start_time = None

        except queue.Empty:
            pass

        if self.start_time:
            elapsed = time.time() - self.start_time
            mins = int(elapsed // 60)
            secs = elapsed % 60
            self.timer_label.config(text=f"Timer: {mins:02d}:{secs:04.1f}")

        self.root.after(50, self._process_events)

    def notify_new_prompt(self, prompt: str, index: int, total: int) -> None:
        self.event_queue.put(("new_prompt", prompt, index, total))

    def notify_new_token(self, token: str) -> None:
        self.event_queue.put(("new_token", token))

    def notify_result(self, formatted_json: str) -> None:
        self.event_queue.put(("result", formatted_json))

    def notify_validation_error(self, error_msg: str) -> None:
        self.event_queue.put(("validation_error", error_msg))

    def notify_complete(self) -> None:
        self.event_queue.put(("complete",))

    def run(self, build_fn: Callable[[], None]) -> None:
        """Start the GUI and run build_fn in a background thread."""
        self.start_time = time.time()
        self._process_events()

        def _safe_run() -> None:
            build_fn()

        thread = threading.Thread(target=_safe_run, daemon=True)
        thread.start()
        self.root.mainloop()
