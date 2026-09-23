"""Optional progress and cooperative cancellation for unified builds."""

from collections.abc import Callable
from dataclasses import dataclass
from threading import Event


#============================================
class BuildCancelledError(Exception):
	"""Raised when a build reaches a boundary after cancellation was requested."""


#============================================
@dataclass(frozen=True)
class BuildProgress:
	"""Report internal build events and check a caller-owned cancellation signal."""

	callback: Callable[[str, dict[str, object]], None]
	cancel_event: Event

	def emit(self, event: str, **details: object) -> None:
		"""Send one progress event to the caller."""
		self.callback(event, details)

	def check_cancelled(self) -> None:
		"""Stop before starting more work after a cooperative cancellation request."""
		if self.cancel_event.is_set():
			raise BuildCancelledError("Build cancelled after the active operation completed.")
