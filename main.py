import os
import threading
from src.encoder import split_file_to_chunks, encode_chunks_to_qr
from src.decoder import decode_qr_from_directory,decode_qr_from_camera
from src.file_assembler import assemble_file
from src.encryption import generate_key
from src.gui import FileTransferGUI,ModeSelectionGUI
import logging
import time
import tkinter as tk

SEND_DIR = "send"
RECEIVE_DIR = "receive"

QR_CODES_DIR = "qr_codes"


def cleanup_qr_codes(directory):
    # Функция для удаление всех QR после успешной отправки
    if not os.path.exists(directory):
        print(f"Директория {directory} не существует.")
        return

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            os.remove(file_path)
            print(f"Был удален QR: {file_path}")
        except Exception as e:
            print(f"Ошибка при удаления QR {file_path}: {e}")




def run_gui():
    root = tk.Tk()
    app = FileTransferGUI(root, SEND_DIR,None)
    logging.basicConfig(
        filename="file_transfer_log.txt",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    def on_new_file_detected_with_app(file_path):
        log_message = lambda msg: (logging.info(msg), print(msg))
        log_message(f"Распознан новый файл: {file_path}")

        app.update_progress(10) 

        try:
            # Шаг 1: Генерируем ключ
            key = generate_key(32)
            log_message(f"КЛюч был создан для: {file_path}")

            # Шаг 2: Файл был разделен
            chunks = split_file_to_chunks(file_path,key)
            log_message(f"Файл был разделен: {file_path}")

            app.update_progress(25)

            # Шаг 3: Преображение чанков в QR
            qr_codes = encode_chunks_to_qr(chunks)
            log_message(f"Преображение чанков в QR: {file_path}")

            app.update_progress(50)
            for i, qr_code in enumerate(qr_codes):
                print(f"Показ QR-кода {i + 1}/{len(qr_codes)}")
                app.display_qr_code(qr_code)  # Отображение QR-кода через GUI
                
                time.sleep(5)  # Интервал между показами

            # Шаг 4: Расшифрока QR кодов
            decoded_chunks = decode_qr_from_directory(key,directory=QR_CODES_DIR,)
            if not decoded_chunks:
                log_message(f"Ошибка при расшифроке QR: {file_path}")
                app.update_status(f"Ошибка при расшифроке QR: {file_path}")
                return
            log_message(f"QR код был успешно расшифрован: {file_path}")
            app.update_progress(75)

            # Шаг 5: Обратно собираем файл
            reassembled_file_path = os.path.join(RECEIVE_DIR, os.path.basename(file_path))
            assemble_file(decoded_chunks, reassembled_file_path)
            log_message(f"Файл был создан в : {reassembled_file_path}")
            app.update_progress(100)
            app.update_status("Файл успешно отправлен.")

            # Шаг 6: Удаление всех QR кодов
            cleanup_qr_codes(QR_CODES_DIR)
            log_message(f"Все QR коды были успешны в: {file_path}")

            # Шаг 7: Удаляем файл с папки SEND_DIR
            send_file_path = os.path.join(SEND_DIR, os.path.basename(file_path))
            os.remove(send_file_path)
            log_message(f"Оригинальный файл был удален: {send_file_path}")

        except Exception as e:
            log_message(f"Ошибка при обработке файла {file_path}: {e}")
            app.update_status(f"Ошибка при обработке файла: {e}")


    # Assign the wrapped function as the callback
    app.callback = on_new_file_detected_with_app

    root.mainloop()

def run_client():
    print("Клиент: Открытие камеры для считывания QR-кодов...")
    decoded_chunks = decode_qr_from_camera()

    if decoded_chunks:
        reassembled_file_path = os.path.join(RECEIVE_DIR, "reassembled_file.bin")
        assemble_file(decoded_chunks, reassembled_file_path)
        print(f"Файл собран: {reassembled_file_path}")
    else:
        print("Не удалось расшифровать QR-коды.")

def main():
    if not os.path.exists(SEND_DIR):
        os.makedirs(SEND_DIR)
    if not os.path.exists(RECEIVE_DIR):
        os.makedirs(RECEIVE_DIR)
    
    root = tk.Tk()
    mode_selection_app = ModeSelectionGUI(root)
    root.mainloop()

    if mode_selection_app.selected_mode == "server":
        run_gui()
    elif mode_selection_app.selected_mode == "client":
        run_client()
    else:
        print("Режим не выбран. Завершение работы.")
    # gui_thread = threading.Thread(target=run_gui)
    # gui_thread.start()

    # gui_thread.join()



if __name__ == "__main__":
    main()
