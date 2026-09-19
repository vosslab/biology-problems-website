"""Project-local seam over local_llm_wrapper.llm.

Mirrors validate_ollama_model and create_llm_client from the sibling repo
biology-problems/topic_classifier/classifier_common.py so the integration
shape stays consistent across repos.
"""

# PIP3 modules
import ollama
# PIP3 modules (vendored at ~/nsh/local-llm-wrapper, see source_me.sh)
import local_llm_wrapper.llm as llm


DEFAULT_OLLAMA_MODEL = "gemma4:e4b"


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
def create_llm_client(model: str = None) -> llm.LLMClient:
	"""Create an Ollama client for problem-set title generation.

	Args:
		model: exact Ollama model name, or None for the project default

	Returns:
		configured LLMClient with a single Ollama transport
	"""
	ollama_model = model if model else DEFAULT_OLLAMA_MODEL
	transport = llm.OllamaTransport(model=ollama_model)
	client = llm.LLMClient(transports=[transport], quiet=True)
	return client
