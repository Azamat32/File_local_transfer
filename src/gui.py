import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import os
import threading
from PIL import Image, ImageTk
class ModeSelectionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Выбор режима")
        self.selected_mode = None

        tk.Label(root, text="Выберите режим:").pack(pady=10)

        server_button = tk.Button(root, text="Сервер", command=self.select_server)
        server_button.pack(pady=5)

        client_button = tk.Button(root, text="Клиент", command=self.select_client)
        client_button.pack(pady=5)

    def select_server(self):
        self.selected_mode = "server"
        self.root.quit()

    def select_client(self):
        self.selected_mode = "client"
        self.root.quit()


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

    def display_qr_code(self, qr_code_path):
        # Schedule the QR code display on the main thread
        self.root.after(0, lambda: self._show_qr_code(qr_code_path))

    def _show_qr_code(self, qr_code_path):
        qr_window = tk.Toplevel(self.root)
        qr_window.attributes('-fullscreen', True)  # Fullscreen mode
        qr_window.configure(bg='black')  # Black background
        
        try:
            qr_image = tk.PhotoImage(file=qr_code_path)

            screen_width = qr_window.winfo_screenwidth()
            screen_height = qr_window.winfo_screenheight()

            scaled_image = qr_image.subsample(
                max(qr_image.width() // screen_width, 1),
                max(qr_image.height() // screen_height, 1)
            )

            qr_label = tk.Label(qr_window, image=scaled_image, bg='black')
            qr_label.image = scaled_image
            qr_label.place(relx=0.5, rely=0.5, anchor='center')

            def close_qr(event=None):
                qr_window.destroy()

            qr_window.bind("<Escape>", close_qr)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка отображения QR-кода: {e}")
    def quit_app(self):
        self.root.destroy()
