"""Keep website styles outside dynamically mounted question content."""

# Standard Library
import pathlib

# PIP3 modules
import tinycss2


#============================================
def _selector_groups(prelude: list) -> list[str]:
	"""Split selector lists at top-level commas, preserving function arguments."""
	groups = []
	tokens = []
	for token in prelude:
		if token.type == "literal" and token.value == ",":
			groups.append(tinycss2.serialize(tokens).strip())
			tokens = []
		else:
			tokens.append(token)
	groups.append(tinycss2.serialize(tokens).strip())
	return groups


#============================================
def scope_styles(css: str) -> str:
	"""Exclude question content while preserving document-root and asset rules.

	Args:
		css: Website stylesheet text, including nested conditional rules.

	Returns:
		CSS with element selectors scoped outside mounted questions. Root-only
		selectors and asset declarations remain global.
	"""
	parts = []
	for rule in tinycss2.parse_stylesheet(css, skip_whitespace=False, skip_comments=False):
		if rule.type == "qualified-rule":
			selectors = _selector_groups(rule.prelude)
			root_selectors = [selector for selector in selectors if selector in ("html", ":root")]
			scoped_selectors = [selector for selector in selectors if selector not in ("html", ":root")]
			declarations = "{" + tinycss2.serialize(rule.content) + "}"
			# Material groups :root with theme selectors; preserve each root branch.
			if root_selectors:
				parts.append(",".join(root_selectors) + declarations)
			if scoped_selectors:
				text = ",".join(scoped_selectors) + declarations
				parts.append("@scope (:root) to (.selftest-reroll-content) {" + text + "}")
		elif rule.type == "at-rule" and rule.lower_at_keyword in (
			"media", "supports", "container", "layer",
		) and rule.content is not None:
			content = scope_styles(tinycss2.serialize(rule.content))
			parts.append("@" + rule.at_keyword + tinycss2.serialize(rule.prelude) + "{" + content + "}")
		else:
			# Font faces, keyframes and other asset declarations are not element selectors.
			parts.append(rule.serialize())
	result = "".join(parts)
	return result


#============================================
def on_post_build(config: dict) -> None:
	"""Scope copied build stylesheets, leaving canonical sources untouched.

	Args:
		config: MkDocs configuration containing the output directory in site_dir.
	"""
	# ASVS 5.3.2: paths come from trusted build configuration, not submitted filenames.
	stylesheet_dir = pathlib.Path(config["site_dir"]) / "assets" / "stylesheets"
	marker = "/* Website styles exclude self-test content. */\n"
	for stylesheet in sorted(stylesheet_dir.glob("*.css")):
		css = stylesheet.read_text(encoding="utf-8")
		# Dirty development builds may retain already-scoped output files.
		if css.startswith(marker):
			continue
		stylesheet.write_text(marker + scope_styles(css), encoding="utf-8")
