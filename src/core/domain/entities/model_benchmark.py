import json
import logging
import os
import time
from typing import Any, Dict, List


class ModelBenchmark:
    """
    Benchmark AI model performance and resource utilization
    """

    def __init__(self, model_providers: List[str] = None):
        """
        Initialize model benchmarking

        :param model_providers: List of model providers to benchmark
        """
        self._logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
        self._model_providers = model_providers or ["openai", "anthropic", "google"]
        self._test_prompts = [
            "Tell me a short story about a curious child.",
            "Explain quantum computing in simple terms.",
            "Write a poem about learning and discovery.",
            "Solve a simple math problem step by step.",
            "Describe the importance of emotional intelligence.",
        ]

    def _benchmark_llm(self, provider: str) -> Dict[str, Any]:
        """
        Benchmark a specific language model provider

        :param provider: Name of the LLM provider
        :return: Benchmark results for the provider
        """
        try:
            if provider == "openai":
                from openai import OpenAI

                client = OpenAI()
                results = {
                    "provider": "OpenAI",
                    "model": "gpt-3.5-turbo",
                    "prompts": [],
                }
                for prompt in self._test_prompts:
                    start_time = time.time()
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a helpful assistant.",
                            },
                            {"role": "user", "content": prompt},
                        ],
                    )
                    end_time = time.time()
                    results["prompts"].append(
                        {
                            "prompt": prompt,
                            "response_time": end_time - start_time,
                            "tokens_used": response.usage.total_tokens,
                            "response_length": len(response.choices[0].message.content),
                        }
                    )
                return results
            elif provider == "anthropic":
                import anthropic

                client = anthropic.Anthropic()
                results = {"provider": "Anthropic", "model": "claude-2", "prompts": []}
                for prompt in self._test_prompts:
                    start_time = time.time()
                    response = client.completions.create(
                        model="claude-2", max_tokens_to_sample=300, prompt=prompt
                    )
                    end_time = time.time()
                    results["prompts"].append(
                        {
                            "prompt": prompt,
                            "response_time": end_time - start_time,
                            "tokens_used": len(response.completion.split()),
                            "response_length": len(response.completion),
                        }
                    )
                return results
            elif provider == "google":
                import google.generativeai as genai

                genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
                results = {"provider": "Google", "model": "gemini-pro", "prompts": []}
                model = genai.GenerativeModel("gemini-pro")
                for prompt in self._test_prompts:
                    start_time = time.time()
                    response = model.generate_content(prompt)
                    end_time = time.time()
                    results["prompts"].append(
                        {
                            "prompt": prompt,
                            "response_time": end_time - start_time,
                            "tokens_used": len(response.text.split()),
                            "response_length": len(response.text),
                        }
                    )
                return results
            else:
                raise ValueError(f"Unsupported provider: {provider}")
        except Exception as e:
            self._logger.error(f"Benchmark error for {provider}: {e}")
            return {"provider": provider, "error": str(e)}

    def run_benchmarks(self) -> Dict[str, Any]:
        """
        Run benchmarks for all specified providers

        :return: Comprehensive benchmark results
        """
        results = {"timestamp": time.time(), "providers": []}
        for provider in self._model_providers:
            provider_results = self._benchmark_llm(provider)
            results["providers"].append(provider_results)
        return results

    def export_results(
        self, results: Dict[str, Any], output_path: str = "model_benchmark.json"
    ):
        """
        Export benchmark results to a JSON file

        :param results: Benchmark results
        :param output_path: Path to export results
        """
        try:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(results, f, indent=4)
            self._logger.info(f"Benchmark results exported to {output_path}")
        except Exception as e:
            self._logger.error(f"Error exporting benchmark results: {e}")


def main():
    """
    CLI for model benchmarking
    """
    import argparse

    parser = argparse.ArgumentParser(description="AI Model Performance Benchmark")
    parser.add_argument(
        "-p",
        "--providers",
        nargs="+",
        default=["openai", "anthropic", "google"],
        help="List of model providers to benchmark",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="model_benchmark.json",
        help="Path to export benchmark results",
    )
    parser.add_argument(
        "--print", action="store_true", help="Print benchmark results to console"
    )
    args = parser.parse_args()
    benchmark = ModelBenchmark(args.providers)
    results = benchmark.run_benchmarks()
    if args.print:
        logger.info(json.dumps(results, indent=4))
    benchmark.export_results(results, args.output)


if __name__ == "__main__":
    main()
