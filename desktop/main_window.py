import json

from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from backend.services import openai_service, parsing_service
from backend.services.history_service import history_service
from desktop.worker import AnalysisWorker


def format_analysis(data: dict) -> str:
    lines = []
    if "strengths" in data:
        lines.append("<b>Сильные стороны:</b><ul>" + "".join(f"<li>{s}</li>" for s in data["strengths"]) + "</ul>")
        lines.append("<b>Слабые стороны:</b><ul>" + "".join(f"<li>{s}</li>" for s in data["weaknesses"]) + "</ul>")
        lines.append("<b>Уникальные предложения:</b><ul>" + "".join(f"<li>{s}</li>" for s in data["unique_offers"]) + "</ul>")
        lines.append("<b>Рекомендации:</b><ul>" + "".join(f"<li>{s}</li>" for s in data["recommendations"]) + "</ul>")
        lines.append(f"<b>Резюме:</b> {data['summary']}")
    elif "description" in data:
        lines.append(f"<b>Описание:</b> {data['description']}")
        lines.append(f"<b>Visual style score:</b> {data['visual_style_score']}/10 &nbsp; <b>Design score:</b> {data['design_score']}/10")
        lines.append("<b>Маркетинговые инсайты:</b><ul>" + "".join(f"<li>{s}</li>" for s in data["marketing_insights"]) + "</ul>")
        lines.append(f"<b>Анализ визуального стиля:</b> {data['visual_style_analysis']}")
        lines.append(f"<b>Потенциал анимации:</b> {data['animation_potential']}")
        lines.append("<b>Рекомендации:</b><ul>" + "".join(f"<li>{s}</li>" for s in data["recommendations"]) + "</ul>")
    return "<br>".join(lines)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Competitor Monitor — анализ конкурентов (цифровые аватары)")
        self.resize(760, 640)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self._build_text_tab()
        self._build_image_tab()
        self._build_parse_tab()
        self._build_history_tab()

        self.worker = None

    def _set_busy(self, busy: bool):
        self.tabs.setEnabled(not busy)
        self.statusBar().showMessage("Обрабатываю запрос..." if busy else "Готово")

    def _run_async(self, func, on_done, *args, **kwargs):
        self._set_busy(True)
        self.worker = AnalysisWorker(func, *args, **kwargs)
        self.worker.finished.connect(lambda result: (self._set_busy(False), on_done(result)))
        self.worker.failed.connect(lambda err: (self._set_busy(False), self._show_error(err)))
        self.worker.start()

    def _show_error(self, message: str):
        QMessageBox.critical(self, "Ошибка", message)

    # --- Текст ---
    def _build_text_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        layout.addWidget(QLabel("Название конкурента (опционально):"))
        self.text_name_input = QLineEdit()
        layout.addWidget(self.text_name_input)

        layout.addWidget(QLabel("Текст для анализа:"))
        self.text_input = QTextEdit()
        layout.addWidget(self.text_input)

        btn = QPushButton("Анализировать текст")
        btn.clicked.connect(self._on_analyze_text)
        layout.addWidget(btn)

        self.text_result = QTextBrowser()
        layout.addWidget(self.text_result)

        self.tabs.addTab(widget, "Текст")

    def _on_analyze_text(self):
        text = self.text_input.toPlainText().strip()
        if not text:
            return self._show_error("Введите текст")

        def on_done(result):
            self.text_result.setHtml(format_analysis(result))
            history_service.add_entry("analyze_text", self.text_name_input.text() or text[:60], result)

        self._run_async(openai_service.analyze_text, on_done, text)

    # --- Изображение ---
    def _build_image_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        row = QHBoxLayout()
        self.image_path_label = QLabel("Файл не выбран")
        pick_btn = QPushButton("Выбрать изображение...")
        pick_btn.clicked.connect(self._on_pick_image)
        row.addWidget(self.image_path_label)
        row.addWidget(pick_btn)
        layout.addLayout(row)

        analyze_btn = QPushButton("Анализировать изображение")
        analyze_btn.clicked.connect(self._on_analyze_image)
        layout.addWidget(analyze_btn)

        self.image_result = QTextBrowser()
        layout.addWidget(self.image_result)

        self.tabs.addTab(widget, "Изображение")
        self._selected_image_path = None

    def _on_pick_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self._selected_image_path = path
            self.image_path_label.setText(path)

    def _on_analyze_image(self):
        if not self._selected_image_path:
            return self._show_error("Выберите изображение")

        with open(self._selected_image_path, "rb") as f:
            image_bytes = f.read()
        mime = "image/jpeg" if self._selected_image_path.lower().endswith((".jpg", ".jpeg")) else "image/png"

        def on_done(result):
            self.image_result.setHtml(format_analysis(result))
            history_service.add_entry("analyze_image", self._selected_image_path, result)

        self._run_async(openai_service.analyze_image, on_done, image_bytes, mime)

    # --- Парсинг ---
    def _build_parse_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        layout.addWidget(QLabel("URL сайта конкурента:"))
        self.parse_url_input = QLineEdit()
        self.parse_url_input.setPlaceholderText("https://www.synthesia.io/")
        layout.addWidget(self.parse_url_input)

        btn = QPushButton("Спарсить и проанализировать")
        btn.clicked.connect(self._on_parse)
        layout.addWidget(btn)

        self.parse_result = QTextBrowser()
        layout.addWidget(self.parse_result)

        self.tabs.addTab(widget, "Парсинг URL")

    def _on_parse(self):
        url = self.parse_url_input.text().strip()
        if not url:
            return self._show_error("Введите URL")

        def do_parse(url):
            parsed = parsing_service.parse_url(url)
            analysis = None
            if parsed.get("first_paragraph"):
                analysis = openai_service.analyze_parsed_content(
                    parsed.get("title") or "", parsed.get("h1") or "", parsed.get("first_paragraph") or ""
                )
            return {**parsed, "analysis": analysis}

        def on_done(result):
            html = f"<b>Title:</b> {result.get('title')}<br><b>H1:</b> {result.get('h1')}<br>"
            html += f"<b>Первый абзац:</b> {result.get('first_paragraph')}<br><br>"
            if result.get("analysis"):
                html += format_analysis(result["analysis"])
            self.parse_result.setHtml(html)
            history_service.add_entry("parse_demo", url, result)

        self._run_async(do_parse, on_done, url)

    # --- История ---
    def _build_history_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        row = QHBoxLayout()
        refresh_btn = QPushButton("Обновить историю")
        refresh_btn.clicked.connect(self._on_refresh_history)
        clear_btn = QPushButton("Очистить историю")
        clear_btn.clicked.connect(self._on_clear_history)
        row.addWidget(refresh_btn)
        row.addWidget(clear_btn)
        layout.addLayout(row)

        self.history_view = QTextBrowser()
        layout.addWidget(self.history_view)

        self.tabs.addTab(widget, "История")

    def _on_refresh_history(self):
        entries = history_service.get_all()
        if not entries:
            self.history_view.setHtml("<i>История пуста</i>")
            return
        html = "<br>".join(
            f"<b>{e['operation_type']}</b> — {e['input_summary']} <i>({e['timestamp']})</i>"
            for e in reversed(entries)
        )
        self.history_view.setHtml(html)

    def _on_clear_history(self):
        history_service.clear()
        self.history_view.setHtml("<i>История очищена</i>")
