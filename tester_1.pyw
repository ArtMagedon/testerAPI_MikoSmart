import tkinter as tk
from tkinter import ttk, font
import json
import os
import requests
from ctypes import windll

# Включение поддержки High-DPI для четкого отображения текста на Windows
windll.shcore.SetProcessDpiAwareness(2)

# Определение пути к файлу сохранения (рядом со скриптом)
SAVE_FILE = f"{os.path.abspath(__file__).replace(os.path.basename(__file__), '')}\\saved_data.json"

# --- КОНСТАНТЫ И НАСТРОЙКИ ---
TOTAL_ROWS = 20
VISIBLE_ROWS = 3
BLOCK_ROWS = 12
TEXT_ROWS = 12
methods = ["GET", "PUT", "POST", "DELETE"]

# Настройки шрифтов для различных элементов интерфейса
default_fonts = {
    "label": {"family": "Arial", "size": 10, "weight": "bold"},
    "combo": {"family": "Arial", "size": 10, "weight": "bold"},
    "entry": {"family": "Consolas", "size": 10},
    "button": {"family": "Arial", "size": 10},
    "body": {"family": "Consolas", "size": 10},
    "output": {"family": "Consolas", "size": 10}
}

#def print_window_size():
#   width = root.winfo_width()
#    height = root.winfo_height()
#    print(f"Window size: {width}x{height}")
#    root.after(1000, print_window_size)  # через 1000 мс вызываем снова

# Функция добавления контекстного меню (ПКМ -> Вставить)
def add_context_menu(widget):
    menu = tk.Menu(widget, tearoff=0)
    menu.add_command(label="Вставить", command=lambda: widget.insert(
        tk.INSERT, widget.clipboard_get()))

    def show_menu(event):
        menu.tk_popup(event.x_root, event.y_root)

    widget.bind("<Button-3>", show_menu)

# Логика выполнения HTTP-запроса при нажатии кнопки Send
def button_action(row):
    # Сбор данных из полей ввода
    method = method_vars[row].get()
    path = entry_vars[row].get()
    body = text_widgets_body[row].get("1.0", tk.END).strip()
    base_url = top_entry_var.get().strip()

    # Проверка наличия базового URL
    if not base_url:
        output_widgets[row].delete("1.0", tk.END)
        output_widgets[row].insert(
            tk.END, "❌ Укажите базовый адрес в верхнем поле")
        return

    # Формирование полного URL
    url = base_url.rstrip("/") + "/" + path.lstrip("/")

    # Выполнение запроса в зависимости от выбранного метода
    try:
        if method == "GET":
            resp = requests.get(url)
        elif method == "POST":
            resp = requests.post(url, data=body)
        elif method == "PUT":
            resp = requests.put(url, data=body)
        elif method == "DELETE":
            resp = requests.delete(url, data=body)
        else:
            resp = None

        # Вывод результата в правое текстовое поле
        if resp is not None:
            output_widgets[row].delete("1.0", tk.END)
            output_widgets[row].insert(
                tk.END, f"Status: {resp.status_code}\n\n{resp.text}")
    except Exception as e:
        output_widgets[row].delete("1.0", tk.END)
        output_widgets[row].insert(tk.END, f"❌ Ошибка: {e}")

# Функция сохранения состояния всех полей в JSON файл
def save_data():
    data = {
        "top": top_entry_var.get(),
        "blocks": [],
        "fonts": default_fonts
    }
    # Проход по всем блокам и сбор данных
    for i in range(TOTAL_ROWS):
        data["blocks"].append({
            "label": label_vars[i].get(),
            "method": method_vars[i].get(),
            "entry": entry_vars[i].get(),
            "body": text_widgets_body[i].get("1.0", tk.END).strip(),
            # "output": output_widgets[i].get("1.0", tk.END).strip()
        })
    
    # Запись в файл
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("Data saved successfully")

    # --- ВИЗУАЛЬНОЕ ПОДТВЕРЖДЕНИЕ ---
    # Проверяем, создана ли уже кнопка (чтобы не было ошибок при авто-сохранении при закрытии)
    if 'btn_save_manual' in globals() and btn_save_manual.winfo_exists():
        # Если кнопка еще не "зеленая" (защита от спама нажатий), запоминаем цвет
        if btn_save_manual.cget("text") != "✔ ОК":
            original_bg = btn_save_manual.cget("bg")
            
            # Меняем вид кнопки: светло-зеленый фон и текст "ОК"
            btn_save_manual.config(text="✔ ОК", bg="#98FB98") 

            # Внутренняя функция для возврата кнопки в исходное состояние
            def revert_button():
                if btn_save_manual.winfo_exists():
                    btn_save_manual.config(text="Сохранить", bg=original_bg)
            
            # Запускаем таймер возврата через 700 мс
            root.after(700, revert_button)


# Создание пустого файла конфигурации, если он отсутствует
def create_json_file(n: int = 20, filename: str = "file.json"):
    data = {"top": "",
            "fonts": default_fonts,
            "blocks": []}
    for i in range(1, n + 1):
        temp = {"label": f"№{i}",
            "Method": "GET",
            "entry": "",
            "body": ""
        }
        data["blocks"].append(temp)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Загрузка настроек шрифтов из файла или использование стандартных
def load_fonts():
    if not os.path.exists(SAVE_FILE):
        create_json_file(n=TOTAL_ROWS, filename=SAVE_FILE)
    with open(SAVE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    fonts_data = data.get("fonts", default_fonts)
    
    # Инициализация объектов шрифтов
    for key, params in fonts_data.items():
        default_fonts[key] = params
        font_objects[key] = font.Font(**params)
    for key, params in default_fonts.items():
        font_objects[key] = font.Font(**params)

# Загрузка сохраненных данных в поля интерфейса
def load_data():
    if not os.path.exists(SAVE_FILE):
        return
    with open(SAVE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    top_entry_var.set(data.get("top", ""))

    for i in range(TOTAL_ROWS):
        if i < len(data.get("blocks", [])):
            label_vars[i].set(data["blocks"][i].get("label", f"№{i+1}"))
            method_vars[i].set(data["blocks"][i].get("method", "GET"))
            entry_vars[i].set(data["blocks"][i].get("entry", ""))
            
            text_widgets_body[i].delete("1.0", tk.END)
            text_widgets_body[i].insert(
                "1.0", data["blocks"][i].get("body", ""))
            
            output_widgets[i].delete("1.0", tk.END)
            output_widgets[i].insert(
                "1.0", data["blocks"][i].get("output", ""))

# Обработка событий прокрутки колесиком мыши (для Windows/Linux)
def bind_mousewheel(widget, command):
    def _on_mousewheel(event):
        if event.delta:
            command(int(-1*(event.delta/120)))
        else:
            if event.num == 4:
                command(-1)
            elif event.num == 5:
                command(1)
    widget.bind_all("<MouseWheel>", _on_mousewheel)
    widget.bind_all("<Button-4>", _on_mousewheel)
    widget.bind_all("<Button-5>", _on_mousewheel)

# Настройка независимой прокрутки внутри текстовых полей
def bind_text_scroll(text_widget):
    def _on_mousewheel_text(event):
        text_widget.yview_scroll(int(-1*(event.delta/120)), "units")
        return "break"  
    
    # Перехват прокрутки при наведении на текстовое поле
    text_widget.bind("<Enter>", lambda e: text_widget.bind_all(
        "<MouseWheel>", _on_mousewheel_text))
    # Возврат прокрутки холста при уходе курсора
    text_widget.bind("<Leave>", lambda e: bind_mousewheel(
        canvas, lambda step: canvas.yview_scroll(step, "units")))

# --- ИНИЦИАЛИЗАЦИЯ ГЛАВНОГО ОКНА ---
root = tk.Tk()
root.title("REST Client GUI (20 блоков с прокруткой)")

# Настройка вкладок
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

tab1 = ttk.Frame(notebook)
notebook.add(tab1, text="REST Client")

tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="Config")

# Метка для базового URL
top_label = tk.Label(tab1, text="Базовый URL:", font=(
    default_fonts["label"]["family"], default_fonts["label"]["size"], default_fonts["label"]["weight"]))
top_label.pack(anchor="w", padx=5, pady=(10, 0))

# --- ВЕРХНЯЯ ПАНЕЛЬ С ПОЛЕМ ВВОДА И КНОПКОЙ СОХРАНЕНИЯ ---
top_frame_container = tk.Frame(tab1)
top_frame_container.pack(fill="x", padx=5, pady=5)

top_entry_var = tk.StringVar()
# Поле ввода (занимает всё доступное место слева)
top_entry = tk.Entry(top_frame_container, textvariable=top_entry_var)
top_entry.pack(side="left", fill="x", expand=True)
add_context_menu(top_entry)

# Кнопка сохранения (прижата справа)
btn_save_manual = tk.Button(top_frame_container, text="Сохранить", command=save_data)
btn_save_manual['font'] = default_fonts["button"]
btn_save_manual.pack(side="right", padx=(10, 0))

# Разделитель под верхней панелью
separator = ttk.Separator(tab1, orient='horizontal')
separator.pack(fill="x", padx=5, pady=5)

# --- ОБЛАСТЬ ПРОКРУТКИ (CANVAS) ---
container = tk.Frame(tab1)
container.pack(fill="both", expand=True)

canvas = tk.Canvas(container)

scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

# Обновление области прокрутки при изменении размера фрейма
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind("<Configure>", lambda e: canvas.itemconfigure(
    window_id, width=e.width))

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Настройка веса колонок сетки для правильного растягивания
scrollable_frame.grid_columnconfigure(3, weight=1)
scrollable_frame.grid_columnconfigure(4, weight=1)

# Инициализация списков для хранения ссылок на виджеты и переменные
label_vars = []
method_vars = []
entry_vars = []
text_widgets_body = []
output_widgets = []
font_objects = {}

load_fonts()

# --- ГЕНЕРАЦИЯ БЛОКОВ ЗАПРОСОВ ---
for i in range(1, TOTAL_ROWS*(BLOCK_ROWS+1), BLOCK_ROWS+1):
    label_var = tk.StringVar()
    method_var = tk.StringVar(value=methods[0])
    entry_var = tk.StringVar()
    label_vars.append(label_var)
    method_vars.append(method_var)
    entry_vars.append(entry_var)

    # Метка с номером блока
    numeric = tk.Label(scrollable_frame, textvariable=label_var)
    numeric['font'] = font_objects["label"]
    numeric.grid(row=i, column=0, sticky="w", padx=5, pady=0)

    # Функция создания выпадающего меню с цветовой кодировкой
    def make_option_menu_color(var):
        menu = tk.OptionMenu(scrollable_frame, var, *methods)
        menu['font'] = font_objects["combo"]

        def update_color(*args):
            value = var.get()
            if value == "GET":
                menu.config(fg="green")
            elif value == "POST":
                menu.config(fg="blue")
            elif value == "PUT":
                menu.config(fg="orange")
            elif value == "DELETE":
                menu.config(fg="red")
            else:
                menu.config(fg="black")

        var.trace_add("write", update_color)
        update_color()
        return menu

    # Меню выбора метода (GET, POST...)
    combo = make_option_menu_color(method_var)
    combo.grid(row=i, column=1, padx=(55, 0), pady=0, sticky="w")

    # Поле ввода пути (Endpoint)
    entry = tk.Entry(scrollable_frame, textvariable=entry_var, width=56)
    entry['font'] = font_objects["entry"]
    entry.grid(row=i+1, column=0, columnspan=3, padx=3, pady=0)
    add_context_menu(entry)

    # Кнопка отправки запроса
    btn = tk.Button(scrollable_frame, text="Send", width=34,
                    command=lambda r=i//BLOCK_ROWS: button_action(r))
    btn['font'] = font_objects["button"]
    btn.grid(row=i+2, column=0, columnspan=3, padx=3, pady=0)

    # Поле для ввода тела запроса (Body)
    frame_body = tk.Frame(scrollable_frame)
    frame_body.grid(row=i, column=3, rowspan=BLOCK_ROWS,
                    padx=3, pady=12, sticky="nsew")
    body_widget = tk.Text(frame_body, height=TEXT_ROWS, width=44)
    body_widget['font'] = font_objects["body"]
    
    scrollbar_body = tk.Scrollbar(
        frame_body, orient="vertical", command=body_widget.yview)
    body_widget.configure(yscrollcommand=scrollbar_body.set)
    
    body_widget.pack(side="left", fill="both", expand=True)
    scrollbar_body.pack(side="right", fill="y")
    
    text_widgets_body.append(body_widget)
    bind_text_scroll(body_widget)
    add_context_menu(body_widget)

    # Поле для вывода ответа (Response)
    frame_out = tk.Frame(scrollable_frame)
    frame_out.grid(row=i, column=4, rowspan=BLOCK_ROWS,
                   padx=(3, 10), pady=12, sticky="nsew")
    out_widget = tk.Text(frame_out, height=TEXT_ROWS, width=44)
    out_widget['font'] = font_objects["output"]
    
    scrollbar_out = tk.Scrollbar(
        frame_out, orient="vertical", command=out_widget.yview)
    out_widget.configure(yscrollcommand=scrollbar_out.set)
    
    out_widget.pack(side="left", fill="both", expand=True)
    scrollbar_out.pack(side="right", fill="y")
    
    output_widgets.append(out_widget)
    bind_text_scroll(out_widget)

    # Горизонтальный разделитель между блоками
    separator_row = ttk.Separator(scrollable_frame, orient='horizontal')
    separator_row.grid(row=i+(BLOCK_ROWS), column=0,
                   columnspan=5, sticky='ew', pady=0)

# Загрузка данных после построения интерфейса
load_data()
bind_mousewheel(canvas, lambda step: canvas.yview_scroll(step, "units"))

root.update_idletasks()

# Расчет геометрии окна на основе размеров блоков
block_height = text_widgets_body[0].winfo_height() + 16 + 10
window_height = block_height * VISIBLE_ROWS + top_entry.winfo_height() + top_label.winfo_reqheight() + 56
root.geometry(f"{window_height*2}x{window_height}")
root.minsize(width=440+48*(default_fonts["body"]["size"]+default_fonts["output"]["size"]), height=window_height)
root.resizable(True, True)

# Обработчик закрытия окна (автосохранение)
root.protocol("WM_DELETE_WINDOW", lambda: (save_data(), root.destroy()))

# --- ПРИВЯЗКА ГОРЯЧИХ КЛАВИШ ---
# Ctrl+S для сохранения (на Windows работает даже при русской раскладке, так как считывает код клавиши)
root.bind("<Control-s>", lambda event: save_data())
root.bind("<Control-S>", lambda event: save_data())

root.mainloop()