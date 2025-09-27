import sys
import re
import json
from importlib import resources
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

# ---------- Константы ----------
DISTANCES = [500, 1000, 1500, 2000, 2500, 3000, 4000, 5000, 6000, 8000, 10000]
GENDERS_UI = {"ж": "female", "м": "male"}
EXERCISES_UI_TO_KEY = {"жим": "bench-press", "присед": "squat", "тяга": "deadlift"}
EXERCISES_KEY_TO_RU = {"bench-press": "жиме", "squat": "приседе", "deadlift": "становой тяге"}
MODE_CHOICES = ["Эргометр", "Штанга"]

REPS_TABLE = {
    1: 100, 2: 97, 3: 94, 4: 92, 5: 89, 6: 86, 7: 83, 8: 81, 9: 78, 10: 75,
    11: 73, 12: 71, 13: 70, 14: 68, 15: 67, 16: 65, 17: 64, 18: 63, 19: 61,
    20: 60, 21: 59, 22: 58, 23: 57, 24: 56, 25: 55, 26: 54, 27: 53, 28: 52,
    29: 51, 30: 50
}

# ---------- Стили (крупнее и «воздушнее» под iOS) ----------
IS_IOS = (sys.platform == "ios")
F_HEAD = 22 if IS_IOS else 18
F_LABEL = 16 if IS_IOS else 14
F_INPUT = 16 if IS_IOS else 14
PAD_MAIN = 18 if IS_IOS else 14
GAP_MAIN = 14 if IS_IOS else 10

S_MAIN = Pack(direction=COLUMN, padding=PAD_MAIN, gap=GAP_MAIN)
S_ROW = Pack(direction=ROW, gap=10, padding_bottom=6)
S_HEAD = Pack(font_size=F_HEAD, padding_bottom=6)
S_LABEL = Pack(font_size=F_LABEL, padding_right=8)
S_INPUT = Pack(font_size=F_INPUT)
S_BTN = Pack(padding_top=6, padding_bottom=6)
S_OUT = Pack(height=140, font_size=F_INPUT, padding_top=4)


# ---------- Утилиты ----------
def load_json_from_package(filename: str):
    with resources.files(__package__).joinpath("data").joinpath(filename).open("r", encoding="utf-8") as f:
        return json.load(f)


def get_distance_data(i_gender, i_distance, rowing_data):
    return rowing_data.get(i_gender, {}).get(str(i_distance), {})


def get_strength_data(i_gender, i_weight, strength_data):
    return strength_data.get(i_gender, {}).get(str(i_weight), {})


def normalize_time_str(time_str: str) -> str:
    """ '6:11'/'06:11'/'06:11.0' → '06:11' """
    m = re.match(r"^\s*(\d{1,2}):(\d{2})(?:[.,](\d{1,2}))?\s*$", (time_str or ""))
    if not m:
        raise ValueError("Неверный формат времени. Используйте MM:SS или MM:SS.ms")
    mm, ss = int(m.group(1)), int(m.group(2))
    if ss >= 60 or mm < 0:
        raise ValueError("Секунды должны быть < 60")
    return f"{mm:02d}:{ss:02d}"


# ---------- Приложение ----------
class RowStrengthApp(toga.App):
    def startup(self):
        # Данные
        self.rowing_data = load_json_from_package("data_for_rowing_app.json")
        self.strength_data_all = load_json_from_package("data_for_strength_app.json")

        # Заголовок
        title = toga.Label("RowStrength", style=S_HEAD)

        # Режим: iOS → SegmentedButton, иначе Selection
        self.mode_widget = self._make_mode_widget()

        # Общие поля
        self.gender = toga.Selection(items=["ж", "м"], value="м", style=S_INPUT)
        # NumberInput: используем min/max (min_value/max_value в старых версиях не поддерживаются)
        self.weight = toga.NumberInput(step=1, min=40, max=140, value=80, style=S_INPUT)

        # Режим 1 (Эргометр → Штанга)
        self.distance = toga.Selection(items=[str(d) for d in DISTANCES], value="2000", style=S_INPUT)
        self.time_input = toga.TextInput(placeholder="MM:SS[.ms]", style=S_INPUT)
        self.res1_output = toga.MultilineTextInput(readonly=True, style=S_OUT)

        # Режим 2 (Штанга → Эргометр)
        self.exercise = toga.Selection(items=[i.capitalize() for i in list(EXERCISES_UI_TO_KEY.keys())], value="Жим", style=S_INPUT)
        self.bar_weight = toga.NumberInput(step=1, min=1, value=100, style=S_INPUT)
        self.reps = toga.NumberInput(step=1, min=1, max=30, value=5, style=S_INPUT)
        self.res2_output = toga.MultilineTextInput(readonly=True, style=S_OUT)

        # Кнопка
        self.calc_button = toga.Button("Рассчитать", on_press=self.calculate, style=S_BTN)

        # Компоновка — крупные отступы, структурированные блоки
        head_row = toga.Box(children=[title], style=Pack(direction=ROW, padding_bottom=8))

        mode_row = toga.Box(
            children=[toga.Label("Режим:", style=S_LABEL), self.mode_widget],
            style=S_ROW
        )
        common_row = toga.Box(
            children=[toga.Label("Пол:", style=S_LABEL), self.gender,
                      toga.Label("Вес (кг):", style=S_LABEL), self.weight],
            style=S_ROW
        )

        self.mode1_box = toga.Box(
            children=[toga.Label("Дистанция:", style=S_LABEL), self.distance,
                      toga.Label("Время:", style=S_LABEL), self.time_input],
            style=S_ROW
        )
        self.mode2_box = toga.Box(
            children=[toga.Label("Упражнение:", style=S_LABEL), self.exercise,
                      toga.Label("Вес на штанге (кг):", style=S_LABEL), self.bar_weight,
                      toga.Label("Повторы:", style=S_LABEL), self.reps],
            style=S_ROW
        )

        self.results_box = toga.Box(
            children=[self.res1_output, self.res2_output],
            style=Pack(direction=COLUMN, gap=10, padding_top=4)
        )

        main_box = toga.Box(
            children=[head_row, mode_row, common_row, self.mode1_box, self.mode2_box, self.calc_button,
                      self.results_box],
            style=S_MAIN
        )

        # Показ/скрытие нужных блоков
        self._on_mode_changed(None)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

    # ---- вспомогательные методы UI ----
    def _make_mode_widget(self):
        """Создание переключателя режима: iOS -> SegmentedButton, иначе Selection."""
        if IS_IOS and hasattr(toga, "SegmentedButton"):
            widget = toga.SegmentedButton(items=MODE_CHOICES, on_change=self._on_mode_changed)
            # предварительное значение
            # у SegmentedButton value — текст выбранного сегмента
            widget.value = MODE_CHOICES[0]
            return widget
        else:
            return toga.Selection(items=MODE_CHOICES, value=MODE_CHOICES[0], on_change=self._on_mode_changed,
                                  style=S_INPUT)

    def _get_mode_value(self) -> str:
        """Единый способ получить значение режима для SegmentedButton/Selection."""
        # SegmentedButton имеет .value (строка); Selection тоже .value
        return self.mode_widget.value

    def _on_mode_changed(self, widget):
        if self._get_mode_value() == MODE_CHOICES[0]:
            # Эргометр → Штанга
            self.mode1_box.style.update(visibility="visible")
            self.res1_output.style.update(visibility="visible")
            self.mode2_box.style.update(visibility="hidden")
            self.res2_output.style.update(visibility="hidden")
        else:
            # Штанга → Эргометр
            self.mode1_box.style.update(visibility="hidden")
            self.res1_output.style.update(visibility="hidden")
            self.mode2_box.style.update(visibility="visible")
            self.res2_output.style.update(visibility="visible")

    # ---- бизнес-логика ----
    def calculate(self, widget):
        try:
            g_key = GENDERS_UI[self.gender.value]
            weight = int(self.weight.value)

            if self._get_mode_value() == MODE_CHOICES[0]:
                # --- Эргометр → Штанга ---
                distance = int(self.distance.value)
                distance_data = get_distance_data(g_key, distance, self.rowing_data)
                if not distance_data:
                    raise ValueError("Нет данных по выбранной дистанции/полу")

                t_norm = normalize_time_str(self.time_input.value)
                distance_data_time = distance_data.get(t_norm) or distance_data.get(t_norm.lstrip("0"))
                if not distance_data_time:
                    times_str = list(distance_data.keys())
                    raise ValueError(f"Время вне диапазона. Доступно: от {times_str[0]} до {times_str[-1]}")

                percent = distance_data_time.get("percent")
                strength = get_strength_data(g_key, weight, self.strength_data_all)
                if not strength:
                    raise ValueError("Нет силовых данных для указанного веса")

                lines = ["Ваши расчётные максимумы на дистанциях:"]
                for k, v in distance_data_time.items():
                    if k != "percent":
                        lines.append(f"{k} — {v}.00")

                lines.append("\nС учётом вашего веса это сопоставимо со следующими результатами в штанге:")
                for ex_key, ex_label_ru in EXERCISES_KEY_TO_RU.items():
                    kilo = strength.get(ex_key, {}).get(percent)
                    if kilo == "1":
                        vmap = strength.get(ex_key, {})
                        kilo = round((float(kilo) + float(vmap.get("1"))) / 2, 2)
                    lines.append(f"В {ex_label_ru} — {kilo} кг")

                self.res1_output.value = "\n".join(lines)

            else:
                # --- Штанга → Эргометр ---
                ex_key = EXERCISES_UI_TO_KEY[self.exercise.value]
                bar_w = float(self.bar_weight.value)
                reps = int(self.reps.value)
                if reps not in REPS_TABLE:
                    raise ValueError("Поддерживаются повторы 1..30")

                rep_max = round((bar_w / REPS_TABLE[reps]) * 100, 2)

                strength_for_user = get_strength_data(g_key, weight, self.strength_data_all)
                if not strength_for_user:
                    raise ValueError("Нет силовых данных для указанного веса")

                ex_table = strength_for_user.get(ex_key, {})
                i_percent = None
                for pct_str, val in ex_table.items():
                    if float(val) <= rep_max:
                        i_percent = float(pct_str)
                    else:
                        break
                if i_percent is None:
                    raise ValueError("Не удалось сопоставить проценты для 1ПМ")

                distance_data = get_distance_data(g_key, 2000, self.rowing_data)
                km2_res = None
                for k, v in distance_data.items():
                    km2_res = k
                    if float(v.get("percent")) < i_percent:
                        break

                self.res2_output.value = "\n".join([
                    f"Ваш примерный разовый максимум: {rep_max} кг",
                    f"С учётом веса — сопоставимо с результатом: {km2_res} на 2 км на гребном эргометре"
                ])

        except Exception as e:
            try:
                self.main_window.error_dialog("Ошибка", str(e))
            except Exception:
                print("Ошибка:", e)


def main():
    return RowStrengthApp("RowStrength", "com.rowstrength")
