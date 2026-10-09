# Blackboard render visual review

Date: 2026-10-09. Fresh visual review of Phase 3a against
[i-want-to-explore-optimized-spindle.md](../i-want-to-explore-optimized-spindle.md).

## Verdict and scope

Current D11 candidate: modern-screenshot at scale 1 with full-color PNGs uniformly across banks
in Chromium and Firefox. PASS for the six representative jobs directly inspected in the D11
follow-up below. The earlier 29-job geometry/content review remains historical evidence;
this follow-up does not claim direct inspection of all 58 full-color calibration images.
Use 64-color quantization only as an experiment comparison: the guide demonstrates visible
heading hue and edge losses that full-color capture avoids.

### Earlier quantized review

PASS for scientific-content fidelity and readable labels in the 29 inspected calibration jobs
using modern-screenshot at scale 1 with a 64-color palette in Chromium and Firefox. Standalone
canvases use the experiment's direct RDKit.js canvas capture path. No inspected accepted image
loses a scientific label, band, fraction component, table value, or chemical/tree connection.
The palette changes some guide heading colors visibly; this is a cosmetic limitation in the
inspected guide, whose named categories and background groups remain distinguishable.

This verdict covers the selected calibration configuration and corpus. It does not establish
Blackboard Ultra display size, grading, full-bank visual acceptance, WebKit acceptance, or the
end-to-end gate for option D. The user must still import browser-built ZIPs into Ultra and check
size and grading.

## Evidence and method

Read repository instructions and Markdown/repository style conventions before review. Applied
"Use the scientific method" and "Ground requirements in actual needs": judge visible scientific
information, without a pixel-distance, hash-distance, or byte-size acceptance cutoff.

Evidence root: `tests/_temp/blackboard_browser_render/`. Reviewed the plan, current spike report,
gallery structure, calibration inventory, acceptance filenames, and summary measurements.
Inspected the actual local PNGs with `view_image`, rather than inferring fidelity from successful
capture status or measurement scores.

For every ID below, inspected these three paths:

- `native/{id}.png`
- `quantized/{id}-chromium-modern-1-acceptance.png`
- `quantized/{id}-firefox-modern-1-acceptance.png`

Coverage is 29 native references and 58 selected browser PNGs, across ten scientific classes in
nine banks. The guide and nested table+canvas classes overlap in the macromolecule bank.

| Bank | Inspected IDs |
| --- | --- |
| Gel | `gel-0001`, `gel-0002`, `gel-0003` |
| Punnett | `punnett-0001`, `punnett-0002`, `punnett-0003` |
| Chi-square | `chi_square-0001`, `chi_square-0002`, `chi_square-0003` |
| Gene tree | `gene_tree-0001`, `gene_tree-0002`, `gene_tree-0003`, `gene_tree-0427` |
| Tetrad | `tetrad-0001`, `tetrad-0002`, `tetrad-0003` |
| Macromolecule | `macromolecule-0001`, `macromolecule-0002`, `macromolecule-0003` |
| Projection | `projection-0001`, `projection-0002`, `projection-0003`, `projection-0008` |
| Agglutination | `agglutination-0001`, `agglutination-0002`, `agglutination-0003` |
| RDKit canvas | `rdkit-0001`, `rdkit-0002`, `rdkit-0003` |

Also inspected raw `renders/macromolecule-0001-{engine}-modern-1-acceptance.png` for both browsers
to distinguish palette effects from browser layout, and the two preserved initial failures:
`initial_renders/gene_tree-0002-chromium-modern-2.png` and
`initial_renders/tetrad-0003-firefox-snapdom-2.png`.

Used Pillow read-only metadata to confirm selected raster dimensions and palette counts.
Native table images are approximately twice scale-1 browser dimensions; direct canvas images
remain 480 x 320 in both native and browser output. Compared table layout at the implied native
DPR-2 CSS size: the native raster's larger displayed size alone is not evidence of lost content.
No derivative images or source changes were made for this review.

## Criterion-specific findings

The observations below describe visible facts; the final column records the review judgment.

| Scientific class | Observed native/browser comparison | Judgment |
| --- | --- | --- |
| Box-shadow gel | All three mother/child/five-male row patterns retain their broad and narrow blue bands, horizontal alignments, separation, and row labels. Soft halos remain visible. Firefox increases row spacing slightly. | PASS: band comparison remains possible; no disappeared or merged scientific band observed. |
| Punnett square | All three grids retain header allele case, four offspring cells, AA versus Aa lettering, and black versus gray cell fills. | PASS: genotype and cell assignment are unambiguous. |
| Chi-square data | Critical-value probabilities, degrees of freedom, and all displayed entries remain readable. Both calculation tables retain phenotype text, observed/expected counts, squared terms, statistics, and sum. Firefox changes row height. | PASS: no cropped value or altered column assignment. This is fidelity review, not validation of authored statistical formulas. |
| LEVEL_4 gene tree | All four jobs retain the matrix/diagrams and captions. The three trees preserve terminal label order and branching pairings, including the distinct `6twohead3`, `4comb+pair4`, and `6comb` patterns. | PASS: no changed connectivity or missing terminal/caption. |
| Tetrad | The genotype grid retains all four symbols per set, allele/color backgrounds, counts 4,880 / 3,948 / 172, and total 9,000. Both small fractions retain complete numerators, horizontal rules, and denominator 9,000. | PASS: fraction and grid information remains readable, including `86 + 516`. |
| Macromolecule guide | All five named sections and every bullet remain visible, including subscripts, superscripts, and the bottom DNA bullet. Quantization changes purple phosphate heading text toward muted brown/mauve and reduces orange lipid heading saturation; Chromium heading edges look less even. Firefox's table is taller. | PASS for scientific information; exact palette/typographic fidelity is weaker. Named categories and separate background blocks preserve grouping. |
| Nested table+canvas | Arachidic acid and Lys-Leu structures retain chain paths, atom labels, terminal groups, double bonds, and the peptide's solid/hashed stereobonds. Adjacent information tables retain names, formulas, numerical values, units, and the peptide canvas caption. | PASS: no lost canvas or shifted scientific association. Small atom lettering in the long fatty-acid drawing is inherently tiny at the authored display size. |
| Fischer/Haworth | Fischer H/OH left-right placement and terminal groups are retained. All three Haworth variants retain substituent placement, ring oxygen, thin/dashed/heavy bond distinctions, and CH2OH subscripts. Firefox changes vertical spacing but preserves each connection and substituent. | PASS: stereochemical distinctions remain interpretable. |
| Agglutination wells | All three patterns retain A/B/D/control labels, individual small and large clumps, and uniform filled red wells where present. Browser spacing differs slightly; no well crosses its column boundary. | PASS: clumped versus uniform phenotype remains clear. |
| RDKit canvas-only | All three amino-acid drawings retain red oxygen, blue nitrogen, sulfur label, bond multiplicity, ring connectivity, and solid/hashed stereochemical bonds at the same 480 x 320 size. | PASS: atoms and stereochemistry remain distinguishable after quantization. |

## Corrected failures

Observed the original Chromium gene-tree image ending at the label table with its caption
absent. The accepted Chromium and Firefox versions visibly restore the caption and match the
native branch relationships. Observed the original Firefox snapdom fraction wrapping `86 + 516`
onto two lines with the denominator absent. The accepted modern-screenshot images retain a
single numerator line and the full denominator.

These original images fail scientific fidelity. Their failures do not apply to the inspected
accepted configuration. The spike report attributes the caption correction to the documented
clone hook resetting table height to `auto`; this review verifies the visible outcome rather
than auditing that implementation.

## Limitations and recommendation

- No visual review of the remaining full-bank images, all 348 effective calibration settings,
  WebKit, or every raw/scale-2 alternative. The 87 selected images listed above were inspected.
- Native table references contain more raster detail than scale 1. At larger zoom, browser text
  and very small labels will look softer. Normal authored CSS-size readability passes here;
  magnified or high-density display quality is a separate consideration.
- The PNG viewer and metadata establish local image fidelity, not a calibrated display or a
  measured accessibility contrast audit. No numerical contrast measurement was performed.
- The smallest long-chain canvas atom labels deserve attention during Ultra import. Confirm
  that the image is displayed at its intended size and can be enlarged when needed.
- The guide's palette shift is visible but does not encode a changed scientific category in
  this corpus. If exact heading hues become a requirement, compare a larger palette or raw PNG
  for this case; no image/source change is necessary for the present scientific-fidelity gate.
- Preserve the native references, accepted PNGs, and initial failures through the import gate.
  Proceed with the selected Chromium/Firefox configuration for the authorized experiment,
  while keeping the Ultra size/grading gate open.

## D11 full-color follow-up

Date: 2026-10-09. Fresh, narrow review of the chosen full-color candidate. This section
supersedes the earlier palette recommendation while preserving that review's historical scope.
The criterion is preservation of scientific content, color appearance, and readable labels.
No arbitrary pixel-distance or aesthetic redesign criterion is added.

### Directly inspected evidence

Evidence root remains `tests/_temp/blackboard_browser_render/`. Read the existing review,
gallery path/scale conventions, and acceptance metadata. Inspected actual PNGs with
`view_image` for each of these six IDs:

- `macromolecule-0001`: identifying guide, including phosphate and lipid headings.
- `macromolecule-0003`: Lys-Leu nested RDKit canvas and information table.
- `projection-0002`: colored Haworth labels and thin/dashed/heavy bonds.
- `rdkit-0002` and `rdkit-0003`: standalone RDKit atom colors and solid stereobonds.
- `gel-0001`: soft blue bands and mother/child/five-male row labels.

For every listed ID, inspected these exact path patterns:

- `native/{id}.png`
- `renders/{id}-chromium-modern-1-acceptance.png`
- `renders/{id}-firefox-modern-1-acceptance.png`

Also directly compared `quantized/macromolecule-0001-chromium-modern-1-acceptance.png` and
`quantized/macromolecule-0001-firefox-modern-1-acceptance.png` against their full-color captures.
This follow-up therefore views 20 PNGs: six native, twelve full-color, and two quantized.
It does not repeat the earlier 87-image review or claim that all raw alternatives were viewed.

Read-only Pillow metadata confirms RGBA mode for the inspected full-color guide, projection,
standalone RDKit, and gel captures, and palette mode for the two quantized guide derivatives.
Those full-color acceptance records report `ok` with revision
`measured-container-clone-height-auto`. The guide is 602 x 629 in Chromium and 602 x 651 in
Firefox versus native 1205 x 1259. Standalone RDKit stays 480 x 320 in all three paths.
These measurements explain comparison scale; they are not numerical fidelity gates.

### Findings and calls

The middle column records observations; the last column records judgment.

| Criterion | Observed comparison | Call |
| --- | --- | --- |
| Guide heading appearance | Both full-color captures retain distinctly purple phosphate and orange lipid headings matching the native hue families. Chromium's quantized phosphate heading becomes muted brown/mauve and its orange heading becomes pale with less even edges. Firefox's quantized phosphate heading also shifts toward brown/mauve. | PASS for full color. Quantization loses visible appearance and is unsuitable as the uniform appearance-preserving default. |
| Guide small labels | Full-color subscripts in CH2O and NH2, the phosphate subscript/superscript, charge marks, and every bottom-section bullet remain visible and readable. Firefox keeps its previously observed taller layout. | PASS at authored CSS size; no new label or content loss observed. |
| Nested RDKit stereochemistry | Lys-Leu retains red oxygen and blue nitrogen labels, carbon-group subscripts, solid wedge and separate hashed wedge marks, peptide connections, caption, formula, weight, and units in both browsers. | PASS: small labels and both stereo-bond forms remain interpretable. |
| Projection atom colors | Haworth retains blue H, brown OH/HO, red ring oxygen, purple CH2OH, and the pale center label. Substituent positions and thin/dashed/heavy connections remain visible. Firefox retains its slightly taller layout. | PASS: color distinctions and scientific connections survive full-color capture. |
| Standalone RDKit | Both examples retain red O/OH and blue N/NH2 labels, ring/chain connections, double bonds, and solid wedges at the same 480 x 320 raster size as native. | PASS: no observed color or stereochemical information loss. |
| Gel soft bands | Broad and narrow blue bands retain their row patterns, alignment, and soft halos; Mother, Child, and Male 1-5 remain readable. Firefox has slightly larger row spacing. | PASS: no missing/merged band observed and band comparison remains possible. |

### Recommendation and limits

Recommend the uniform modern-screenshot scale-1 full-color candidate for the authorized D11
experiment. Removing palette reduction avoids the demonstrated guide color/edge loss without
introducing per-bank selection rules. Keep quantized derivatives as experiment evidence only.
The prior review already covers scientific geometry across the 29 calibration jobs; the fresh
follow-up checks representative appearance-sensitive cases and does not expand that evidence
into a claim of individually reviewed full-color output for every job.

Full color does not remove the resolution difference between DPR-2 native tables and scale-1
browser tables, nor the observed Firefox spacing differences. The review uses local PNG viewing,
not calibrated display color measurement or a numerical contrast audit. No measurement tool
needed for this scoped visual judgment was unavailable. Source scientific statements, formulas,
and stereochemical assignments are compared for fidelity, not independently revalidated.
Blackboard Ultra size/grading, full-bank visual acceptance, and WebKit remain outside this PASS.
Preserve these evidence images through the separate Ultra import gate.
