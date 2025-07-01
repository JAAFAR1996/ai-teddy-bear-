"""
Mock Transformers library for development
This prevents import errors when transformers is not installed
"""


class AutoTokenizer:
    @classmethod
    def from_pretrained(cls, model_name, **kwargs):
        return MockTokenizer()


class AutoModelForCausalLM:
    @classmethod
    def from_pretrained(cls, model_name, **kwargs):
        return MockModel()


class MockTokenizer:
    def __init__(self):
        self.vocab_size = 50000

    def encode(self, text, **kwargs):
        # Mock encoding - return list of integers
        return [1, 2, 3, 4, 5]

    def decode(self, tokens, **kwargs):
        # Mock decoding
        return "مرحبا بك"

    def __call__(self, text, **kwargs):
        return {"input_ids": [[1, 2, 3, 4, 5]], "attention_mask": [[1, 1, 1, 1, 1]]}


class MockModel:
    def __init__(self):
        self.config = MockConfig()

    def generate(self, **kwargs):
        # Mock generation
        return [[1, 2, 3, 4, 5, 6, 7]]

    def to(self, device):
        return self

    def eval(self):
        return self


class MockConfig:
    def __init__(self):
        self.vocab_size = 50000
        self.hidden_size = 768


# Mock pipeline function
def pipeline(task, **kwargs):
    return MockPipeline(task)


class MockPipeline:
    def __init__(self, task):
        self.task = task

    def __call__(self, text, **kwargs):
        if self.task == "sentiment-analysis":
            return [{"label": "POSITIVE", "score": 0.9}]
        elif self.task == "text-generation":
            return [{"generated_text": "مرحبا! كيف يمكنني مساعدتك؟"}]
        else:
            return [{"result": "mock_result"}]


# Mock torch for compatibility
class MockTorch:
    @staticmethod
    def tensor(data):
        return MockTensor(data)

    @staticmethod
    def no_grad():
        return MockContext()

    cuda = MockCuda()


class MockTensor:
    def __init__(self, data):
        self.data = data

    def to(self, device):
        return self


class MockContext:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class MockCuda:
    @staticmethod
    def is_available():
        return False


# Export mock torch as well
torch = MockTorch()
