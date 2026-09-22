"""Project-local seam over local_llm_wrapper.llm.

The build supports Ollama, Codex CLI, and Claude Code CLI title generation
through the same LLMClient interface.
"""

# Standard Library
import shutil

# PIP3 modules
import ollama
# PIP3 modules (vendored at ~/nsh/local-llm-wrapper, see source_me.sh)
import local_llm_wrapper.llm as llm


DEFAULT_OLLAMA_MODEL = "gemma4:e4b"
LLM_BACKENDS = ("ollama", "codex", "claude")
DEFAULT_LLM_BACKEND = "ollama"


#============================================
def validate_ollama_model(model: str) -> None:
	"""Verify that model is installed locally in Ollama.

	Uses the official `ollama` Python client so the connection details
	(host, scheme) come from its standard environment-variable handling
	rather than a hand-rolled URL.

	Args:
		model: exact Ollama model name to check

	Raises:
		RuntimeError: if Ollama is unreachable or the model is not installed
	"""
	# ollama.list() raises ConnectionError when the daemon is not running.
	try:
		listing = ollama.list()
	except (ConnectionError, ollama.ResponseError) as exc:
		raise RuntimeError(
			f"Cannot connect to Ollama: {exc}\n"
			"Start Ollama first: ollama serve"
		)
	# Each entry is a Model object with a 'model' attribute (e.g. "llama3.2:3b").
	local_models = [entry.model for entry in listing.models]
	if model not in local_models:
		installed_str = ", ".join(local_models) if local_models else "none"
		raise RuntimeError(
			f"Requested Ollama model not available locally: {model}\n"
			f"Installed models: {installed_str}\n"
			f"Install with: ollama pull {model}"
		)


#============================================
def validate_backend(backend: str, model: str | None = None) -> None:
	"""Validate the selected title-generation backend before rendering."""
	if backend not in LLM_BACKENDS:
		raise ValueError(
			f"Unknown LLM backend: {backend}. "
			f"Choose one of: {', '.join(LLM_BACKENDS)}."
		)
	if backend == "ollama":
		validate_ollama_model(model or DEFAULT_OLLAMA_MODEL)
		return
	cli_name = "codex" if backend == "codex" else "claude"
	if shutil.which(cli_name) is None:
		raise RuntimeError(
			f"The {backend} backend requires the '{cli_name}' command on PATH."
		)


#============================================
def create_llm_client(
		backend: str = DEFAULT_LLM_BACKEND,
		model: str | None = None,
	) -> llm.LLMClient:
	"""Create a title-generation client for the selected backend.

	Args:
		backend: one of ``ollama``, ``codex``, or ``claude``
		model: backend-specific model name, or None for that backend's default

	Returns:
		configured LLMClient with one selected transport
	"""
	if backend == "ollama":
		transport = llm.OllamaTransport(model=model or DEFAULT_OLLAMA_MODEL)
	elif backend == "codex":
		transport = llm.CodexTransport(model=model)
	elif backend == "claude":
		transport = llm.ClaudeCodeTransport(model=model)
	else:
		raise ValueError(
			f"Unknown LLM backend: {backend}. "
			f"Choose one of: {', '.join(LLM_BACKENDS)}."
		)
	# ASVS 1.2.5 and 2.2.1: backend names are an allowlist, and the selected
	# transport receives the prompt through its parameterized process/API path.
	client = llm.LLMClient(transports=[transport], quiet=True)
	return client
