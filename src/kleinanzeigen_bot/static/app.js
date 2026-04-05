/**
 * Kleinanzeigen-Bot – Frontend-Logik
 *
 * Verwaltet: Bild-Upload, KI-Analyse, Artikel-Editor, Batch-Veröffentlichung
 */

const state = {
    articles: [],
    currentFiles: null,
};

// DOM-Elemente
const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("file-input");
const imagePreview = document.getElementById("image-preview");
const analyzeBtn = document.getElementById("analyze-btn");
const progressSection = document.getElementById("progress-section");
const progressFill = document.getElementById("progress-fill");
const progressText = document.getElementById("progress-text");
const articlesSection = document.getElementById("articles-section");
const articlesList = document.getElementById("articles-list");
const addMoreBtn = document.getElementById("add-more-btn");
const publishAllBtn = document.getElementById("publish-all-btn");
const resultSection = document.getElementById("result-section");
const resultList = document.getElementById("result-list");
const resetBtn = document.getElementById("reset-btn");
const healthStatus = document.getElementById("health-status");

// -- Initialisierung --

document.addEventListener("DOMContentLoaded", () => {
    checkHealth();
    setupDropZone();
    setupButtons();
});

// -- Health-Check --

async function checkHealth() {
    try {
        const res = await fetch("/api/health");
        const data = await res.json();
        if (data.ollama.available) {
            healthStatus.textContent = "KI bereit";
            healthStatus.className = "status-indicator status-ok";
        } else {
            healthStatus.textContent = "KI nicht verfügbar";
            healthStatus.className = "status-indicator status-error";
        }
    } catch {
        healthStatus.textContent = "Server nicht erreichbar";
        healthStatus.className = "status-indicator status-error";
    }
}

// -- Drag & Drop --

function setupDropZone() {
    dropZone.addEventListener("click", () => fileInput.click());
    fileInput.addEventListener("change", handleFiles);

    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.classList.add("drag-over");
    });

    dropZone.addEventListener("dragleave", () => {
        dropZone.classList.remove("drag-over");
    });

    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.classList.remove("drag-over");
        fileInput.files = e.dataTransfer.files;
        handleFiles();
    });
}

function handleFiles() {
    const files = fileInput.files;
    if (!files || files.length === 0) return;

    state.currentFiles = files;
    imagePreview.innerHTML = "";

    for (const file of files) {
        const img = document.createElement("img");
        img.src = URL.createObjectURL(file);
        img.alt = file.name;
        imagePreview.appendChild(img);
    }

    analyzeBtn.disabled = false;
}

// -- Buttons --

function setupButtons() {
    analyzeBtn.addEventListener("click", analyzeImages);
    addMoreBtn.addEventListener("click", addMoreArticles);
    publishAllBtn.addEventListener("click", publishAll);
    resetBtn.addEventListener("click", resetApp);
}

// -- Analyse --

async function analyzeImages() {
    if (!state.currentFiles) return;

    const uploadSection = document.getElementById("upload-section");
    uploadSection.hidden = true;
    progressSection.hidden = false;
    progressFill.style.width = "20%";
    progressText.textContent = "Bilder werden hochgeladen...";

    const formData = new FormData();
    for (const file of state.currentFiles) {
        formData.append("files", file);
    }

    try {
        progressFill.style.width = "40%";
        progressText.textContent = "KI analysiert Bilder...";

        const res = await fetch("/api/analyze", {
            method: "POST",
            body: formData,
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Analyse fehlgeschlagen");
        }

        progressFill.style.width = "80%";
        progressText.textContent = "Preise werden recherchiert...";

        const data = await res.json();

        progressFill.style.width = "100%";
        progressText.textContent = "Fertig!";

        // Artikel hinzufügen
        state.articles.push({
            ...data,
            price_cents: data.price_estimate.suggested_price_cents,
            price_type: "NEGOTIABLE",
        });

        // Nach kurzer Verzögerung zum Editor wechseln
        setTimeout(() => {
            progressSection.hidden = true;
            showArticlesEditor();
        }, 500);
    } catch (err) {
        progressFill.style.width = "0";
        progressText.textContent = `Fehler: ${err.message}`;
        setTimeout(() => {
            progressSection.hidden = true;
            uploadSection.hidden = false;
        }, 3000);
    }

    // Upload-State zurücksetzen
    state.currentFiles = null;
    fileInput.value = "";
    imagePreview.innerHTML = "";
    analyzeBtn.disabled = true;
}

// -- Artikel-Editor --

function showArticlesEditor() {
    articlesSection.hidden = false;
    renderArticles();
    publishAllBtn.disabled = state.articles.length === 0;
}

function renderArticles() {
    articlesList.innerHTML = "";

    state.articles.forEach((article, index) => {
        const card = document.createElement("div");
        card.className = "article-card";
        card.innerHTML = `
            <h3>Artikel ${index + 1}</h3>
            <div class="article-images">
                ${article.images.map((name) =>
                    `<img src="#" alt="${name}" title="${name}">`
                ).join("")}
            </div>
            <div class="form-group">
                <label for="title-${index}">Titel (max. 70 Zeichen)</label>
                <input type="text" id="title-${index}" maxlength="70"
                       value="${escapeHtml(article.vision.title)}"
                       data-index="${index}" data-field="title">
            </div>
            <div class="form-group">
                <label for="desc-${index}">Beschreibung</label>
                <textarea id="desc-${index}" maxlength="4000"
                          data-index="${index}" data-field="description"
                >${escapeHtml(article.vision.description)}</textarea>
            </div>
            <div class="form-group">
                <label for="price-${index}">Preis (EUR)</label>
                <input type="number" id="price-${index}" min="0" step="1"
                       value="${Math.round(article.price_cents / 100)}"
                       data-index="${index}" data-field="price">
                <div class="price-info ${article.price_estimate.confidence}">
                    Schätzung: ${formatPrice(article.price_estimate.suggested_price_cents)}
                    (${formatPrice(article.price_estimate.min_price_cents)} - ${formatPrice(article.price_estimate.max_price_cents)})
                    | Konfidenz: ${article.price_estimate.confidence}
                    | ${article.price_estimate.source_count} Quellen
                </div>
            </div>
            <div class="form-group">
                <label for="ptype-${index}">Preisart</label>
                <select id="ptype-${index}" data-index="${index}" data-field="price_type">
                    <option value="NEGOTIABLE" ${article.price_type === "NEGOTIABLE" ? "selected" : ""}>VB (Verhandlungsbasis)</option>
                    <option value="FIXED" ${article.price_type === "FIXED" ? "selected" : ""}>Festpreis</option>
                    <option value="GIVEAWAY" ${article.price_type === "GIVEAWAY" ? "selected" : ""}>Zu verschenken</option>
                </select>
            </div>
            <div class="form-group">
                <label for="cat-${index}">Kategorie</label>
                <input type="text" id="cat-${index}" readonly
                       value="${escapeHtml(article.category.category_path)}"
                       data-index="${index}">
            </div>
            <button class="btn btn-secondary" onclick="removeArticle(${index})" style="margin-top:8px">
                Artikel entfernen
            </button>
        `;
        articlesList.appendChild(card);
    });

    // Event-Listener für Eingabefelder
    articlesList.querySelectorAll("input, textarea, select").forEach((el) => {
        el.addEventListener("change", handleFieldChange);
    });
}

function handleFieldChange(e) {
    const index = parseInt(e.target.dataset.index);
    const field = e.target.dataset.field;
    if (field === undefined || isNaN(index)) return;

    const article = state.articles[index];
    switch (field) {
        case "title":
            article.vision.title = e.target.value;
            break;
        case "description":
            article.vision.description = e.target.value;
            break;
        case "price":
            article.price_cents = parseInt(e.target.value) * 100;
            break;
        case "price_type":
            article.price_type = e.target.value;
            break;
    }
}

function removeArticle(index) {
    state.articles.splice(index, 1);
    renderArticles();
    publishAllBtn.disabled = state.articles.length === 0;
}

function addMoreArticles() {
    articlesSection.hidden = true;
    const uploadSection = document.getElementById("upload-section");
    uploadSection.hidden = false;
}

// -- Veröffentlichen --

async function publishAll() {
    if (state.articles.length === 0) return;

    articlesSection.hidden = true;
    resultSection.hidden = false;
    resultList.innerHTML = "";

    for (const article of state.articles) {
        const resultItem = document.createElement("div");
        resultItem.className = "result-item";
        resultItem.innerHTML = `<span class="result-icon">...</span> ${escapeHtml(article.vision.title)}`;
        resultList.appendChild(resultItem);

        try {
            const res = await fetch("/api/publish", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    upload_id: article.upload_id,
                    title: article.vision.title,
                    description: article.vision.description,
                    price_cents: article.price_cents,
                    price_type: article.price_type,
                    category_id: article.category.category_id,
                    category_path: article.category.category_path,
                }),
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Veröffentlichung fehlgeschlagen");
            }

            resultItem.className = "result-item success";
            resultItem.innerHTML = `<span class="result-icon">&#10004;</span> ${escapeHtml(article.vision.title)} - Veröffentlicht`;
        } catch (err) {
            resultItem.className = "result-item error";
            resultItem.innerHTML = `<span class="result-icon">&#10008;</span> ${escapeHtml(article.vision.title)} - ${escapeHtml(err.message)}`;
        }
    }
}

// -- Reset --

function resetApp() {
    state.articles = [];
    state.currentFiles = null;
    fileInput.value = "";
    imagePreview.innerHTML = "";
    analyzeBtn.disabled = true;

    resultSection.hidden = true;
    articlesSection.hidden = true;
    progressSection.hidden = true;
    document.getElementById("upload-section").hidden = false;
}

// -- Hilfsfunktionen --

function formatPrice(cents) {
    if (!cents || cents === 0) return "–";
    return `${Math.round(cents / 100)} €`;
}

function escapeHtml(text) {
    if (!text) return "";
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}
