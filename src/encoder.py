import qrcode
import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend



def split_file_to_chunks(file_path,key, max_chunk_size=1024):

    # if len(key) not in (16, 24, 32):
    #     raise ValueError("Ошибка при валидации ключа.")
    # iv = b"initialvector123"  
    # cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    # encryptor = cipher.encryptor()

    chunks = []
    with open(file_path, "rb") as f:
        while chunk := f.read(max_chunk_size):
            chunks.append(chunk)
            # padding_length = 16 - (len(chunk) % 16)
            # chunk += bytes([padding_length]) * padding_length
            # # Шифруем чанки
            # encrypted_chunk = encryptor.update(chunk)
    # final_chunk = encryptor.finalize()
    # if final_chunk:
    #     chunks.append(final_chunk)

    print(f"Файл был разделен на  {len(chunks)} чанков.")
    return chunks


def encode_chunks_to_qr(chunks, output_dir="qr_codes"):

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    qr_code_paths = []

    total_chunks = len(chunks)
    for index, chunk in enumerate(chunks):
        
        data = f"{index}|{total_chunks}|{base64.b64encode(chunk).decode()}"
        
        # Генерация QR кода
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L)
        qr.add_data(data)
        qr.make(fit=True)
        
        # Созраняем QR код
        qr_code_path = os.path.join(output_dir, f"chunk_{index + 1}.png")
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(qr_code_path)
        qr_code_paths.append(qr_code_path)
    
    print(f"QR codes saved to {output_dir}")
    return qr_code_paths
