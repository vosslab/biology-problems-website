"use strict";

(function () {
	// ASVS 3.6.1: pinned dependencies and converter bytes are served by this site.
	const assetBase = new URL("../", document.currentScript.src);
	let enginePromise;
	let rendererPromise;
	let rdkitPromise;
	const banks = new Map();

	function sameOrigin(url) {
		if (url.origin !== window.location.origin) {
			throw new Error("Question data must come from this site.");
		}
		return url;
	}

	async function bytes(url) {
		const response = await fetch(sameOrigin(url));
		if (!response.ok) { throw new Error("Could not load question data. Try again."); }
		return new Uint8Array(await response.arrayBuffer());
	}

	function engine() {
		if (!enginePromise) {
			enginePromise = (async function () {
				const api = await import(new URL("qti_wasm/src/index.js", assetBase).href);
				await api.initialize(await bytes(new URL("qti_wasm/generated/qti_wasm_bg.wasm", assetBase)));
				return api;
			}()).catch(function (error) { enginePromise = undefined; throw error; });
		}
		return enginePromise;
	}

	function renderer() {
		if (!rendererPromise) {
			const url = new URL("package_render/modern_screenshot.mjs", assetBase);
			rendererPromise = import(url.href).catch(function (error) {
				rendererPromise = undefined;
				throw error;
			});
		}
		return rendererPromise;
	}

	function rdkit() {
		if (!rdkitPromise) {
			rdkitPromise = (async function () {
				if (!window.initRDKitModule) {
					await new Promise(function (resolve, reject) {
						const script = document.createElement("script");
						script.src = new URL("package_render/rdkit.js", assetBase).href;
						script.onload = resolve;
						script.onerror = function () {
							script.remove();
							reject(new Error("Could not load molecule drawing. Try again."));
						};
						document.head.appendChild(script);
					});
				}
				return window.initRDKitModule({ locateFile: function () {
					return new URL("package_render/rdkit.wasm", assetBase).href;
				} });
			}()).catch(function (error) { rdkitPromise = undefined; throw error; });
		}
		return rdkitPromise;
	}

	async function bankData(url) {
		if (!banks.has(url.href)) {
			const pending = (async function () {
				const source = await bytes(url);
				const doc = new DOMParser().parseFromString(new TextDecoder().decode(source), "text/html");
				const names = new Set(Array.from(doc.querySelectorAll("img[src]")).map(function (img) {
					return img.getAttribute("src");
				}).filter(function (src) { return !/^(data:|https?:|\/\/)/i.test(src); }));
				const companions = await Promise.all(Array.from(names).map(async function (name) {
					return { name: name, bytes: await bytes(new URL(name, url)) };
				}));
				return { kind: "file", name: url.pathname.split("/").pop(), bytes: source, companions };
			}()).catch(function (error) { banks.delete(url.href); throw error; });
			banks.set(url.href, pending);
		}
		return banks.get(url.href);
	}

	function successful(result) {
		if (result.status !== "success") { throw new Error(result.error.message); }
		return result;
	}

	async function renderFrame(wrapper) {
		const frame = document.createElement("iframe");
		frame.setAttribute("aria-hidden", "true");
		frame.setAttribute("sandbox", "allow-same-origin");
		frame.tabIndex = -1;
		// Keep native 1280px layout; visibility/display:none prevents useful capture geometry.
		frame.style.cssText = "position:fixed;left:-100000px;top:0;width:1280px;height:720px;border:0";
		await new Promise(function (resolve) {
			frame.onload = resolve;
			frame.srcdoc = wrapper;
			document.body.appendChild(frame);
		});
		return frame;
	}

	function pngBytes(dataUrl) {
		const binary = atob(dataUrl.split(",")[1]);
		return Uint8Array.from(binary, function (character) { return character.charCodeAt(0); });
	}

	async function canvasPng(canvas) {
		const blob = await new Promise(function (resolve, reject) {
			canvas.toBlob(function (value) {
				if (!value) { reject(new Error("Could not draw a molecule. Try again.")); return; }
				resolve(value);
			}, "image/png");
		});
		return new Uint8Array(await blob.arrayBuffer());
	}

	function drawingDetails(module, molecule, spec) {
		const details = { ...spec.drawingDetails, bonds: [...spec.drawingDetails.bonds] };
		if (!spec.peptideQuery) { return details; }
		// QPM supplies the query and atom pair; the host only executes the RDKit operations.
		const query = module.get_qmol(spec.peptideQuery.smarts);
		if (!query) { throw new Error("Could not read a molecule highlight rule."); }
		try {
			const matches = JSON.parse(molecule.get_substruct_matches(query));
			const bonds = JSON.parse(molecule.get_json()).molecules[0].bonds;
			for (const match of Array.isArray(matches) ? matches : []) {
				const pair = spec.peptideQuery.bondAtoms.map(index => match.atoms[index]);
				const index = bonds.findIndex(function (bond) {
					return bond.atoms.includes(pair[0]) && bond.atoms.includes(pair[1]);
				});
				if (index >= 0) { details.bonds.push(index); }
			}
			if (!details.bonds.length) { throw new Error("A molecule highlight rule matched no bonds."); }
			return details;
		} finally { query.delete(); }
	}

	async function drawCanvas(doc, spec) {
		const canvas = doc.createElement("canvas");
		canvas.width = spec.width;
		canvas.height = spec.height;
		const module = await rdkit();
		const molecule = module.get_mol(spec.smiles);
		if (!molecule) { throw new Error("Could not read a molecule in this question bank."); }
		try {
			molecule.draw_to_canvas_with_highlights(canvas, JSON.stringify(drawingDetails(module, molecule, spec)));
			return { png: await canvasPng(canvas), width: spec.width, height: spec.height };
		} finally { molecule.delete(); }
	}

	async function drawTable(doc, job, completed) {
		const root = doc.getElementById("qti-render-root");
		const template = doc.createElement("template");
		template.innerHTML = job.html;
		// The source-owned wrapper also blocks scripts; authored drawing uses the typed canvas API.
		template.content.querySelectorAll("script,iframe,frame,object,embed,base,meta,link").forEach(function (node) {
			node.remove();
		});
		template.content.querySelectorAll("img[src^='qti-render:']").forEach(function (image) {
			const id = image.getAttribute("src").slice("qti-render:".length);
			const rendered = completed.get(id);
			if (!rendered) { throw new Error("A question image has not finished drawing."); }
			image.src = rendered.dataUrl;
		});
		root.replaceChildren(template.content);
		await doc.fonts.ready;
		await Promise.all(Array.from(root.querySelectorAll("img")).map(function (image) {
			return image.decode();
		}));
		const table = root.querySelector("table");
		if (!table) { throw new Error("A question table could not be drawn."); }
		const bounds = table.getBoundingClientRect();
		const block = doc.createElement("div");
		block.style.cssText = `display:block;width:${bounds.width}px;height:${bounds.height}px;background:white`;
		table.style.width = `${bounds.width}px`;
		table.replaceWith(block);
		block.appendChild(table);
		const library = await renderer();
		const dataUrl = await library.domToPng(block, {
			scale: 1, backgroundColor: "#fff", timeout: 5000,
			onCloneNode: function (clone) {
				// A cloned table's computed height stretches caption rows; retain natural row layout.
				clone.querySelectorAll("table").forEach(function (item) { item.style.height = "auto"; });
			},
		});
		return { png: pngBytes(dataUrl), width: bounds.width, height: bounds.height, dataUrl };
	}

	async function renderJobs(plan, update) {
		const frame = await renderFrame(plan.wrapper);
		const completed = new Map();
		const hashes = new Map();
		const renders = [];
		// Source-owned dependencies refer to canvas jobs; draw these before outer tables.
		const jobs = plan.jobs.filter(job => job.kind === "canvas")
			.concat(plan.jobs.filter(job => job.kind === "table"));
		try {
			for (const job of jobs) {
				let rendered = hashes.get(job.contentHash);
				if (!rendered) {
					rendered = job.kind === "canvas"
						? await drawCanvas(frame.contentDocument, job.canvasSpec)
						: await drawTable(frame.contentDocument, job, completed);
					if (!rendered.dataUrl) {
						const blob = new Blob([rendered.png], { type: "image/png" });
						rendered.dataUrl = await new Promise(function (resolve, reject) {
							const reader = new FileReader();
							reader.onload = function () { resolve(reader.result); };
							reader.onerror = reject;
							reader.readAsDataURL(blob);
						});
					}
					hashes.set(job.contentHash, rendered);
				}
				completed.set(job.id, rendered);
				renders.push({ id: job.id, png: rendered.png, width: rendered.width, height: rendered.height });
				update(renders.length / jobs.length, `Drawing question images: ${renders.length} of ${jobs.length}...`);
			}
			return renders;
		} finally { frame.remove(); }
	}

	function deliver(result, button, tab) {
		const artifact = result.artifact;
		if (!artifact || artifact.kind !== "file") { throw new Error("No download was generated."); }
		const html = button.dataset.format === "human_readable";
		const url = URL.createObjectURL(new Blob([artifact.primary.bytes], {
			type: html ? "text/html;charset=utf-8" : "application/zip",
		}));
		if (html) {
			tab.location.href = url;
		} else {
			const link = document.createElement("a");
			link.href = url;
			link.download = button.dataset.filename;
			document.body.appendChild(link);
			link.click();
			link.remove();
		}
		// Allow the browser time to consume the Blob before releasing it.
		setTimeout(function () { URL.revokeObjectURL(url); }, 60000);
	}

	async function download(button) {
		const row = button.closest(".button-container");
		const status = row.querySelector(".qti-package-status");
		const progress = row.querySelector(".qti-package-progress");
		const buttons = row.querySelectorAll(".qti-package-download");
		let tab;
		function update(value, message) {
			progress.value = value;
			// ASVS 3.2.2: failure messages are displayed as text.
			status.textContent = message;
		}
		buttons.forEach(function (item) { item.disabled = true; });
		progress.hidden = false;
		update(0, "Loading question bank...");
		try {
			if (button.dataset.format === "human_readable") {
				// Reserve the tab during the click so asynchronous loading retains popup permission.
				tab = window.open("", "_blank");
				if (!tab) { throw new Error("Allow a new tab for this site, then try again."); }
				tab.opener = null;
			}
			const url = sameOrigin(new URL(button.dataset.bbq, window.location.href));
			const loaded = await Promise.all([engine(), bankData(url)]);
			const request = {
				inputFormat: "bbq_text_upload", outputFormat: button.dataset.format, input: loaded[1],
			};
			const api = loaded[0];
			let result;
			if (request.outputFormat === "blackboard_export_zip") {
				update(0, "Preparing question images...");
				const plan = successful(api.planRenderJobs(request));
				if (plan.jobs.length) {
					const renders = await renderJobs(plan, update);
					update(1, "Building download...");
					result = api.finishConvert(request, renders);
				} else { result = api.convert(request); }
			} else {
				update(0, "Building download...");
				result = api.convert(request);
			}
			deliver(successful(result), button, tab);
			update(1, tab ? "Question bank opened in a new tab." : "Download ready.");
		} catch (error) {
			if (tab && !tab.closed) { tab.close(); }
			update(0, (error.message || "Could not build this download.") + " Select the button to retry.");
		} finally {
			progress.hidden = true;
			buttons.forEach(function (item) { item.disabled = false; });
		}
	}

	// Delegation also handles MkDocs navigation updates without duplicate listeners.
	document.addEventListener("click", function (event) {
		const button = event.target.closest(".qti-package-download");
		if (button && !button.disabled) { event.preventDefault(); download(button); }
	});
}());
