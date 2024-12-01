import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import os
import threading


class FileTransferGUI:
    def __init__(self, root, send_dir, callback):
        self.root = root
        self.root.title("Перенос файла")
        self.send_dir = send_dir
        self.callback = callback

        
        self.status_label = tk.Label(root, text="Статус: Ожидание...", font=("Arial", 14))
        self.status_label.pack(pady=10)

        
        self.progress = tk.Label(root, text="Прогресс: 0%", font=("Arial", 14))
        self.progress.pack(pady=10)

        # label
        self.dir_label = tk.Label(root, text="Файлы в директории для отправки:", font=("Arial", 14))
        self.dir_label.pack(pady=10)

        # Директория
        self.dir_listbox = tk.Listbox(root, width=50, height=10)
        self.dir_listbox.pack(pady=10)
        self.refresh_directory_contents()

        # Кнопка добавления файла
        self.add_file_button = tk.Button(root, text="Добавить файл", command=self.add_file)
        self.add_file_button.pack(pady=10)

        # Кнопка обновления
        self.refresh_button = tk.Button(root, text="Обновить", command=self.refresh_directory_contents)
        self.refresh_button.pack(pady=10)

        # Кнопка выхода
        self.quit_button = tk.Button(root, text="Выйти", command=self.quit_app)
        self.quit_button.pack(pady=10)

    def refresh_directory_contents(self):
        try:
            self.dir_listbox.delete(0, tk.END)

            files = os.listdir(self.send_dir)
            for file in files:
                self.dir_listbox.insert(tk.END, file)

            self.update_status("Директория была обновлена.")
        except Exception as e:
            messagebox.showerror("ошибка", f"Ошибка при обновлении директории: {e}")

    def update_status(self, text):
        self.status_label.config(text=f"Статус: {text}")

    def update_progress(self, progress):
        self.progress.config(text=f"Прогресс: {progress}%")

    def add_file(self):
        file_path = filedialog.askopenfilename(title="Выберите файл для отправки")
        if file_path:
            try:
                filename = os.path.basename(file_path)
                shutil.copy(file_path, os.path.join(self.send_dir, filename))
                self.update_status(f"Файл {filename} успешно добавлен в директорию.")
                self.refresh_directory_contents()

                threading.Thread(target=self.process_file, args=(file_path,)).start()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Файл не был добавлен: {e}")

    def process_file(self, file_path):
        self.update_status(f"Загрузка {os.path.basename(file_path)}...")
        try:
            self.callback(file_path)
            self.update_progress(100)
            self.update_status("Файл успешно загружен.")
            self.refresh_directory_contents()
        except Exception as e:
            self.update_status(f"Ошибка: {e}")
            messagebox.showerror("Произошла ошибка:", str(e))

    def quit_app(self):
        self.root.destroy()
