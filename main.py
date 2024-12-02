import os
import threading
from src.encoder import split_file_to_chunks, encode_chunks_to_qr
from src.decoder import decode_qr_from_directory, decode_qr_from_camera
from src.file_assembler import assemble_file
from src.encryption import generate_key
from src.gui import FileTransferGUI, ModeSelectionGUI
import logging
import tkinter as tk
import time

SEND_DIR = "send"
RECEIVE_DIR = "receive"
QR_CODES_DIR = "qr_codes"


def cleanup_qr_codes(directory):
    if not os.path.exists(directory):
        print(f"Директория {directory} не существует.")
        return

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            os.remove(file_path)
            print(f"Удалён QR: {file_path}")
        except Exception as e:
            print(f"Ошибка при удалении QR {file_path}: {e}")


def run_server_gui(root):
    app = FileTransferGUI(root, SEND_DIR, None)

    def on_new_file_detected_with_app(file_path):
        log_message = lambda msg: (logging.info(msg), print(msg))
        log_message(f"Распознан новый файл: {file_path}")

        try:
            key = generate_key(32)
            log_message(f"Ключ создан: {file_path}")

            chunks = split_file_to_chunks(file_path, key)
            log_message(f"Файл разделён на чанки: {file_path}")

            qr_codes = encode_chunks_to_qr(chunks)
            log_message(f"Чанки преобразованы в QR-коды: {file_path}")

            for i, qr_code in enumerate(qr_codes):
                print(f"Показ QR-кода {i + 1}/{len(qr_codes)}")
                app.display_qr_code(qr_code)  # Отображение QR-кода через GUI
                time.sleep(5)  # Интервал между показами

            decoded_chunks = decode_qr_from_directory(key, directory=QR_CODES_DIR)
            if not decoded_chunks:
                log_message(f"Ошибка при расшифровке QR-кодов: {file_path}")
                return

            reassembled_file_path = os.path.join(RECEIVE_DIR, os.path.basename(file_path))
            assemble_file(decoded_chunks, reassembled_file_path)
            log_message(f"Файл собран в: {reassembled_file_path}")

            cleanup_qr_codes(QR_CODES_DIR)
            log_message(f"QR-коды удалены: {file_path}")

        except Exception as e:
            log_message(f"Ошибка при обработке файла {file_path}: {e}")

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
        run_server_gui(root)
    elif mode_selection_app.selected_mode == "client":
        run_client()
    else:
        print("Режим не выбран. Завершение работы.")


if __name__ == "__main__":
    main()
