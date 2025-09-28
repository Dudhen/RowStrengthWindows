import sys
import re
import json
import asyncio
from importlib import resources

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

# ---------- Константы ----------
DISTANCES = [500, 1000, 1500, 2000, 2500, 3000, 4000, 5000, 6000, 8000, 10000]
REPS_TABLE = {
    1: 100, 2: 97, 3: 94, 4: 92, 5: 89, 6: 86, 7: 83, 8: 81, 9: 78, 10: 75,
    11: 73, 12: 71, 13: 70, 14: 68, 15: 67, 16: 65, 17: 64, 18: 63, 19: 61,
    20: 60, 21: 59, 22: 58, 23: 57, 24: 56, 25: 55, 26: 54, 27: 53, 28: 52,
    29: 51, 30: 50
}
WINDOW_SIZE = (1000, 750)

# ---------- Стили ----------
IS_IOS = (sys.platform == "ios")
F_HEAD = 22 if IS_IOS else 18
F_LABEL = 16 if IS_IOS else 14
F_INPUT = 16 if IS_IOS else 14
PAD_MAIN = 18 if IS_IOS else 14
GAP_MAIN = 14 if IS_IOS else 10

S_MAIN = Pack(direction=COLUMN, margin=PAD_MAIN, gap=GAP_MAIN)
S_ROW = Pack(direction=ROW, gap=10, margin_bottom=6, flex=0)
S_HEAD = Pack(font_size=F_HEAD, margin_bottom=6)
S_LABEL = Pack(font_size=F_LABEL, margin_right=8)
S_INPUT = Pack(font_size=F_INPUT)
S_BTN = Pack(margin_top=6, margin_bottom=6)
S_OUT = Pack(height=140, font_size=F_INPUT, margin_top=4)
S_SECTION = Pack(direction=COLUMN, gap=6)            # вертикальные «секции»
S_BTN_CENTER = Pack(margin_top=6, margin_bottom=2, text_align="center")

# ---------- Локализация ----------
LANGS = ["en", "de", "fr", "es", "ru"]
LANG_LABEL = {
    "en": "English", "de": "Deutsch", "fr": "Français", "es": "Español", "ru": "Русский"
}
T = {
    "app_title": {l: "RowStrength" for l in LANGS},
    "splash": {l: "Dev by Dudhen: @arseny.dudhen" for l in LANGS},
    "language": {"en": "Language", "de": "Sprache", "fr": "Langue", "es": "Idioma", "ru": "Язык"},
    "mode_label": {"en": "Mode", "de": "Modus", "fr": "Mode", "es": "Modo", "ru": "Режим"},
    "mode_erg": {"en": "Ergometer", "de": "Ergometer", "fr": "Ergomètre", "es": "Ergómetro", "ru": "Эргометр"},
    "mode_bar": {"en": "Barbell", "de": "Langhantel", "fr": "Barre", "es": "Barra", "ru": "Штанга"},
    "gender": {"en": "Gender", "de": "Geschlecht", "fr": "Sexe", "es": "Sexo", "ru": "Пол"},
    "female": {"en": "Female", "de": "Weiblich", "fr": "Femme", "es": "Mujer", "ru": "ж"},
    "male": {"en": "Male", "de": "Männlich", "fr": "Homme", "es": "Hombre", "ru": "м"},
    "weight": {"en": "Body weight (kg)", "de": "Körpergewicht (kg)", "fr": "Poids (kg)", "es": "Peso corporal (kg)",
               "ru": "Вес (кг)"},
    "distance": {"en": "Distance", "de": "Distanz", "fr": "Distance", "es": "Distancia", "ru": "Дистанция"},
    "minutes": {"en": "Min", "de": "Min", "fr": "Min", "es": "Min", "ru": "Мин"},
    "seconds": {"en": "Sec", "de": "Sek", "fr": "Sec", "es": "Seg", "ru": "Сек"},
    "centis": {"en": "Tenths", "de": "Zehntel", "fr": "Dixièmes", "es": "Décimas", "ru": "Сотые"},
    "exercise": {"en": "Exercise", "de": "Übung", "fr": "Exercice", "es": "Ejercicio", "ru": "Упражнение"},
    "bar_weight": {"en": "Bar weight (kg)", "de": "Hantelgewicht (kg)", "fr": "Charge (kg)", "es": "Peso en barra (kg)",
                   "ru": "Вес на штанге (кг)"},
    "reps": {"en": "Reps", "de": "Wdh.", "fr": "Répétitions", "es": "Reps", "ru": "Повторы"},
    "calc": {"en": "Calculate", "de": "Berechnen", "fr": "Calculer", "es": "Calcular", "ru": "Рассчитать"},
    "res1_title": {
        "en": "⏱ Results across distances", "de": "⏱ Ergebnisse über Distanzen",
        "fr": "⏱ Résultats par distances", "es": "⏱ Resultados por distancias", "ru": "⏱ Результаты по дистанциям",
    },
    "res1_strength_title": {
        "en": "🏋️ Barbell equivalents (bodyweight-adjusted)",
        "de": "🏋️ Hantel-Äquivalente (mit Körpergewicht)",
        "fr": "🏋️ Équivalents barre (pondérés par le poids)",
        "es": "🏋️ Equivalentes con barra (ajustado por peso)",
        "ru": "🏋️ Эквиваленты в штанге с учётом вашего собственного веса",
    },
    "res2_title": {
        "en": "🏋️ 1 rep max and 2k ergometer equivalent",
        "de": "🏋️ 1 Wdh.-Max. und 2-km-Ergo-Äquivalent",
        "fr": "🏋️ 1 rep max et équivalent 2 km ergomètre",
        "es": "🏋️ 1 rep máx y equivalente 2 km ergómetro",
        "ru": "🏋️ Разовый максимум и эквивалент на эргометре 2 км",
    },
    "err_no_data": {
        "en": "No data for selected distance/gender",
        "de": "Keine Daten für Distanz/Geschlecht",
        "fr": "Pas de données pour la distance/genre",
        "es": "No hay datos para distancia/sexo",
        "ru": "Нет данных по выбранной дистанции/полу",
    },
    "err_time_range": {
        "en": "Time out of range. Available: {a} .. {b}",
        "de": "Zeit außerhalb des Bereichs. Verfügbar: {a} .. {b}",
        "fr": "Temps hors plage. Disponible : {a} .. {b}",
        "es": "Tiempo fuera de rango. Disponible: {a} .. {b}",
        "ru": "Время вне диапазона. Доступно: от {a} до {b}",
    },
    "err_no_strength": {
        "en": "No strength data for this body weight",
        "de": "Keine Kraftdaten für dieses Körpergewicht",
        "fr": "Pas de données de force pour ce poids",
        "es": "No hay datos de fuerza para este peso",
        "ru": "Нет силовых данных для указанного веса",
    },
    "err_reps": {
        "en": "Supported reps: 1..30", "de": "Unterstützte Wiederholungen: 1..30",
        "fr": "Répétitions prises en charge : 1..30", "es": "Repeticiones soportadas: 1..30",
        "ru": "Поддерживаются повторы 1..30",
    },
    "err_1rm_map": {
        "en": "Unable to map to 1 rep max percent",
        "de": "Zuordnung zu 1 Wdh.-Max.-Prozent nicht möglich",
        "fr": "Impossible d'associer au pourcentage de 1 rep max",
        "es": "No se pudo mapear al porcentaje de 1 rep máx",
        "ru": "Не удалось сопоставить проценты для разового максимума",
    },
    "res_1rm": {
        "en": "Estimated 1 rep max: {v} kg", "de": "Geschätztes 1 Wdh.-Max.: {v} kg",
        "fr": "1 rep max estimé : {v} kg", "es": "1 rep máx. estimado: {v} kg",
        "ru": "Оценка разового максимума: {v} кг",
    },
    "res_2k": {
        "en": "2k ergometer equivalent: {v}", "de": "2-km-Ergo-Äquivalent: {v}",
        "fr": "Équivalent ergomètre 2 km : {v}", "es": "Equivalente ergómetro 2 km: {v}",
        "ru": "Эквивалент на эргометре 2 км: {v}",
    },
    "ex_bench": {"en": "Bench press", "de": "Bankdrücken", "fr": "Développé couché", "es": "Press banca", "ru": "Жим"},
    "ex_squat": {"en": "Squat", "de": "Kniebeuge", "fr": "Squat", "es": "Sentadilla", "ru": "Присед"},
    "ex_deadlift": {"en": "Deadlift", "de": "Kreuzheben", "fr": "Soulevé de terre", "es": "Peso muerto",
                    "ru": "Становая тяга"},
}
EX_UI_TO_KEY = {
    lang: {
        T["ex_bench"][lang]: "bench-press",
        T["ex_squat"][lang]: "squat",
        T["ex_deadlift"][lang]: "deadlift",
    } for lang in LANGS
}
EX_KEY_TO_LABEL = {lang: {v: k for k, v in EX_UI_TO_KEY[lang].items()} for lang in LANGS}
GENDER_LABELS = {lang: [T["female"][lang], T["male"][lang]] for lang in LANGS}
GENDER_MAP = {lang: {GENDER_LABELS[lang][0]: "female", GENDER_LABELS[lang][1]: "male"} for lang in LANGS}


# ---------- Утилиты ----------
def get_split_500m(distance: str, time: str) -> str:
    m = re.search(r'\d+', distance)
    if not m:
        raise ValueError("Bad distance")
    meters = int(m.group())
    if meters <= 0:
        raise ValueError("Distance must be > 0")
    m = re.fullmatch(r'\s*(\d{1,2}):(\d{2})\s*', time)
    if not m:
        raise ValueError("Time must be MM:SS")
    mm, ss = int(m.group(1)), int(m.group(2))
    if ss >= 60:
        raise ValueError("Seconds < 60")
    total_sec = mm * 60 + ss
    tenths_total = round(total_sec * 10 / (meters / 500))
    mins = tenths_total // 600
    sec_tenths = tenths_total % 600
    secs = sec_tenths // 10
    tenth = sec_tenths % 10
    return f"{mins:02d}:{secs:02d}.{tenth}/500m"


def load_json_from_package(filename: str):
    with resources.files(__package__).joinpath("data").joinpath(filename).open("r", encoding="utf-8") as f:
        return json.load(f)


def get_distance_data(i_gender, i_distance, rowing_data):
    return rowing_data.get(i_gender, {}).get(str(i_distance), {})


def get_strength_data(i_gender, i_weight, strength_data):
    return strength_data.get(i_gender, {}).get(str(i_weight), {})


def _parse_time_range_from_data(distance_data):
    times = []
    for k in distance_data.keys():
        m = re.match(r"^\s*(\d{1,2}):(\d{2})\s*$", k)
        if m:
            times.append((int(m.group(1)), int(m.group(2))))
    if not times:
        return (0, 0), (59, 59)
    min_mm = min(mm for mm, _ in times)
    max_mm = max(mm for mm, _ in times)
    min_ss = min(ss for mm, ss in times if mm == min_mm)
    max_ss = max(ss for mm, ss in times if mm == max_mm)
    return (min_mm, min_ss), (max_mm, max_ss)


def _two(n: int) -> str:
    return f"{n:02d}"


# ---------- Приложение ----------
class RowStrengthApp(toga.App):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lang = "en"
        self._updating = False

    # --------- Сплэш ----------
    def startup(self):
        self.main_window = toga.MainWindow(title="RowStrength", size=WINDOW_SIZE)
        try:
            self.main_window.resizeable = False
        except Exception:
            try:
                self.main_window.resizable = False
            except Exception:
                pass

        splash_label = toga.Label(
            T["splash"][self.lang],
            style=Pack(font_size=18, text_align="center", margin_top=200, color="#6A5ACD")
        )
        splash_box = toga.Box(children=[splash_label],
                              style=Pack(direction=COLUMN, align_items="center", flex=1, margin=40))
        self.main_window.content = splash_box
        self.main_window.show()

        if sys.platform == "darwin":
            self.on_running = self._after_start
        else:
            loop = asyncio.get_event_loop()
            loop.call_later(3, self._safe_init_ui)

    async def _after_start(self, app):
        await asyncio.sleep(0)
        await asyncio.sleep(3.0)
        self._safe_init_ui()

    def _install_global_tap_dismiss(self):
        """iOS: скрывать picker/клавиатуру при тапе в любое место."""
        if sys.platform != "ios":
            return
        try:
            from rubicon.objc import ObjCClass, NSObject, objc_method

            UITapGestureRecognizer = ObjCClass("UITapGestureRecognizer")

            # Объект-таргет для жеста
            class _TapCloser(NSObject):
                @objc_method
                def handleTap_(self, sender) -> None:
                    try:
                        # закрыть любой first responder (picker/keyboard)
                        self.window_ref._impl.native.view.endEditing(True)
                    except Exception:
                        pass

            self._tap_delegate = _TapCloser.alloc().init()
            # передадим ссылку на окно (чтоб не ловить GC и было что закрывать)
            self._tap_delegate.window_ref = self.main_window

            view = self.main_window._impl.native.view
            self._tap_recognizer = UITapGestureRecognizer.alloc().initWithTarget_action_(
                self._tap_delegate, "handleTap:"
            )
            # Не глушим события для обычных контролов
            self._tap_recognizer.cancelsTouchesInView = False

            # Повесим распознаватель на корневой вью
            view.addGestureRecognizer_(self._tap_recognizer)
        except Exception:
            # На всякий случай — молча игнорируем, если вдруг нет rubicon/нестандартный бэкенд
            pass

    def _safe_init_ui(self):
        try:
            self._init_ui()
        except Exception as e:
            import traceback
            self.main_window.error_dialog("Init error", f"{e}\n\n{traceback.format_exc()}")

    # --------- Основной UI ----------
    def _init_ui(self):
        # данные
        self.rowing_data = load_json_from_package("data_for_rowing_app.json")
        self.strength_data_all = load_json_from_package("data_for_strength_app.json")

        # заголовок и язык
        self.title_label = toga.Label("", style=S_HEAD)
        self.lang_caption = toga.Label("", style=S_LABEL)
        self.lang_sel = toga.Selection(
            items=[LANG_LABEL[c] for c in LANGS],
            value=LANG_LABEL[self.lang],
            on_change=self._on_lang_changed,
            style=S_INPUT
        )

        # общие поля (для обеих вкладок, сверху)
        self.gender_caption = toga.Label("", style=S_LABEL)
        self.gender = toga.Selection(items=GENDER_LABELS[self.lang], value=GENDER_LABELS[self.lang][1],
                                     on_change=self._on_gender_changed, style=S_INPUT)
        self.weight_caption = toga.Label("", style=S_LABEL)
        self.weight = toga.NumberInput(step=1, min=40, max=140, value=80, style=S_INPUT)

        # -------- Эргометр (вкладка 1) --------
        self.distance_caption = toga.Label("", style=S_LABEL)
        self.minutes_caption = toga.Label("", style=S_LABEL)
        self.seconds_caption = toga.Label("", style=S_LABEL)
        self.centis_caption = toga.Label("", style=S_LABEL)

        self.distance = toga.Selection(items=[str(d) for d in DISTANCES], value="2000",
                                       on_change=self._on_distance_changed, style=S_INPUT)
        self.time_min = toga.Selection(items=["06"], value="06",
                                       on_change=self._on_time_min_changed, style=S_INPUT)
        self.time_sec = toga.Selection(items=[_two(i) for i in range(60)], value="00", style=S_INPUT)
        self.time_ms = toga.Selection(items=[str(i) for i in range(10)], value="0", style=S_INPUT)

        self.res1_title = toga.Label("", style=S_LABEL)
        self.res1_output = toga.MultilineTextInput(readonly=True, style=S_OUT)
        self.res1_strength_title = toga.Label("", style=S_LABEL)
        self.res1_output_strength = toga.MultilineTextInput(readonly=True, style=S_OUT)

        # Ввод — более вертикально: 2 строки («Дистанция»; «Время»)
        row_distance = toga.Box(children=[self.distance_caption, self.distance], style=S_ROW)
        row_time = toga.Box(
            children=[self.minutes_caption, self.time_min, self.seconds_caption, self.time_sec, self.centis_caption, self.time_ms],
            style=S_ROW
        )

        self.mode1_inputs = toga.Box(children=[row_distance, row_time], style=S_SECTION)
        self.calc_button_erg = toga.Button("", on_press=self.calculate_erg, style=S_BTN)
        self.mode1_results_box = toga.Box(
            children=[self.res1_title, self.res1_output, self.res1_strength_title, self.res1_output_strength],
            style=Pack(direction=COLUMN, gap=10, margin_top=4)
        )
        self.erg_container = toga.Box(
            children=[self.mode1_inputs, self.calc_button_erg, self.mode1_results_box],
            style=Pack(direction=COLUMN, gap=8)
        )

        # -------- Штанга (вкладка 2) --------
        self.exercise_caption = toga.Label("", style=S_LABEL)
        self.exercise = toga.Selection(items=list(EX_UI_TO_KEY[self.lang].keys()),
                                       value=list(EX_UI_TO_KEY[self.lang].keys())[0], style=S_INPUT)
        self.bar_weight_caption = toga.Label("", style=S_LABEL)
        self.bar_weight = toga.NumberInput(step=1, min=1, value=100, style=S_INPUT)
        self.reps_caption = toga.Label("", style=S_LABEL)
        self.reps = toga.NumberInput(step=1, min=1, max=30, value=5, style=S_INPUT)

        self.res2_title = toga.Label("", style=S_LABEL)
        self.res2_output = toga.MultilineTextInput(readonly=True, style=S_OUT)

        # Ввод — вертикально: 3 короткие строки
        row_ex = toga.Box(children=[self.exercise_caption, self.exercise], style=S_ROW)
        row_w = toga.Box(children=[self.bar_weight_caption, self.bar_weight], style=S_ROW)
        row_r = toga.Box(children=[self.reps_caption, self.reps], style=S_ROW)

        self.mode2_inputs = toga.Box(children=[row_ex, row_w, row_r], style=S_SECTION)
        self.calc_button_bar = toga.Button("", on_press=self.calculate_bar, style=S_BTN)
        self.mode2_results_box = toga.Box(children=[self.res2_title, self.res2_output],
                                          style=Pack(direction=COLUMN, gap=10, margin_top=4))
        self.bar_container = toga.Box(
            children=[self.mode2_inputs, self.calc_button_bar, self.mode2_results_box],
            style=Pack(direction=COLUMN, gap=8)
        )

        self.erg_page = toga.ScrollContainer(content=self.erg_container)
        self.bar_page = toga.ScrollContainer(content=self.bar_container)

        # ----- Контейнер вкладок -----
        self.tabs_holder = toga.Box(style=Pack(direction=COLUMN, flex=1))
        self._build_tabs()

        # Компоновка верхней части
        head_row = toga.Box(children=[self.title_label], style=Pack(direction=ROW, margin_bottom=8))
        lang_row = toga.Box(children=[self.lang_caption, self.lang_sel], style=S_ROW)
        common_row = toga.Box(children=[self.gender_caption, self.gender,
                                        self.weight_caption, self.weight], style=S_ROW)

        main_box = toga.Box(children=[head_row, lang_row, common_row, self.tabs_holder], style=S_MAIN)
        scroller = toga.ScrollContainer(content=main_box)

        # Локализация и первичная инициализация
        self._apply_language()
        self._rebuild_time_selects()

        self.main_window.content = scroller
        self._install_global_tap_dismiss()

    # ---------- Tabs ----------
    def _build_tabs(self):
        for c in list(self.tabs_holder.children):
            self.tabs_holder.remove(c)
        try:
            self.tabs = toga.OptionContainer(
                content=[(self.tr("mode_erg"), self.erg_page),
                         (self.tr("mode_bar"), self.bar_page)],
                style=Pack(flex=1)
            )
        except TypeError:
            self.tabs = toga.OptionContainer(
                content=[(self.erg_page, self.tr("mode_erg")),
                         (self.bar_page, self.tr("mode_bar"))],
                style=Pack(flex=1)
            )
        self.tabs_holder.add(self.tabs)

    # ---- локализация UI ----
    def tr(self, key):
        return T[key][self.lang]

    def _set_selection(self, sel: toga.Selection, items=None, value=None):
        self._updating = True
        try:
            if items is not None and list(getattr(sel, "items", [])) != list(items):
                sel.items = items
            if value is not None and getattr(sel, "value", None) != value:
                sel.value = value
        finally:
            self._updating = False

    def _apply_language(self):
        self.title_label.text = self.tr("app_title")
        self.lang_caption.text = self.tr("language")
        self.gender_caption.text = self.tr("gender")
        self.weight_caption.text = self.tr("weight")
        self.distance_caption.text = self.tr("distance")
        self.minutes_caption.text = self.tr("minutes")
        self.seconds_caption.text = self.tr("seconds")
        self.centis_caption.text = self.tr("centis")
        self.res1_title.text = self.tr("res1_title")
        self.res1_strength_title.text = self.tr("res1_strength_title")
        self.exercise_caption.text = self.tr("exercise")
        self.bar_weight_caption.text = self.tr("bar_weight")
        self.reps_caption.text = self.tr("reps")
        self.res2_title.text = self.tr("res2_title")
        self.calc_button_erg.text = self.tr("calc")
        self.calc_button_bar.text = self.tr("calc")

        self._set_selection(self.lang_sel, items=[LANG_LABEL[c] for c in LANGS], value=LANG_LABEL[self.lang])

        cur_gender_value = self.gender.value
        self._set_selection(
            self.gender,
            items=GENDER_LABELS[self.lang],
            value=cur_gender_value if cur_gender_value in GENDER_LABELS[self.lang] else GENDER_LABELS[self.lang][1],
        )

        old_ex = self.exercise.value
        ex_items = list(EX_UI_TO_KEY[self.lang].keys())
        self._set_selection(self.exercise, items=ex_items, value=old_ex if old_ex in ex_items else ex_items[0])

        # переименовывать вкладки без пересоздания
        self._set_tab_titles()

    # ---- handlers ----
    def _on_lang_changed(self, widget):
        if self._updating:
            return
        inv = {v: k for k, v in LANG_LABEL.items()}
        self.lang = inv.get(self.lang_sel.value, "en")
        self._apply_language()
        self._rebuild_time_selects()
        self._clear_results()

    def _set_tab_titles(self):
        if hasattr(self, "tabs") and self.tabs is not None:
            try:
                items = list(self.tabs.content)
                if len(items) >= 2:
                    items[0].text = self.tr("mode_erg")
                    items[1].text = self.tr("mode_bar")
            except Exception:
                try:
                    self.tabs.set_tab_label(self.erg_page, self.tr("mode_erg"))
                    self.tabs.set_tab_label(self.bar_page, self.tr("mode_bar"))
                except Exception:
                    pass

    def _clear_results(self):
        if hasattr(self, "res1_output"):
            self.res1_output.value = ""
        if hasattr(self, "res1_output_strength"):
            self.res1_output_strength.value = ""
        if hasattr(self, "res2_output"):
            self.res2_output.value = ""

    def _on_distance_changed(self, widget):
        if self._updating:
            return
        self._rebuild_time_selects()

    def _on_gender_changed(self, widget):
        if self._updating:
            return
        self._rebuild_time_selects()

    def _on_time_min_changed(self, widget):
        pass

    def _rebuild_time_selects(self):
        g_label = self.gender.value
        g_key = GENDER_MAP[self.lang].get(g_label, "male")
        distance = int(self.distance.value)
        distance_data = get_distance_data(g_key, distance, self.rowing_data)
        (min_mm, _), (max_mm, _) = _parse_time_range_from_data(distance_data)
        if not distance_data:
            min_mm, max_mm = 0, 59

        minutes_items = [_two(i) for i in range(min_mm, max_mm + 1)]
        prev_min = self.time_min.value if self.time_min.value in minutes_items else _two(min_mm)
        self._set_selection(self.time_min, items=minutes_items, value=prev_min)

        sec_items = [_two(i) for i in range(60)]
        prev_sec = self.time_sec.value if self.time_sec.value in sec_items else "00"
        self._set_selection(self.time_sec, items=sec_items, value=prev_sec)

        if self.time_ms.value is None:
            self.time_ms.value = "0"

    # ---- бизнес-логика ----
    def calculate_erg(self, widget):
        def _meters_from_key(k) -> int:
            m = re.search(r"\d+", str(k))
            return int(m.group()) if m else 0

        try:
            g_key = GENDER_MAP[self.lang].get(self.gender.value, "male")
            weight = int(self.weight.value)

            distance = int(self.distance.value)
            distance_data = get_distance_data(g_key, distance, self.rowing_data)
            if not distance_data:
                raise ValueError(T["err_no_data"][self.lang])

            t_norm = f"{self.time_min.value}:{self.time_sec.value}"
            distance_data_time = distance_data.get(t_norm) or distance_data.get(t_norm.lstrip("0"))
            if not distance_data_time:
                times_str = list(distance_data.keys())
                raise ValueError(T["err_time_range"][self.lang].format(a=times_str[0], b=times_str[-1]))

            percent = distance_data_time.get("percent")
            strength = get_strength_data(g_key, weight, self.strength_data_all)
            if not strength:
                raise ValueError(T["err_no_strength"][self.lang])

            keys = [kk for kk in distance_data_time.keys() if kk != "percent"]
            keys.sort(key=_meters_from_key)
            lines_dist = []
            for k in keys:
                v = distance_data_time[k]
                meters = _meters_from_key(k)
                split = get_split_500m(distance=str(meters), time=v)
                lines_dist.append(f"{meters} m — {v}.00 ({split})")
            self.res1_output.value = "\n".join(lines_dist)

            ex_labels = EX_KEY_TO_LABEL[self.lang]
            lines_str = []
            for ex_key, label in ex_labels.items():
                kilo = strength.get(ex_key, {}).get(percent)
                if kilo == "1":
                    vmap = strength.get(ex_key, {})
                    kilo = round((float(kilo) + float(vmap.get("1"))) / 2, 2)
                lines_str.append(f"{label}: {kilo} kg")
            self.res1_output_strength.value = "\n".join(lines_str)

        except Exception as e:
            try:
                import traceback
                self.main_window.error_dialog("Error", f"{e}\n\n{traceback.format_exc()}")
            except Exception:
                print("Error:", e)

    def calculate_bar(self, widget):
        try:
            g_key = GENDER_MAP[self.lang].get(self.gender.value, "male")
            weight = int(self.weight.value)

            ex_key = EX_UI_TO_KEY[self.lang][self.exercise.value]
            bar_w = float(self.bar_weight.value)
            reps = int(self.reps.value)
            if reps not in REPS_TABLE:
                raise ValueError(T["err_reps"][self.lang])

            rep_max = round((bar_w / REPS_TABLE[reps]) * 100, 2)

            strength_for_user = get_strength_data(g_key, weight, self.strength_data_all)
            if not strength_for_user:
                raise ValueError(T["err_no_strength"][self.lang])

            ex_table = strength_for_user.get(ex_key, {})
            i_percent = None
            for pct_str, val in ex_table.items():
                if float(val) <= rep_max:
                    i_percent = float(pct_str)
                else:
                    break
            if i_percent is None:
                raise ValueError(T["err_1rm_map"][self.lang])

            distance_data = get_distance_data(g_key, 2000, self.rowing_data)
            km2_res = None
            for k, v in distance_data.items():
                km2_res = k
                if float(v.get("percent")) < i_percent:
                    break

            self.res2_output.value = "\n".join([
                T["res_1rm"][self.lang].format(v=rep_max),
                T["res_2k"][self.lang].format(v=km2_res)
            ])

        except Exception as e:
            try:
                import traceback
                self.main_window.error_dialog("Error", f"{e}\n\n{traceback.format_exc()}")
            except Exception:
                print("Error:", e)


def main():
    return RowStrengthApp("RowStrength", "com.rowstrength")
