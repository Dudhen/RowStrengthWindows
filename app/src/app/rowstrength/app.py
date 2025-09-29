import sys
import re
import json
import asyncio
from importlib import resources

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

# -------- Константы/настройки --------
DISTANCES = [500, 1000, 1500, 2000, 2500, 3000, 4000, 5000, 6000, 8000, 10000]
SHOW_DISTANCES = [500, 1000, 2000, 3000, 5000, 6000, 10000]  # 7 строк
REPS_TABLE = {
    1: 100, 2: 97, 3: 94, 4: 92, 5: 89, 6: 86, 7: 83, 8: 81, 9: 78, 10: 75,
    11: 73, 12: 71, 13: 70, 14: 68, 15: 67, 16: 65, 17: 64, 18: 63, 19: 61,
    20: 60, 21: 59, 22: 58, 23: 57, 24: 56, 25: 55, 26: 54, 27: 53, 28: 52,
    29: 51, 30: 50
}
WINDOW_SIZE = (1000, 750)

IS_IOS = (sys.platform == "ios")
F_HEAD = 22 if IS_IOS else 18
F_LABEL = 16 if IS_IOS else 14
F_INPUT = 16 if IS_IOS else 14
PAD_MAIN = 16 if IS_IOS else 14

CLR_HEADER_BG = "#D9CCFF"
CLR_TABLE_BG = "#EDE7FF"
CLR_BTN_BG = "#D9CCFF"
CLR_BTN_FG = "#2B1C7A"
CLR_ACCENT = "#6A5ACD"


def S_MAIN():  return Pack(direction=COLUMN, padding=PAD_MAIN, flex=1)


def S_ROW():   return Pack(direction=ROW, padding_bottom=6)


def S_COL():   return Pack(direction=COLUMN)


def S_HEAD():  return Pack(font_size=F_HEAD, padding_bottom=6)


def S_LBL():   return Pack(font_size=F_LABEL, padding_right=8, flex=1)


def S_INP(w=None): return Pack(font_size=F_INPUT, padding_right=10, width=w if w else None)


def S_BTN():   return Pack(padding_top=10, padding_bottom=10, padding_left=12, padding_right=12, flex=1)


# -------- Локализация --------
LANGS = ["en", "de", "fr", "es", "ru"]
LANG_LABEL = {"en": "English", "de": "Deutsch", "fr": "Français", "es": "Español", "ru": "Русский"}
T = {
    "splash": {l: "Dev by Dudhen: @arseny.dudchenko" for l in LANGS},
    "title": {l: "RowStrength by Dudhen" for l in LANGS},
    "mode_erg": {"en": "Ergometer", "de": "Ergometer", "fr": "Ergomètre", "es": "Ergómetro", "ru": "Эргометр"},
    "mode_bar": {"en": "Barbell", "de": "Langhantel", "fr": "Barre", "es": "Barra", "ru": "Штанга"},
    "language": {"en": "Language", "de": "Sprache", "fr": "Langue", "es": "Idioma", "ru": "Язык"},
    "gender": {"en": "Gender", "de": "Geschlecht", "fr": "Sexe", "es": "Sexo", "ru": "Пол"},
    "female": {"en": "Female", "de": "Weiblich", "fr": "Femme", "es": "Mujer", "ru": "Жен"},
    "male": {"en": "Male", "de": "Männlich", "fr": "Homme", "es": "Hombre", "ru": "Муж"},
    "weight": {"en": "Body weight (kg)", "de": "Körpergewicht (kg)", "fr": "Poids (kg)", "es": "Peso corporal (kg)",
               "ru": "Вес (кг)"},
    "distance": {"en": "Distance", "de": "Distanz", "fr": "Distance", "es": "Distancia", "ru": "Дистанция"},
    "minutes": {"en": "Min", "de": "Min", "fr": "Min", "es": "Min", "ru": "Мин"},
    "seconds": {"en": "Sec", "de": "Sek", "fr": "Sec", "es": "Seg", "ru": "Сек"},
    "centis": {"en": "Tenths", "de": "Zehntel", "fr": "Dixièmes", "es": "Décimas", "ru": "Миллисекунды"},
    "exercise": {"en": "Exercise", "de": "Übung", "fr": "Exercice", "es": "Ejercicio", "ru": "Упражнение"},
    "bar_weight": {"en": "Bar weight (kg)", "de": "Hantelgewicht (kg)", "fr": "Charge (kg)", "es": "Peso en barra (kg)",
                   "ru": "Вес на штанге (кг)"},
    "reps": {"en": "Reps", "de": "Wdh.", "fr": "Répétitions", "es": "Reps", "ru": "Повторы"},
    "calc": {"en": "Calculate", "de": "Berechnen", "fr": "Calculer", "es": "Calcular", "ru": "Рассчитать"},
    # Заголовки таблиц
    "erg_tbl1_title": {
        "en": "Results across distances",
        "de": "Ergebnisse über Distanzen",
        "fr": "Résultats par distances",
        "es": "Resultados por distancias",
        "ru": "Результаты по дистанциям",
    },
    "erg_tbl2_title": {
        "en": "Barbell equivalents (bodyweight {w} kg)",
        "de": "Hantel-Äquivalente (Körpergewicht {w} kg)",
        "fr": "Équivalents barre (poids du corps {w} kg)",
        "es": "Equivalentes con barra (peso corporal {w} kg)",
        "ru": "Эквивалент в штанге с весом {w} кг",
    },
    "bar_tbl_title": {
        "en": "One-rep max\nand 2k ergometer equivalent",
        "de": "1RM\nund 2-km-Ergometer-Äquivalent",
        "fr": "1 RM\net équivalent ergomètre 2 km",
        "es": "1RM\ny equivalente de ergómetro 2 km",
        "ru": "Разовый максимум\nи эквивалент на эргометре 2км",
    },
    # Табличные подписи
    "tbl_1rm": {"en": "1 rep max", "de": "1RM", "fr": "1 RM", "es": "1RM", "ru": "Разовый максимум"},
    "tbl_2k": {"en": "2k ergometer", "de": "2 km Ergo", "fr": "Ergo 2 km", "es": "Ergo 2 km", "ru": "2км эргометр"},
    # Упражнения
    "ex_bench": {"en": "Bench press", "de": "Bankdrücken", "fr": "Développé couché", "es": "Press banca", "ru": "Жим"},
    "ex_squat": {"en": "Squat", "de": "Kniebeuge", "fr": "Squat", "es": "Sentadilla", "ru": "Присед"},
    "ex_deadlift": {"en": "Deadlift", "de": "Kreuzheben", "fr": "Soulevé de terre", "es": "Peso muerto",
                    "ru": "Становая тяга"},
    # Ошибки
    "err_title": {"en": "Notice", "de": "Hinweis", "fr": "Avis", "es": "Aviso", "ru": "Упс"},
    "err_weight": {"en": "Body weight must be between 40 and 140 kg.",
                   "de": "Körpergewicht muss zwischen 40 und 140 kg liegen.",
                   "fr": "Le poids doit être entre 40 et 140 kg.",
                   "es": "El peso corporal debe estar entre 40 y 140 kg.",
                   "ru": "Упс: вес тела должен быть от 40 до 140"},
    "err_reps": {"en": "Supported reps: 1..30.",
                 "de": "Unterstützte Wiederholungen: 1..30.",
                 "fr": "Répétitions prises en charge : 1..30.",
                 "es": "Repeticiones soportadas: 1..30.",
                 "ru": "Поддерживаются повторы: 1..30."},
    "err_bar_weight": {"en": "Bar weight must be between 1 and 700 kg.",
                       "de": "Hantelgewicht muss zwischen 1 und 700 kg liegen.",
                       "fr": "La charge doit être entre 1 et 700 kg.",
                       "es": "El peso en barra debe estar entre 1 y 700 kg.",
                       "ru": "Вес на штанге должен быть от 1 до 700"},
    "err_no_data": {"en": "No data for the selected distance/gender.",
                    "de": "Keine Daten für die gewählte Distanz/Geschlecht.",
                    "fr": "Pas de données pour cette distance/genre.",
                    "es": "No hay datos para esta distancia/sexo.",
                    "ru": "Нет данных по выбранной дистанции и полу."},
    "err_time_range": {"en": "Time is out of range.", "de": "Zeit außerhalb des Bereichs.",
                       "fr": "Temps hors plage.", "es": "Tiempo fuera de rango.", "ru": "Время вне диапазона."},
    "err_no_strength": {"en": "No strength data for this body weight.",
                        "de": "Keine Kraftdaten für dieses Körpergewicht.",
                        "fr": "Pas de données de force pour ce poids.",
                        "es": "No hay datos de fuerza para este peso.",
                        "ru": "Нет силовых данных для указанного веса."},
    "err_1rm_map": {"en": "Unable to estimate 1RM percent for these inputs.",
                    "de": "Prozentsatz zum 1RM konnte nicht ermittelt werden.",
                    "fr": "Impossible d'estimer le pourcentage de 1RM.",
                    "es": "No se puede estimar el porcentaje de 1RM.",
                    "ru": "Не удалось сопоставить процент к 1ПМ для этих данных."},
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


# -------- Утилиты расчёта/таблиц --------
def _two(n: int) -> str:
    return f"{n:02d}"


def get_split_500m(distance_m: int, time_mmss: str) -> str:
    m = re.fullmatch(r'\s*(\d{1,2}):(\d{2})\s*', time_mmss)
    mm, ss = int(m.group(1)), int(m.group(2))
    total_sec = mm * 60 + ss
    tenths_total = round(total_sec * 10 / (distance_m / 500))
    mins = tenths_total // 600
    sec_tenths = tenths_total % 600
    secs = sec_tenths // 10
    tenth = sec_tenths % 10
    return f"{mins:02d}:{secs:02d}.{tenth}/500m"


def load_json_from_package(filename: str):
    pkg = __package__ or "rowstrength"
    with resources.files(pkg).joinpath("data").joinpath(filename).open("r", encoding="utf-8") as f:
        return json.load(f)


def get_distance_data(gender, distance, data):
    return data.get(gender, {}).get(str(distance), {})


def get_strength_data(gender, bw, data):
    return data.get(gender, {}).get(str(int(bw)), {})


def parse_available_times(distance_data):
    mins = {}
    for key in distance_data.keys():
        m = re.fullmatch(r'\s*(\d{1,2}):(\d{2})\s*', key)
        if not m:
            continue
        mm, ss = _two(int(m.group(1))), _two(int(m.group(2)))
        mins.setdefault(mm, set()).add(ss)
    minutes_sorted = sorted(mins.keys(), key=lambda x: int(x))
    seconds_for_minute = {mm: sorted(list(sset), key=lambda x: int(x)) for mm, sset in mins.items()}
    return minutes_sorted, seconds_for_minute


def meters_from_key(k) -> int:
    m = re.search(r"\d+", str(k))
    return int(m.group()) if m else 0


def make_table(rows, col_flex=None):
    if not rows:
        return toga.Box(style=S_COL())
    cols = max(len(r) for r in rows)
    col_flex = col_flex or [1] * cols
    table = toga.Box(style=S_COL())
    for r in rows:
        row = toga.Box(style=Pack(direction=ROW, background_color=CLR_TABLE_BG, padding=6))
        for i in range(cols):
            text = r[i] if i < len(r) else ""
            lbl = toga.Label(text, style=Pack(flex=col_flex[i], font_size=F_INPUT))
            row.add(lbl)
        table.add(row)
    return table


# --- вспомогательный форс лэйаута для iOS ---
def _force_layout_ios(window):
    if sys.platform != "ios":
        return
    try:
        native = window._impl.native
        native.view.setNeedsLayout()
        native.view.layoutIfNeeded()
    except Exception:
        pass


# -------- Приложение --------
class RowStrengthApp(toga.App):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lang = "ru"
        self._updating = False
        self._erg_init_done = False
        self.rowing_data = None
        self.strength_data_all = None
        # ссылки на заголовки таблиц (создаются только при расчёте)
        self.erg_tbl1_title_label = None
        self.erg_tbl2_title_label = None
        self.bar_tbl_title_label = None

    # ---- Сплэш ----
    def startup(self):
        self.main_window = toga.MainWindow(title="RowStrength", size=WINDOW_SIZE)
        for attr in ("resizeable", "resizable"):
            try:
                setattr(self.main_window, attr, False)
                break
            except Exception:
                pass

        splash = toga.Label(T["splash"][self.lang], style=Pack(font_size=18, text_align="center", color=CLR_ACCENT))
        center_row = toga.Box(style=Pack(direction=ROW, flex=1))
        center_row.add(toga.Box(style=Pack(flex=1)))
        center_row.add(splash)
        center_row.add(toga.Box(style=Pack(flex=1)))
        splash_root = toga.Box(children=[toga.Box(style=Pack(flex=1)), center_row, toga.Box(style=Pack(flex=1))],
                               style=Pack(direction=COLUMN, flex=1, padding=24))
        self.main_window.content = splash_root
        self.main_window.show()

        if sys.platform == "darwin":
            self.on_running = self._after_start
        else:
            asyncio.get_event_loop().call_later(3.0, self._safe_build_main)

    async def _after_start(self, app):
        await asyncio.sleep(0)
        await asyncio.sleep(3.0)
        self._safe_build_main()

    def _safe_build_main(self):
        try:
            self._build_main()
        except Exception as e:
            self._info(str(e))

    def _info(self, msg: str):
        try:
            self.main_window.info_dialog(T["err_title"][self.lang], msg)
        except Exception:
            print(msg)

    def _dismiss_ios_inputs(self):
        if sys.platform != "ios":
            return
        try:
            from rubicon.objc import ObjCClass
            UIApplication = ObjCClass("UIApplication")
            app = UIApplication.sharedApplication
            key_window = app.keyWindow or (app.windows and app.windows.firstObject)
            if key_window:
                key_window.endEditing(True)
        except Exception:
            pass

    # ---- Основной UI ----
    def _build_main(self):
        self.rowing_data = load_json_from_package("data_for_rowing_app.json")
        self.strength_data_all = load_json_from_package("data_for_strength_app.json")

        # Шапка
        title_lbl = toga.Label(T["title"][self.lang], style=Pack(font_size=F_HEAD, color="#501c59", padding=8))
        self.lang_sel = toga.Selection(items=[LANG_LABEL[c] for c in LANGS],
                                       value=LANG_LABEL[self.lang],
                                       on_change=self._on_lang_change,
                                       style=S_INP(160))
        header = toga.Box(style=Pack(direction=ROW, background_color=CLR_HEADER_BG, padding_left=8, padding_right=8))
        header.add(title_lbl)
        header.add(toga.Box(style=Pack(flex=1)))
        header.add(toga.Label(T["language"][self.lang], style=Pack(font_size=F_LABEL, padding_right=6)))
        header.add(self.lang_sel)

        # ===== Вкладка Эргометр =====
        self.gender_lbl = toga.Label(T["gender"][self.lang], style=S_LBL())
        self.gender = toga.Selection(items=GENDER_LABELS[self.lang], value=GENDER_LABELS[self.lang][1],
                                     on_change=self._on_gender_change, style=S_INP(160))
        self.weight_lbl = toga.Label(T["weight"][self.lang], style=S_LBL())
        self.weight = toga.NumberInput(step=1, value=80, style=S_INP(160))

        self.distance_lbl = toga.Label(T["distance"][self.lang], style=S_LBL())
        self.distance = toga.Selection(items=[str(d) for d in DISTANCES], value="2000",
                                       on_change=self._on_distance_change, style=S_INP(160))

        self.min_lbl = toga.Label(T["minutes"][self.lang], style=S_LBL())
        self.sec_lbl = toga.Label(T["seconds"][self.lang], style=S_LBL())
        self.cen_lbl = toga.Label(T["centis"][self.lang], style=S_LBL())
        self.min_sel = toga.Selection(items=["06"], value="06", on_change=self._on_minute_change, style=S_INP(120))
        self.sec_sel = toga.Selection(items=[_two(i) for i in range(60)], value="00", style=S_INP(120))
        self.cen_sel = toga.Selection(items=[str(i) for i in range(10)], value="0", style=S_INP(120))

        self.btn_erg = toga.Button(T["calc"][self.lang], on_press=self.calculate_erg, style=S_BTN())
        try:
            self.btn_erg.style.background_color = CLR_BTN_BG
            self.btn_erg.style.color = CLR_BTN_FG
        except Exception:
            pass

        # Контейнер результатов Эргометра (пустой до нажатия)
        self.erg_results_holder = toga.Box(style=S_COL())

        erg_rows = [
            toga.Box(children=[self.gender_lbl, self.gender], style=S_ROW()),
            toga.Box(children=[self.weight_lbl, self.weight], style=S_ROW()),
            toga.Box(children=[self.distance_lbl, self.distance], style=S_ROW()),
            toga.Box(children=[self.min_lbl, self.min_sel], style=S_ROW()),
            toga.Box(children=[self.sec_lbl, self.sec_sel], style=S_ROW()),
            toga.Box(children=[self.cen_lbl, self.cen_sel], style=S_ROW()),
            toga.Box(children=[self.btn_erg], style=S_ROW()),
            self.erg_results_holder,  # тут появятся заголовки и таблицы после расчёта
        ]
        erg_col = toga.Box(children=erg_rows, style=S_COL())
        erg_page = toga.ScrollContainer(content=erg_col, horizontal=False)

        # ===== Вкладка Штанга ===== (с Полом и Весом)
        self.gender_b_lbl = toga.Label(T["gender"][self.lang], style=S_LBL())
        self.gender_b = toga.Selection(items=GENDER_LABELS[self.lang], value=GENDER_LABELS[self.lang][1],
                                       style=S_INP(160))
        self.weight_b_lbl = toga.Label(T["weight"][self.lang], style=S_LBL())
        self.weight_b = toga.NumberInput(step=1, value=80, style=S_INP(160))

        self.ex_lbl = toga.Label(T["exercise"][self.lang], style=S_LBL())
        self.exercise = toga.Selection(items=list(EX_UI_TO_KEY[self.lang].keys()),
                                       value=list(EX_UI_TO_KEY[self.lang].keys())[0],
                                       style=S_INP(200))
        self.bw_lbl = toga.Label(T["bar_weight"][self.lang], style=S_LBL())
        self.bar_weight = toga.NumberInput(step=1, value=100, style=S_INP(160))
        self.reps_lbl = toga.Label(T["reps"][self.lang], style=S_LBL())
        self.reps = toga.NumberInput(step=1, value=5, style=S_INP(120))

        self.btn_bar = toga.Button(T["calc"][self.lang], on_press=self.calculate_bar, style=S_BTN())
        try:
            self.btn_bar.style.background_color = CLR_BTN_BG
            self.btn_bar.style.color = CLR_BTN_FG
        except Exception:
            pass

        # Контейнер результатов Штанги (пустой до нажатия)
        self.bar_results_holder = toga.Box(style=S_COL())

        bar_rows = [
            toga.Box(children=[self.gender_b_lbl, self.gender_b], style=S_ROW()),
            toga.Box(children=[self.weight_b_lbl, self.weight_b], style=S_ROW()),
            toga.Box(children=[self.ex_lbl, self.exercise], style=S_ROW()),
            toga.Box(children=[self.bw_lbl, self.bar_weight], style=S_ROW()),
            toga.Box(children=[self.reps_lbl, self.reps], style=S_ROW()),
            toga.Box(children=[self.btn_bar], style=S_ROW()),
            self.bar_results_holder,  # тут появится заголовок + таблица после расчёта
        ]
        bar_col = toga.Box(children=bar_rows, style=S_COL())
        bar_page = toga.ScrollContainer(content=bar_col, horizontal=False)

        # Tabs
        try:
            self.tabs = toga.OptionContainer(content=[(T["mode_erg"][self.lang], erg_page),
                                                      (T["mode_bar"][self.lang], bar_page)],
                                             style=Pack(flex=1))
        except TypeError:
            self.tabs = toga.OptionContainer(content=[(erg_page, T["mode_erg"][self.lang]),
                                                      (bar_page, T["mode_bar"][self.lang])],
                                             style=Pack(flex=1))

        root = toga.Box(style=Pack(direction=COLUMN, flex=1))
        root.add(header)
        root.add(self.tabs)
        self.main_window.content = root

        # Первичная инициализация таймингов
        self._rebuild_time_selects()
        self._erg_init_done = True

        # Пост-фиксации для iOS/первой отрисовки
        self._post_build_fixups()

    # ---- Пост-фиксации для iOS и первой раскладки ----
    def _post_build_fixups(self):
        try:
            self.btn_erg.style.flex = 1
            self.btn_bar.style.flex = 1
            self.btn_erg.refresh()
            self.btn_bar.refresh()
        except Exception:
            pass

        try:
            self._rebuild_time_selects()

            minutes = list(self.min_sel.items) or []
            if "06" in minutes:
                self.min_sel.value = "06"

                g_key = GENDER_MAP[self.lang].get(self.gender.value, "male")
                dist = int(self.distance.value)
                dist_data = get_distance_data(g_key, dist, self.rowing_data)
                _, sec_map = parse_available_times(dist_data)
                secs = sec_map.get("06", list(self.sec_sel.items) or ["00"])
                self.sec_sel.items = secs
                self.sec_sel.value = secs[0]

            self.min_sel.refresh()
            self.sec_sel.refresh()
        except Exception:
            pass

        _force_layout_ios(self.main_window)

        def _second_pass():
            try:
                self.main_window.content.refresh()
                self.min_sel.refresh()
                self.sec_sel.refresh()
                self.btn_erg.refresh()
                self.btn_bar.refresh()
                _force_layout_ios(self.main_window)
            except Exception:
                pass

        asyncio.get_event_loop().call_later(0.15, _second_pass)

    # ---- Минуты/секунды ----
    def _rebuild_time_selects(self):
        g_key = GENDER_MAP[self.lang].get(self.gender.value, "male")
        dist = int(self.distance.value)
        dist_data = get_distance_data(g_key, dist, self.rowing_data)
        if not dist_data:
            self.min_sel.items = ["00"];
            self.min_sel.value = "00"
            self.sec_sel.items = ["00"];
            self.sec_sel.value = "00"
            return

        minutes, sec_map = parse_available_times(dist_data)
        default_min = minutes[1] if len(minutes) >= 2 else minutes[0]
        if self._erg_init_done and self.min_sel.value in minutes:
            default_min = self.min_sel.value
        self.min_sel.items = minutes
        self.min_sel.value = default_min

        seconds = sec_map.get(default_min, ["00"])
        default_sec = seconds[0]
        if self._erg_init_done and self.sec_sel.value in seconds:
            default_sec = self.sec_sel.value
        self.sec_sel.items = seconds
        self.sec_sel.value = default_sec

    # ---- Обновление существующих заголовков (без пересчёта) ----
    def _update_existing_titles(self):
        # Эргометр
        if self.erg_tbl1_title_label is not None:
            self.erg_tbl1_title_label.text = T["erg_tbl1_title"][self.lang]
        if self.erg_tbl2_title_label is not None:
            try:
                w = int(float(self.weight.value or 0))
            except Exception:
                w = 0
            self.erg_tbl2_title_label.text = T["erg_tbl2_title"][self.lang].format(w=w)
        # Штанга
        if self.bar_tbl_title_label is not None:
            self.bar_tbl_title_label.text = T["bar_tbl_title"][self.lang]

    # ---- Handlers ----
    def _on_lang_change(self, widget):
        if self._updating: return
        inv = {v: k for k, v in LANG_LABEL.items()}
        self.lang = inv.get(self.lang_sel.value, "ru")
        self._apply_language_texts()
        self._rebuild_time_selects()
        # НЕ рассчитываем автоматически! Только обновляем заголовки уже показанных таблиц (если они есть).
        self._update_existing_titles()
        self._post_build_fixups()

    def _apply_language_texts(self):
        header = self.main_window.content.children[0]
        header.children[0].text = T["title"][self.lang]
        header.children[-2].text = T["language"][self.lang]

        # Эргометр
        self.gender_lbl.text = T["gender"][self.lang]
        self.weight_lbl.text = T["weight"][self.lang]
        self.distance_lbl.text = T["distance"][self.lang]
        self.min_lbl.text = T["minutes"][self.lang]
        self.sec_lbl.text = T["seconds"][self.lang]
        self.cen_lbl.text = T["centis"][self.lang]
        self.btn_erg.text = T["calc"][self.lang]
        # Пол всегда Муж по умолчанию при смене языка
        self.gender.items = GENDER_LABELS[self.lang]
        self.gender.value = GENDER_LABELS[self.lang][1]

        # Штанга
        self.gender_b_lbl.text = T["gender"][self.lang]
        self.weight_b_lbl.text = T["weight"][self.lang]
        self.gender_b.items = GENDER_LABELS[self.lang]
        self.gender_b.value = GENDER_LABELS[self.lang][1]

        self.ex_lbl.text = T["exercise"][self.lang]
        self.bw_lbl.text = T["bar_weight"][self.lang]
        self.reps_lbl.text = T["reps"][self.lang]
        self.btn_bar.text = T["calc"][self.lang]
        self._set_exercise_items()

        # Заголовки вкладок
        try:
            items = list(self.tabs.content)
            items[0].text = T["mode_erg"][self.lang]
            items[1].text = T["mode_bar"][self.lang]
        except Exception:
            pass

    def _set_exercise_items(self):
        current = self.exercise.value
        items = list(EX_UI_TO_KEY[self.lang].keys())
        self.exercise.items = items
        self.exercise.value = current if current in items else items[0]

    def _on_gender_change(self, widget):
        if self._updating: return
        self._rebuild_time_selects()
        self._post_build_fixups()

    def _on_distance_change(self, widget):
        if self._updating: return
        self._rebuild_time_selects()
        self._post_build_fixups()

    def _on_minute_change(self, widget):
        if self._updating: return
        g_key = GENDER_MAP[self.lang].get(self.gender.value, "male")
        dist = int(self.distance.value)
        dist_data = get_distance_data(g_key, dist, self.rowing_data)
        minutes, sec_map = parse_available_times(dist_data)
        seconds = sec_map.get(self.min_sel.value, ["00"])
        self.sec_sel.items = seconds
        self.sec_sel.value = seconds[0]

    # ---- Расчёты ----
    def calculate_erg(self, widget):
        self._dismiss_ios_inputs()
        try:
            bw = float(self.weight.value or 0)
            if not (40 <= bw <= 140):
                self._info(T["err_weight"][self.lang]);
                return

            g_key = GENDER_MAP[self.lang].get(self.gender.value, "male")
            dist = int(self.distance.value)
            dist_data = get_distance_data(g_key, dist, self.rowing_data)
            if not dist_data: self._info(T["err_no_data"][self.lang]); return

            t_norm = f"{self.min_sel.value}:{self.sec_sel.value}"
            dist_data_time = dist_data.get(t_norm) or dist_data.get(t_norm.lstrip("0"))
            if not dist_data_time: self._info(T["err_time_range"][self.lang]); return

            percent = dist_data_time.get("percent")
            strength = get_strength_data(g_key, bw, self.strength_data_all)
            if not strength: self._info(T["err_no_strength"][self.lang]); return

            # Таблица 1 (7x3)
            rows1, keys = [], [k for k in dist_data_time.keys() if k != "percent"]
            kmap = {meters_from_key(k): dist_data_time[k] for k in keys}
            for m in SHOW_DISTANCES:
                if m in kmap:
                    t = kmap[m]
                    rows1.append([f"{m} m", f"{t}.00", get_split_500m(m, t)])

            # Таблица 2 (3x2)
            rows2, labels = [], EX_KEY_TO_LABEL[self.lang]
            for ex_key, ui_label in labels.items():
                kilo = strength.get(ex_key, {}).get(percent)
                if kilo == "1":
                    vmap = strength.get(ex_key, {})
                    kilo = round((float(kilo) + float(vmap.get("1"))) / 2, 2)
                rows2.append([ui_label, f"{kilo} kg"])

            # Показать заголовки + таблицы (только сейчас)
            self.erg_results_holder.children.clear()

            # Заголовок 1
            self.erg_tbl1_title_label = toga.Label(
                T["erg_tbl1_title"][self.lang],
                style=Pack(font_size=F_LABEL, color=CLR_ACCENT, padding_top=6, padding_bottom=2)
            )
            self.erg_results_holder.add(toga.Box(children=[self.erg_tbl1_title_label], style=S_ROW()))
            # Таблица 1
            self.erg_results_holder.add(make_table(rows1, col_flex=[1, 1, 1]))

            # Заголовок 2 (с весом)
            self.erg_tbl2_title_label = toga.Label(
                T["erg_tbl2_title"][self.lang].format(w=int(bw)),
                style=Pack(font_size=F_LABEL, color=CLR_ACCENT, padding_top=6, padding_bottom=2)
            )
            self.erg_results_holder.add(toga.Box(children=[self.erg_tbl2_title_label], style=S_ROW()))
            # Таблица 2
            self.erg_results_holder.add(make_table(rows2, col_flex=[1, 1]))

        except Exception as e:
            self._info(str(e))

    def calculate_bar(self, widget):
        self._dismiss_ios_inputs()
        try:
            bw = float(self.weight_b.value or 0)
            if not (40 <= bw <= 140):
                self._info(T["err_weight"][self.lang]);
                return

            bar_w = float(self.bar_weight.value or 0)
            if not (1 <= bar_w <= 700):
                self._info(T["err_bar_weight"][self.lang]);
                return

            reps = int(self.reps.value or 0)
            if not (1 <= reps <= 30):
                self._info(T["err_reps"][self.lang]);
                return

            rep_max = round((bar_w / REPS_TABLE[reps]) * 100, 2)

            g_key = GENDER_MAP[self.lang].get(self.gender_b.value, "male")
            strength_for_user = get_strength_data(g_key, bw, self.strength_data_all)
            if not strength_for_user: self._info(T["err_no_strength"][self.lang]); return

            ex_key = EX_UI_TO_KEY[self.lang][self.exercise.value]
            ex_table = strength_for_user.get(ex_key, {})
            i_percent = None
            for pct_str, val in ex_table.items():
                if float(val) <= rep_max:
                    i_percent = float(pct_str)
                else:
                    break
            if i_percent is None: self._info(T["err_1rm_map"][self.lang]); return

            distance_data = get_distance_data(g_key, 2000, self.rowing_data)
            km2_res = None
            for k, v in distance_data.items():
                km2_res = k
                if float(v.get("percent")) < i_percent:
                    break

            rows = [
                [T["tbl_1rm"][self.lang], f"{rep_max} кг" if self.lang == "ru" else f"{rep_max} kg"],
                [T["tbl_2k"][self.lang], km2_res],
            ]

            # Показать заголовок + таблицу (только сейчас)
            self.bar_results_holder.children.clear()

            self.bar_tbl_title_label = toga.Label(
                T["bar_tbl_title"][self.lang],
                style=Pack(font_size=F_LABEL, color=CLR_ACCENT, padding_top=6, padding_bottom=2)
            )
            self.bar_results_holder.add(toga.Box(children=[self.bar_tbl_title_label], style=S_ROW()))
            self.bar_results_holder.add(make_table(rows, col_flex=[1, 1]))

        except Exception as e:
            self._info(str(e))


def main():
    return RowStrengthApp("RowStrength", "com.rowstrength")
