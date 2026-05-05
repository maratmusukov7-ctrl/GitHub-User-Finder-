import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import requests


class GitHubUserFinder:
    """Класс для управления поиском пользователей GitHub"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🔍 GitHub User Finder")
        self.root.geometry("950x750")
        self.root.minsize(850, 700)
        self.root.configure(bg="#f0f0f0")
        
        self.favorites = []
        self.search_results = []
        self.filename = "favorites.json"
        
        # GitHub API URL
        self.api_url = "https://api.github.com"
        
        self.create_widgets()
        self.load_favorites()
    
    def create_widgets(self):
        """Создание элементов интерфейса"""
        
        # Заголовок
        title_label = tk.Label(
            self.root,
            text="🔍 GitHub User Finder",
            font=("Arial", 20, "bold"),
            bg="#f0f0f0",
            fg="#1a1a2e"
        )
        title_label.pack(pady=15)
        
        # Фрейм для поиска
        search_frame = tk.LabelFrame(
            self.root,
            text="Поиск пользователя",
            font=("Arial", 12, "bold"),
            bg="#ffffff",
            padx=15,
            pady=15
        )
        search_frame.pack(fill="x", padx=20, pady=10)
        
        # Поле ввода
        tk.Label(search_frame, text="Имя пользователя:", bg="#ffffff", 
                font=("Arial", 10)).grid(row=0, column=0, sticky="e", pady=5)
        self.entry_username = tk.Entry(search_frame, width=30, font=("Arial", 11))
        self.entry_username.grid(row=0, column=1, padx=10, pady=5)
        self.create_tooltip(self.entry_username, "Введите имя пользователя GitHub")
        
        # Кнопка поиска
        btn_search = tk.Button(
            search_frame,
            text="🔍 Найти",
            command=self.search_user,
            bg="#2196F3",
            fg="white",
            font=("Arial", 11, "bold"),
            width=15,
            height=2
        )
        btn_search.grid(row=0, column=2, padx=10, pady=5)
        self.create_tooltip(btn_search, "Найти пользователя на GitHub")
        
        # Кнопка очистки
        btn_clear = tk.Button(
            search_frame,
            text="🔄 Очистить",
            command=self.clear_search,
            bg="#FF9800",
            fg="white",
            font=("Arial", 11, "bold"),
            width=15,
            height=2
        )
        btn_clear.grid(row=0, column=3, padx=10, pady=5)
        self.create_tooltip(btn_clear, "Очистить поле поиска")
        
        # Фрейм для результатов поиска
        results_frame = tk.LabelFrame(
            self.root,
            text="Результаты поиска",
            font=("Arial", 12, "bold"),
            bg="#ffffff",
            padx=15,
            pady=15
        )
        results_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Информация о пользователе
        self.info_text = tk.Text(
            results_frame,
            height=8,
            width=80,
            font=("Arial", 11),
            bg="#e3f2fd",
            fg="#1565C0",
            wrap="word",
            relief="solid",
            bd=2
        )
        self.info_text.pack(pady=10, padx=10)
        
        # Кнопка добавить в избранное
        btn_add_favorite = tk.Button(
            results_frame,
            text="⭐ Добавить в избранное",
            command=self.add_to_favorites,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11, "bold"),
            width=25,
            height=2
        )
        btn_add_favorite.pack(pady=10)
        self.create_tooltip(btn_add_favorite, "Добавить пользователя в избранное")
        
        # Фрейм для избранного
        favorites_frame = tk.LabelFrame(
            self.root,
            text="⭐ Избранные пользователи",
            font=("Arial", 12, "bold"),
            bg="#ffffff",
            padx=15,
            pady=15
        )
        favorites_frame.pack(fill="x", padx=20, pady=10)
        
        # Список избранных (Listbox)
        self.favorites_listbox = tk.Listbox(
            favorites_frame,
            font=("Arial", 10),
            bg="#fff9e6",
            fg="#333333",
            selectbackground="#FF9800",
            selectforeground="white",
            relief="solid",
            bd=2,
            height=6
        )
        self.favorites_listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        scrollbar = tk.Scrollbar(favorites_frame, orient="vertical", 
                                 command=self.favorites_listbox.yview)
        self.favorites_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y", pady=5)
        
        # Кнопки управления избранным
        fav_btn_frame = tk.Frame(self.root, bg="#f0f0f0")
        fav_btn_frame.pack(pady=5)
        
        btn_remove_favorite = tk.Button(
            fav_btn_frame,
            text="🗑️ Удалить из избранного",
            command=self.remove_from_favorites,
            bg="#f44336",
            fg="white",
            font=("Arial", 10, "bold"),
            width=22,
            height=2
        )
        btn_remove_favorite.pack(side="left", padx=5)
        self.create_tooltip(btn_remove_favorite, "Удалить пользователя из избранного")
        
        btn_save = tk.Button(
            fav_btn_frame,
            text="💾 Сохранить",
            command=self.save_favorites,
            bg="#9C27B0",
            fg="white",
            font=("Arial", 10, "bold"),
            width=22,
            height=2
        )
        btn_save.pack(side="left", padx=5)
        self.create_tooltip(btn_save, "Сохранить избранное в JSON")
        
        # Статус бар
        self.status_label = tk.Label(
            self.root,
            text=f"Избранных: 0",
            font=("Arial", 10),
            bg="#1a1a2e",
            fg="white",
            pady=5
        )
        self.status_label.pack(fill="x", side="bottom")
    
    def create_tooltip(self, widget, text):
        """Создание подсказки для виджета"""
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry("+0+0")
        tooltip.withdraw()
        
        label = tk.Label(
            tooltip,
            text=text,
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            font=("Arial", 9)
        )
        label.pack()
        
        def show_tooltip(event):
            tooltip.deiconify()
            x = widget.winfo_rootx() + 20
            y = widget.winfo_rooty() + widget.winfo_height() + 5
            tooltip.wm_geometry(f"+{x}+{y}")
        
        def hide_tooltip(event):
            tooltip.withdraw()
        
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)
    
    def validate_input(self, username):
        """Проверка корректности ввода"""
        
        if not username.strip():
            messagebox.showerror("Ошибка", "Введите имя пользователя GitHub!")
            return False
        
        return True
    
    def search_user(self):
        """Поиск пользователя на GitHub"""
        
        username = self.entry_username.get().strip()
        
        if not self.validate_input(username):
            return
        
        try:
            # Запрос к GitHub API
            url = f"{self.api_url}/users/{username}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                self.search_results = user_data
                self.display_user_info(user_data)
            elif response.status_code == 404:
                messagebox.showerror("Ошибка", f"Пользователь '{username}' не найден!")
                self.clear_info()
            else:
                messagebox.showerror("Ошибка", f"Ошибка API: {response.status_code}")
                self.clear_info()
                
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Ошибка соединения: {str(e)}")
            self.clear_info()
        except json.JSONDecodeError:
            messagebox.showerror("Ошибка", "Ошибка обработки данных API")
            self.clear_info()
    
    def display_user_info(self, user_data):
        """Отображение информации о пользователе"""
        
        self.info_text.delete("1.0", tk.END)
        
        info = f"""
👤 Имя пользователя: {user_data.get('login', 'N/A')}
📛 Имя: {user_data.get('name', 'N/A')}
📍 Локация: {user_data.get('location', 'N/A')}
🔗 Профиль: {user_data.get('html_url', 'N/A')}
📝 Публичные репозитории: {user_data.get('public_repos', 0)}
👥 Подписчики: {user_data.get('followers', 0)}
📅 Создан: {user_data.get('created_at', 'N/A')}
📄 Биография: {user_data.get('bio', 'N/A')}
        """
        
        self.info_text.insert("1.0", info)
    
    def clear_info(self):
        """Очистка информации о пользователе"""
        
        self.info_text.delete("1.0", tk.END)
        self.search_results = []
    
    def clear_search(self):
        """Очистка поля поиска"""
        
        self.entry_username.delete(0, tk.END)
        self.clear_info()
    
    def add_to_favorites(self):
        """Добавление пользователя в избранное"""
        
        if not self.search_results:
            messagebox.showwarning("Внимание", "Сначала найдите пользователя!")
            return
        
        username = self.search_results.get('login')
        
        # Проверка на дубликат
        for fav in self.favorites:
            if fav.get('login') == username:
                messagebox.showinfo("Инфо", f"Пользователь '{username}' уже в избранном!")
                return
        
        # Добавление в избранное
        favorite = {
            "login": username,
            "name": self.search_results.get('name', 'N/A'),
            "html_url": self.search_results.get('html_url', ''),
            "public_repos": self.search_results.get('public_repos', 0),
            "followers": self.search_results.get('followers', 0)
        }
        
        self.favorites.append(favorite)
        self.update_favorites_list()
        self.save_favorites()
        
        messagebox.showinfo("Успех", f"Пользователь '{username}' добавлен в избранное!")
        self.status_label.config(text=f"Избранных: {len(self.favorites)}")
    
    def remove_from_favorites(self):
        """Удаление пользователя из избранного"""
        
        selected = self.favorites_listbox.curselection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите пользователя для удаления!")
            return
        
        index = selected[0]
        username = self.favorites[index].get('login')
        
        confirm = messagebox.askyesno("Подтверждение", 
                                      f"Удалить '{username}' из избранного?")
        
        if confirm:
            self.favorites.pop(index)
            self.update_favorites_list()
            self.save_favorites()
            messagebox.showinfo("Успех", f"Пользователь '{username}' удалён из избранного!")
            self.status_label.config(text=f"Избранных: {len(self.favorites)}")
    
    def update_favorites_list(self):
        """Обновление списка избранных"""
        
        self.favorites_listbox.delete(0, tk.END)
        
        for fav in self.favorites:
            display_text = f"{fav['login']} — {fav['name']} ({fav['followers']} followers)"
            self.favorites_listbox.insert(tk.END, display_text)
    
    def save_favorites(self):
        """Сохранение избранных в JSON"""
        
        try:
            with open(self.filename, "w", encoding="utf-8") as file:
                json.dump(self.favorites, file, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")
    
    def load_favorites(self):
        """Загрузка избранных из JSON"""
        
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as file:
                    self.favorites = json.load(file)
                self.update_favorites_list()
                self.status_label.config(text=f"Избранных: {len(self.favorites)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить: {e}")
                self.favorites = []
        else:
            self.favorites = []


# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()
