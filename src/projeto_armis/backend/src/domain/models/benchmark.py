from os import sep
from datetime import datetime

from langchain_community.callbacks import OpenAICallbackHandler

from flask import current_app


class Benchmark:
    # TODO: Add timeframes of database operations
    # TODO: Add token info
    def __init__(self, name: str):
        self.name = name.capitalize()
        self.completion_model: str = ""
        self.embeddings_model: str = ""
        self.execution_start_datetime: datetime = datetime.min
        self.execution_end_datetime: datetime = datetime.max
        self.spent_llm_datetime_frames: list[tuple[str, datetime, datetime]] = []
        self.logs: list[str] = []
        self.prompt_tokens: list[tuple[str, int]] = []
        self.completion_tokens: list[tuple[str, int]] = []
        self.reasoning_tokens: list[tuple[str, int]] = []
        self.successful_requests: list[tuple[str, int]] = []
        self.cost: float = 0

    def start_benchmark(self, completion_model, embeddings_model):
        print(f"[Benchmark]: Started benchmark for {self.name}...")
        if not completion_model and not embeddings_model:
            raise RuntimeError("Both completion model and embeddings model can't be null!")
        self.completion_model = completion_model
        self.embeddings_model = embeddings_model
        self.execution_start_datetime = datetime.now()
        self.add_log(text="Start Execution", timestamp=self.execution_start_datetime)

    def end_benchmark(self):
        print(f"[Benchmark]: Ended benchmark for {self.name}...")
        self.execution_end_datetime = datetime.now()

    def process_callback(self, operation_name: str, callback: OpenAICallbackHandler):
        self.add_sucessful_requests(operation_name=operation_name, n_requests=callback.successful_requests)
        self.add_prompt_tokens(operation_name=operation_name, tokens=callback.prompt_tokens)
        self.add_completion_tokens(operation_name=operation_name, tokens=callback.completion_tokens)
        self.add_reasoning_tokens(operation_name=operation_name, tokens=callback.reasoning_tokens)
        self.add_cost(operation_name=operation_name, cost=callback.total_cost)

    def add_thinking_time(self, operation_name: str, start: datetime, end: datetime):
        self.spent_llm_datetime_frames.append((operation_name, start, end))
        self.add_log(f"Added thinking time for {operation_name}")
        return (end - start).total_seconds() * 1000

    def add_prompt_tokens(self, operation_name: str, tokens: int):
        self.prompt_tokens.append((operation_name, tokens))
        self.add_log(f"Added prompt tokens for {operation_name}")

    def add_completion_tokens(self, operation_name: str, tokens: int):
        self.completion_tokens.append((operation_name, tokens))
        self.add_log(f"Added completion tokens for {operation_name}")

    def add_reasoning_tokens(self, operation_name: str, tokens: int):
        self.reasoning_tokens.append((operation_name, tokens))
        self.add_log(f"Added reasoning tokens for {operation_name}")

    def add_cost(self, operation_name: str, cost: float):
        self.cost += cost
        self.add_log(f"Added cost for {operation_name}")

    def add_sucessful_requests(self, operation_name: str, n_requests: int):
        self.successful_requests.append((operation_name, n_requests))
        self.add_log(f"Added reasoning tokens for {operation_name}")

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
        """
        Exibe um resumo organizado do benchmark e salva o output num ficheiro:
        - Períodos de execução
        - Tempos de pensamento vs. tempo total
        - Uso de tokens por operação
        - Custo total
        - Logs detalhados
        """

        lines: list[str] = []
        # Cabeçalho
        lines.append(f"=== {self.name} Benchmark ===")

        # Modelos e período
        lines.append("Modelos:")
        lines.append(f"  • Completion: {self.completion_model}")
        lines.append(f"  • Embeddings: {self.embeddings_model}")
        lines.append("Período:")
        lines.append(f"  • Início: {self.execution_start_datetime}")
        lines.append(f"  • Fim:    {self.execution_end_datetime}")

        # Cálculo de tempos em milissegundos
        total_ms = (self.execution_end_datetime - self.execution_start_datetime).total_seconds() * 1000
        lines.append(f"Total execução: {total_ms:.2f} ms")

        # Tempos de pensamento LLM
        lines.append("\nTempos de pensamento (LLM):")
        thinking_ms = 0.0
        for op, start, end in self.spent_llm_datetime_frames:
            dur = (end - start).total_seconds() * 1000
            thinking_ms += dur
            lines.append(f"  • {op:<20}: {dur:8.2f} ms")
        lines.append(f"  ─{'─' * 28}")
        lines.append(f"Total tempo de pensamento:       {thinking_ms:8.2f} ms")
        real_ms = total_ms - thinking_ms
        lines.append(f"Total Tempo real:      {real_ms:8.2f} ms")

        # Uso de tokens
        lines.append("\nUso de tokens (por operação):")
        header = f"{'Operação':<20} {'Prompt':>8} {'Completion':>12} {'Reasoning':>12}"
        lines.append(header)
        lines.append('-' * len(header))
        ops = set(name for name, _ in self.prompt_tokens) \
              | set(name for name, _ in self.completion_tokens) \
              | set(name for name, _ in self.reasoning_tokens)
        for op in sorted(ops):
            p = next((t for name, t in self.prompt_tokens if name == op), 0)
            c = next((t for name, t in self.completion_tokens if name == op), 0)
            r = next((t for name, t in self.reasoning_tokens if name == op), 0)
            lines.append(f"{op:<20} {p:8d} {c:12d} {r:12d}")

        # Custo
        lines.append(f"\nCusto total: {self.cost:.6f} USD")

        # Logs
        lines.append("\nLogs:")
        for log in self.logs:
            lines.append(f"  - {log}")
        lines.append("=" * 30)

        # Salvar em ficheiro
        timestamp = datetime.now().strftime("%d-%m-%y_%H-%M-%S")
        filename = f"{timestamp}_{self.name.replace(" ", "").lower()}.txt"
        filepath = current_app.config['OUTPUT_FOLDER'] + sep + filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        # Imprimir no ecrã
        for line in lines:
            print(line)
        print(f"\nOutput também salvo em {filename}")
