from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import cv2
import face_recognition
import threading
from time import sleep
# Tanınacak kişilerin yüzlerini yükleyin ve kodlayın
known_image1 = face_recognition.load_image_file("person1.jpg")
known_face_encoding1 = face_recognition.face_encodings(known_image1)[0]

passwords = {}
with open('passwords.txt') as f:
    for line in f:
        user, pwd = line.strip().split(':')
        passwords[user] = pwd

person1_username = "caktas20"
person1_password = passwords[person1_username]

person2_username = "maydin19"
person2_password = passwords[person2_username]
known_image2 = face_recognition.load_image_file("person2.jpg")
known_face_encoding2 = face_recognition.face_encodings(known_image2)[0]

known_face_encodings = [known_face_encoding1, known_face_encoding2]
known_face_names = ["Kilit acildi - Kisi 1", "Kilit acildi - Kisi 2"]

video_capture = cv2.VideoCapture(0)

# Yüz algılama ve tanıma sonuçlarını saklamak için değişkenler
face_locations = []
face_encodings = []
face_names = []

process_this_frame = True
lock = threading.Lock()
browser_opened = False  # Tarayıcının açılıp açılmadığını kontrol eden bayrak
last_seen_name = None  # Son tanınan kişinin adını saklayan değişken

video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

def process_frame():
    global face_locations, face_encodings, face_names, process_this_frame, browser_opened, last_seen_name

    while True:
        ret, frame = video_capture.read()
        if not ret:
            continue

        browser_opened = False  # Her frame işlendiğinde bayrağı sıfırla

        if process_this_frame:
            # Görüntüyü ölçeklendirin (işlem süresini azaltmak için)
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = small_frame[:, :, ::-1]

            # Küçültülmüş görüntüdeki tüm yüzleri bulun ve yüz kodlamalarını hesaplayın
            face_locations_temp = face_recognition.face_locations(rgb_small_frame)
            face_encodings_temp = face_recognition.face_encodings(rgb_small_frame, face_locations_temp)

            face_names_temp = []
            for face_encoding in face_encodings_temp:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Tanimlanmadi"
                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_face_names[first_match_index]
                    if name != last_seen_name:  # Eğer tanınan kişi son görülen kişi değilse
                        # Chrome tarayıcısını başlat
                        driver = webdriver.Chrome()
                        driver.get('https://pusula.pau.edu.tr/')

                        # Kullanıcı adı giriş kutusunu bul ve "mayd" yazısını gönder
                        try:
                            
                          if name == "Kilit acildi - Kisi 1":
                            driver.find_element(By.CSS_SELECTOR, '[id="lvPusula_txtKullanici"]').send_keys(person1_username)
                            driver.find_element(By.CSS_SELECTOR, '[id="lvPusula_txtSifre"]').send_keys(person1_password)
                            driver.find_element(By.CSS_SELECTOR, '[id="lvPusula_btnGiris"]').click()

                          elif name == "Kilit acildi - Kisi 2":
                            driver.find_element(By.CSS_SELECTOR, '[id="lvPusula_txtKullanici"]').send_keys(person2_username)
                            driver.find_element(By.CSS_SELECTOR, '[id="lvPusula_txtSifre"]').send_keys(person2_password)
                            driver.find_element(By.CSS_SELECTOR, '[id="lvPusula_btnGiris"]').click()
                            sleep(15)
                        except Exception as e:
                            print(f"Error: {e}")
                        finally:
                            last_seen_name = name  # Son tanınan kişiyi güncelle

                face_names_temp.append(name)

            # Kilit kullanımı ile paylaşılacak değişkenleri güncelleyin
            with lock:
                face_locations = [(top*4, right*4, bottom*4, left*4) for (top, right, bottom, left) in face_locations_temp]
                face_encodings = face_encodings_temp
                face_names = face_names_temp

        process_this_frame = not process_this_frame

# İş parçacığını başlatın
thread = threading.Thread(target=process_frame)
thread.daemon = True
thread.start()

while True:
    ret, frame = video_capture.read()
    if not ret:
        break

    # Kilit kullanımı ile yüz bilgilerini alın
    with lock:
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Yüz çevresine bir dikdörtgen çizin
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Sonuçları gösterin
    cv2.imshow('Video', frame)

    # 'q' tuşuna basıldığında döngüyü kırın
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Her şeyi serbest bırakın
video_capture.release()
cv2.destroyAllWindows()
