document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("kandidatenForm");

  // Prevent classic form submission
  form.addEventListener("submit", function(e) {
    e.preventDefault();
  });

  /* ---------- Load by ID ---------------------------------- */
  const idInput = document.getElementById("kandidat_id");
  const loadBtn = document.getElementById("loadFromCRM");

  const getTS = (id) => {
    const el = document.getElementById(id);
    return el?.tomselect ?? null;
  };

  loadBtn.addEventListener("click", async () => {
    const kid = idInput.value.trim();
    if (!kid) {
      alert("Bitte eine Kandidaten-ID eingeben!");
      return;
    }

    try {
      const r = await fetch(`/api/kandidat/${kid}`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);

      const d = await r.json();
      fillForm(d);
      showNotice("Daten erfolgreich geladen!", "is-success");
    } catch (e) {
      console.error(e);
      showNotice("Fehler beim Importieren der Daten.", "is-danger");
    }
  });

  /* ---------- Save ---------------------------------------- */
  const submitBtn = document.getElementById("submitButton");

  submitBtn?.addEventListener("click", () => {
    const fd = new FormData(form);

    fetch("/api/submit", {
      method: "POST",
      body: fd,
    })
      .then((r) => r.json())
      .then((res) => {
        const cls = res.status === "success" ? "is-success" : "is-danger";
        showNotice(res.message || "Unbekannte Antwort", cls);
      })
      .catch((err) => {
        console.error(err);
        showNotice("Technischer Fehler beim Speichern.", "is-danger");
      });
  });

  /* ---------- Fill form -------------------------------- */
  function fillForm(data) {
    // Helper to set value by name
    const setVal = (name, val = "") => {
      const el = document.querySelector(`[name="${name}"]`);
      if (el) el.value = val || "";
    };

    // Helper to set radio buttons
    const setRadio = (name, value) => {
      const radios = document.querySelectorAll(`[name="${name}"]`);
      radios.forEach((radio) => {
        radio.checked = radio.value === value;
      });
    };

    function formatGermanNumber(value) {
      if (!value) return "";
      return Number(value).toLocaleString("de-DE");
    }
    // Set basic values
    setVal("vorname", data.vorname);
    setVal("nachname", data.nachname);
    setVal("email", data.email);
    setVal("phone", data.telefon);
    setVal("kandidat_slug", data.slug);
    setVal("consultant", data.consultant);
    setVal("xing_link", data.xing);
    setVal("linkedin_link", data.linkedin);
    setVal("cv_link", data.cv_link);
    setVal("anstellungsart", data.anstellungsart);
    setVal("wechselmotivation", data.wechselmotivation);
    setVal("current_salary", data.current_salary);
    setVal("expected_salary", data.expected_salary);
    setVal("current_salary_display", formatGermanNumber(data.current_salary));
    setVal("expected_salary_display", formatGermanNumber(data.expected_salary));
    setVal("bonus_amount", data.bonus_amount);
    setVal("bonus_type", data.bonus_type);
    setVal("additional_benefits", data.additional_benefits);
    setVal("key_clients", data.key_clients);
    setVal("nicht_an", data.nicht_an);
    setVal("soll_auf_jeden_fall", data.soll_auf_jeden_fall);
    setVal("avatar", data.avatar);

    setVal("wuensche_an_den_job", data.wuensche_an_den_job);
    setVal("berufliche_erfahrung", data.berufliche_erfahrung);
    setVal("berufserfahrung_in_jahren", data.berufserfahrung_in_jahren);

    setVal("umzugsbereit[]", data.umzugsbereit);
    setVal("relevante_berufserfahrung", data.relevante_berufserfahrung);
    setVal("berufliche_ziele", data.berufliche_ziele);
    setVal("private_ziele", data.private_ziele);
    setVal("sonstiges", data.sonstiges);
    setVal("umgang_mit_rueckschlaegen", data.umgang_mit_rueckschlaegen);
    setVal("weiterentwicklung", data.weiterentwicklung);
    setVal("finanzielle_motivation", data.finanzielle_motivation);
    setVal("erfolgsmethodik_kpis", data.erfolgsmethodik_kpis);
    setVal("wechselkommitment", data.wechselkommitment);
    setVal("wunschklinik", data.wunschklinik);

    setVal(
      "aufhebungsvertrag_wahrscheinlichkeit",
      data.aufhebungsvertrag_wahrscheinlichkeit,
    );
    setVal("verfuegbar_ab", data.verfuegbar_ab?.split("T")[0]); // Date only
    setVal("arbeitgeber_standort", data.arbeitgeber_standort);
    setVal("job_extras", data.job_extras);
    setVal("interview_schwerpunkte", data.interview_schwerpunkte);
    setVal("arbeitgeber_art", data.arbeitgeber_art);
    setVal("arbeitgeber_name", data.arbeitgeber_name);
    setVal("verkehrsmittel", data.verkehrsmittel);
    setVal("current_process", data.current_process);
    setVal("arbeitgeber_lage", data.arbeitgeber_lage);
    setVal("wohnort_plz", data.wohnort_plz);
    setVal("wohnort", data.wohnort);
    setVal("radius", data.radius);
    setVal("all_in_salary", data.all_in_salary);
    setVal("zusatzqualifikation", data.zusatzqualifikation);
    setVal("kuendigungsfrist", data.kuendigungsfrist);
    setVal("branche", data.branche);
    setVal("geschlecht", data.geschlecht?.toString());
    setVal(
      "cv_submission_deadline",
      data.cv_submission_deadline?.split("T")[0],
    );



    // Update city tags ========================================
    // if (data.erreichbare_stadtname) {
    //   cities = data.erreichbare_stadtname
    //     .split(",")
    //     .map((city) => city.trim())
    //     .filter((city) => city);
    //   renderTags();
    // }
    // End of city tags update =================================


    // Set radio buttons
    setRadio("aktiv_suche", data.aktiv_suche);
    setRadio("aktiv_bewerbung", data.aktiv_bewerbung);
    setRadio(
      "weitere_personalvermittlungen",
      data.weitere_personalvermittlungen,
    );
    setRadio("home_office_aktuell", data.home_office_aktuell);
    setRadio("home_office_gewuenscht", data.home_office_gewuenscht);
    setRadio("flexible_arbeitszeiten", data.flexible_arbeitszeiten);
    setRadio("gehalt_erhoehen", data.gehalt_erhoehen);

    // Set TomSelect instances
    const tsZusatz = getTS("zusatzbezeichnungen-select");

    if (tsZusatz) {
      tsZusatz.clear();
      if (data["zusatzbezeichnungen[]"]) {
        tsZusatz.addItems(
          data["zusatzbezeichnungen[]"].split(",").map((s) => s.trim()),
        );
      }
    }


    // Trigger branche change for position filtering
    const brancheSel = document.getElementById("branche-select");
    if (brancheSel) {
      brancheSel.value = data.branche || "";
      brancheSel.dispatchEvent(new Event("change"));
    }
    function setupLinkPreview(inputId, buttonId) {
      const input = document.getElementById(inputId);
      const button = document.getElementById(buttonId);

      function updateButton() {
        const url = input.value.trim();
        if (url && url.startsWith("http")) {
          button.href = url;
          button.style.display = "inline-block";
        } else {
          button.style.display = "none";
        }
      }

      updateButton();
    }

    setupLinkPreview("linkedin_link", "open-linkedin");
    setupLinkPreview("xing_link", "open-xing");
    setupLinkPreview("cv_link", "open-cv");

    // Set position after delay (allow filtering to complete)
    setTimeout(() => {
      const positionSel = document.getElementById("position-select");
      if (positionSel) {
        positionSel.value = data.aktuelle_position || "";
        setVal("kategorie", data.kategorie);
        setVal("aktuelle_position", data.aktuelle_position);
      }
    }, 100);
  }

  /* ---------- Mini-Notification (Bulma) ---------------------- */
  function showNotice(msg, cls = "is-info") {
    const n = Object.assign(document.createElement("div"), {
      className: `notification ${cls}`,
      style: "position:fixed;top:1rem;right:1rem;z-index:1000",
      textContent: msg,
    });
    document.body.appendChild(n);
    setTimeout(() => n.remove(), 3500);
  }
});
