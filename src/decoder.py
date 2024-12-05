from pyzbar.pyzbar import decode
from PIL import Image
import os
import base64
import cv2
import numpy as np
import logging

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





def decode_qr_from_camera():
    """
    Captures frames from the camera, decodes QR codes in real-time,
    and returns the decoded data as chunks.

    Returns:
        list: List of decoded chunks from QR codes.
    """
    print("Opening camera. Press 'q' to quit.")
    decoded_chunks = []
    
    # Open the camera
    cap = cv2.VideoCapture(0)  # 0 is the default camera
    if not cap.isOpened():
        print("Failed to open camera.")
        return None

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame. Exiting.")
            break

        # Decode QR codes in the frame
        decoded_objects = decode(frame)
        for obj in decoded_objects:
            try:
                # Extract and decode data from the QR code
                qr_data = obj.data.decode('utf-8')
                print(f"QR Code detected: {qr_data}")

                # Handle chunk format: base64-encoded encrypted data
                decoded_chunk = base64.b64decode(qr_data)
                print(decoded_chunk)
                decoded_chunks.append(decoded_chunk)

                # After processing one QR code, stop scanning and move to the next frame
                break  # Stop processing the current frame after decoding a QR code

            except Exception as e:
                print(f"Error decoding QR: {e}")

        # Display the frame with QR code bounding boxes
        for obj in decoded_objects:
            points = obj.polygon
            if len(points) > 4:  # If QR code is distorted
                hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                points = hull

            # Draw bounding box
            for i in range(len(points)):
                pt1 = (int(points[i].x), int(points[i].y))
                pt2 = (int(points[(i + 1) % len(points)].x), int(points[(i + 1) % len(points)].y))
                cv2.line(frame, pt1, pt2, color=(0, 255, 0), thickness=2)

        # Display the video feed with QR code overlays
        cv2.imshow("QR Code Scanner", frame)

        # Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and close the window
    cap.release()
    cv2.destroyAllWindows()

    if decoded_chunks:
        print("Decoding complete.")
        return decoded_chunks
    else:
        print("No QR codes decoded.")
        return None
