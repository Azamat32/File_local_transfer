from pyzbar.pyzbar import decode
from PIL import Image
import os
import base64
# from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
# from cryptography.hazmat.backends import default_backend

def decode_qr_from_directory(key, directory):

    fragments = {}

    if not os.path.exists(directory):
        print(f"Directory '{directory}' does not exist.")
        return None

    # iv = b"initialvector123"  
    # cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    # decryptor = cipher.decryptor()

    for filename in sorted(os.listdir(directory)):
        file_path = os.path.join(directory, filename)

        try:
            img = Image.open(file_path)
            decoded_objects = decode(img)

            for obj in decoded_objects:
                metadata = obj.data.decode()
                index, total, chunk = metadata.split("|")
                fragments[int(index)] = base64.b64decode(chunk)


                # metadata = obj.data.decode()
                # index, total, chunk = metadata.split("|")

                # encrypted_chunk = base64.b64decode(chunk)

                # decrypted_chunk = decryptor.update(encrypted_chunk)

                # padding_length = decrypted_chunk[-1]
                # decrypted_chunk = decrypted_chunk[:-padding_length]


        except Exception as e:
            print(f"Ошибка при расшифровке {filename}: {e}")

    if len(fragments) == 0:
        print("QR код не был расшифрован.")
        return None

    total_chunks = max(fragments.keys()) + 1
    if len(fragments) == total_chunks:
        print("Все фрагменты успешно расшифрованы.")
        return [fragments[i] for i in sorted(fragments.keys())]
    else:
        print(f"Было утеряно несколько фрагментов: {total_chunks - len(fragments)}")
        return None

