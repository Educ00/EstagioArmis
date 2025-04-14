import json
from datetime import datetime

class Benchmark:
    # TODO: Add timeframes of database operations
    # TODO: Add token info
    def __init__(self):
        self.completion_model: str = ""
        self.embeddings_model: str = ""
        self.execution_start_datetime: datetime = datetime.min
        self.execution_end_datetime: datetime = datetime.max
        self.spent_llm_datetime_frames: list[tuple[str, datetime, datetime]] = []
        self.logs: list[str] = []
        self.input_tokens: list[tuple[str, int]] = []
        self.output_tokens: list[tuple[str, int]] = []

    def start_benchmark(self, completion_model, embeddings_model):
        print("[Benchmark]: Started benchmark...")
        if not completion_model and not embeddings_model:
            raise RuntimeError("Both completion model and embeddings model can't be null!")
        self.completion_model = completion_model
        self.embeddings_model = embeddings_model
        self.execution_start_datetime = datetime.now()
        self.add_log(text="Start Execution", timestamp=self.execution_start_datetime)

    def end_benchmark(self):
        print("[Benchmark]: Ended benchmark...")
        self.execution_end_datetime = datetime.now()
        
    def add_thinking_time(self, operation_name: str, start: datetime, end: datetime):
        self.spent_llm_datetime_frames.append((operation_name, start, end))
        self.add_log(f"Added thinking time for {operation_name}")
        return (end - start).total_seconds() * 1000

    def add_log(self, text: str, timestamp=None) -> str:
        """
        Adds log with timestamp
        :param timestamp: None by default
        :param text: the text log
        :return: formated log
        """
        if timestamp:
            temp_timestamp = timestamp
        else:
            temp_timestamp = datetime.now()

        formatted_text = f"[{temp_timestamp}] {text}"
        self.logs.append(formatted_text)
        return formatted_text

    def compute_execution_time(self):
        return self.execution_start_datetime - self.execution_end_datetime

    def display(self):
        print("\n--- Benchmark Summary ---")
        print(f"Completion model: {self.completion_model}")
        print(f"Embeddings model: {self.embeddings_model}")
        print(f"Execution started at: {self.execution_start_datetime}")
        print(f"Execution ended at:   {self.execution_end_datetime}")

        total_time_ms = (self.execution_end_datetime - self.execution_start_datetime).total_seconds() * 1000
        print(f"Total execution time: {total_time_ms:.2f} ms")

        print("\n--- LLM Thinking Time ---")
        for name, start, end in self.spent_llm_datetime_frames:
            duration = (end - start).total_seconds() * 1000
            print(f"  {name}: {duration:.2f} ms")

        print("\n--- Token Counts ---")
        print("Input tokens:")
        for op, count in self.input_tokens:
            print(f"  {op}: {count}")
        print("Output tokens:")
        for op, count in self.output_tokens:
            print(f"  {op}: {count}")

        print("\n--- Logs ---")
        for log in self.logs:
            print(log)
        print("-----------------------")
    