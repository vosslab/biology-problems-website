# Galactobiose Identification Question

<script src="https://unpkg.com/@rdkit/rdkit/dist/RDKit_minimal.js"></script>
<table style="border-collapse: collapse; border: black solid 1px;">
  <tr>
    <th style="background-color: #d3d3d3;">
      Guide to Identifying the Chemical Structures of Macromolecules
    </th>
  </tr>
  <tr>
    <td style="background-color: #e7f5fe;">
      <strong><span style="color: #0a9bf5;">Carbohydrates (monosaccharides)</span></strong>
      <ul style="margin: 3px; font-size: 90%;">
        <li>Should have about the same number of oxygens as carbons.</li>
        <li>Look for hydroxyl groups (&ndash;OH) attached to the carbon atoms.</li>
        <li>Carbonyl groups (C=O) are often present as well.</li>
        <li>Look for the base unit of CH<sub>2</sub>O.</li>
        <li>Larger carbohydrates will form hexagon or pentagon ring-like structures.</li>
      </ul>
    </td>
  </tr>
  <!-- Add remaining rows for Lipids, Proteins, Nucleic Acids, etc. -->
</table>

<canvas id="canvas_0ccf" width="480" height="512"></canvas>
<script>
  initRDKitModule().then(function(instance) {
    RDKitModule = instance;
    console.log("RDKit:" + RDKitModule.version());
    let smiles = "C([C@@H]1[C@@H]([C@@H]([C@H]([C@@H](O1)O[C@H]2[C@H](O[C@H]([C@@H]([C@H]2O)O)O)CO)O)O)O)O";
    let mol = RDKitModule.get_mol(smiles);
    let mdetails = {};
    mdetails["legend"] = "galactobiose";
    mdetails["explicitMethyl"] = true;
    canvas = document.getElementById("canvas_0ccf");
    mol.draw_to_canvas_with_highlights(canvas, JSON.stringify(mdetails));
  });
</script>

## Question
Which one of the four main types of macromolecules is represented by the chemical structure of galactobiose shown above?

### Answers:
- A. **Carbohydrates (monosaccharides)** - **Correct**
- B. **Lipids (fatty acids)** - Incorrect
- C. **Proteins (amino acids and dipeptides)** - Incorrect
- D. **Nucleic acids (nucleobases)** - Incorrect
