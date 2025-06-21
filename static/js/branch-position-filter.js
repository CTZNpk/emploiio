document.addEventListener("DOMContentLoaded", function() {
  const brancheSelect = document.getElementById("branche-select");
  const positionSelect = document.getElementById("position-select");
  const aktuelle_fachebereiche = document.getElementById(
    "aktuelle-fachbereiche-select",
  );
  const positionFeld = positionSelect.closest(".field");

  const fachbereichFeld = document
    .getElementById("fachbereiche-select")
    ?.closest(".field");
  const zusatzbezeichnungFeld = document
    .getElementById("zusatzbezeichnungen-select")
    ?.closest(".field");
  const zusatzqualifikationFeld = document
    .querySelector('input[name="zusatzqualifikation"]')
    ?.closest(".field");
  const wuenscheFeld = document
    .querySelector('[name="wuensche_an_den_job"]')
    ?.closest(".field");

  const erfahrungFeld = document
    .querySelector('[name="berufliche_erfahrung"]')
    ?.closest(".field");

  function updateFields() {
    const selected = brancheSelect.value;
    const isMed = selected === "emploio Med";

    // Felder ein-/ausblenden
    if (fachbereichFeld)
      fachbereichFeld.style.display = isMed ? "block" : "none";
    if (zusatzbezeichnungFeld)
      zusatzbezeichnungFeld.style.display = isMed ? "block" : "none";
    if (zusatzqualifikationFeld)
      zusatzqualifikationFeld.style.display = isMed ? "block" : "none";
    if (positionFeld) positionFeld.style.display = selected ? "block" : "none";
    if (wuenscheFeld) wuenscheFeld.style.display = isMed ? "block" : "none";

    if (erfahrungFeld) erfahrungFeld.style.display = isMed ? "block" : "none";
    if (aktuelle_fachebereiche)
      aktuelle_fachebereiche.style.display = isMed ? "block" : "none";

    // Positionen setzen
    positionSelect.innerHTML = '<option value="">Bitte wählen</option>';
    const options = window.positionsByBranche?.[selected] || [];
    options.forEach((pos) => {
      const opt = document.createElement("option");
      opt.value = pos;
      opt.textContent = pos;
      positionSelect.appendChild(opt);
    });
  }

  brancheSelect.addEventListener("change", updateFields);
  updateFields(); // beim Laden ausführen
});
