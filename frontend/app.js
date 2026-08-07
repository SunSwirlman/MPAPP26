const tabButtons = document.querySelectorAll(".tab-btn");
const tabContents = document.querySelectorAll(".tab-content");
const loading = document.getElementById("loading");
const resultDiv = document.getElementById("result");

tabButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    tabButtons.forEach((b) => b.classList.remove("active"));
    tabContents.forEach((c) => c.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById("tab-" + btn.dataset.tab).classList.add("active");
    resultDiv.innerHTML = "";
  });
});

function setLoading(isLoading) {
  loading.classList.toggle("hidden", !isLoading);
}

function renderError(message) {
  resultDiv.innerHTML = `<div class="result-card"><div class="error-note">Ошибка: ${message}</div></div>`;
}

function renderTextAnalysis(data) {
  resultDiv.innerHTML = `
    <div class="result-card">
      <h3>Сильные стороны</h3><ul>${data.strengths.map((s) => `<li>${s}</li>`).join("")}</ul>
      <h3>Слабые стороны</h3><ul>${data.weaknesses.map((s) => `<li>${s}</li>`).join("")}</ul>
      <h3>Уникальные предложения</h3><ul>${data.unique_offers.map((s) => `<li>${s}</li>`).join("")}</ul>
      <h3>Рекомендации</h3><ul>${data.recommendations.map((s) => `<li>${s}</li>`).join("")}</ul>
      <h3>Резюме</h3><p>${data.summary}</p>
    </div>`;
}

function renderImageAnalysis(data) {
  resultDiv.innerHTML = `
    <div class="result-card">
      <h3>Описание <span class="score-badge">visual_style: ${data.visual_style_score}/10</span><span class="score-badge">design: ${data.design_score}/10</span></h3>
      <p>${data.description}</p>
      <h3>Маркетинговые инсайты</h3><ul>${data.marketing_insights.map((s) => `<li>${s}</li>`).join("")}</ul>
      <h3>Анализ визуального стиля</h3><p>${data.visual_style_analysis}</p>
      <h3>Потенциал анимации</h3><p>${data.animation_potential}</p>
      <h3>Рекомендации</h3><ul>${data.recommendations.map((s) => `<li>${s}</li>`).join("")}</ul>
    </div>`;
}

function renderParseResult(data) {
  let html = `
    <div class="result-card">
      <h3>${data.title || "(без title)"}</h3>
      <p><b>H1:</b> ${data.h1 || "—"}</p>
      <p><b>Первый абзац:</b> ${data.first_paragraph || "—"}</p>
    </div>`;
  if (data.analysis) {
    resultDiv.innerHTML = html;
    renderTextAnalysis(data.analysis);
  } else {
    resultDiv.innerHTML = html;
  }
}

document.getElementById("analyze-text-btn").addEventListener("click", async () => {
  const text = document.getElementById("text-input").value.trim();
  const competitor_name = document.getElementById("competitor-name").value.trim() || null;
  if (!text) return renderError("Введите текст");

  setLoading(true);
  resultDiv.innerHTML = "";
  try {
    const resp = await fetch("/analyze/text", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, competitor_name }),
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.detail || "неизвестная ошибка");
    renderTextAnalysis(data);
  } catch (e) {
    renderError(e.message);
  } finally {
    setLoading(false);
  }
});

document.getElementById("analyze-image-btn").addEventListener("click", async () => {
  const fileInput = document.getElementById("image-input");
  if (!fileInput.files.length) return renderError("Выберите изображение");

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  setLoading(true);
  resultDiv.innerHTML = "";
  try {
    const resp = await fetch("/analyze/image", { method: "POST", body: formData });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.detail || "неизвестная ошибка");
    renderImageAnalysis(data);
  } catch (e) {
    renderError(e.message);
  } finally {
    setLoading(false);
  }
});

document.getElementById("parse-btn").addEventListener("click", async () => {
  const url = document.getElementById("parse-url").value.trim();
  if (!url) return renderError("Введите URL");

  setLoading(true);
  resultDiv.innerHTML = "";
  try {
    const resp = await fetch("/parse/demo", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.detail || "неизвестная ошибка");
    renderParseResult(data);
  } catch (e) {
    renderError(e.message);
  } finally {
    setLoading(false);
  }
});

document.getElementById("load-history-btn").addEventListener("click", async () => {
  const resp = await fetch("/history");
  const data = await resp.json();
  const list = document.getElementById("history-list");
  list.innerHTML = data
    .slice()
    .reverse()
    .map(
      (e) =>
        `<div class="history-item"><b>${e.operation_type}</b> — ${e.input_summary} <i>(${e.timestamp})</i></div>`
    )
    .join("") || "<p>История пуста</p>";
});

document.getElementById("clear-history-btn").addEventListener("click", async () => {
  await fetch("/history", { method: "DELETE" });
  document.getElementById("history-list").innerHTML = "<p>История очищена</p>";
});
