from flask import Blueprint, request, jsonify, render_template
from PIL import Image
# import easyocr
import pytesseract
import base64
import cv2
import io
import numpy as np

ocr_blueprint = Blueprint('ocr', __name__)

# Tesseract 실행 경로 설정 (Windows)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@ocr_blueprint.route('/')
def ocr_page():
    return render_template('ocr.html')

@ocr_blueprint.route('/process_image', methods=['POST'])
def process_image():
    try:
        # 클라이언트로부터 Base64 이미지 데이터 수신
        data = request.json
        image_data = base64.b64decode(data['image'])
        selected_languages = data.get('languages', ['en'])  # 기본값: 영어

        lang_code = '+'.join(selected_languages)

        # 이미지를 PIL 형식으로 변환 후 흑백 변환
        image = Image.open(io.BytesIO(image_data))
        ori_img = image

        # 이미지를 흑백으로 변환
        image = image.convert("L")

        # Tesseract OCR 실행
        # tesseract_config = f'--psm 6 -l {lang_code}'
        tesseract_config = f'--psm 3 -l {lang_code}'
        recognized_text = pytesseract.image_to_string(image, config=tesseract_config)

        # Tesseract에서 바운딩 박스 가져오기
        boxes = pytesseract.image_to_boxes(image, config=tesseract_config)

        # 바운딩 박스를 OpenCV를 사용해 이미지에 그리기
        image_np = np.array(ori_img)  # PIL 이미지를 NumPy 배열로 변환
        h, w, _ = image_np.shape
        for box in boxes.splitlines():
            b = box.split()
            x1, y1, x2, y2 = map(int, (b[1], b[2], b[3], b[4]))
            y1, y2 = h - y1, h - y2  # Tesseract 좌표계 변환
            cv2.rectangle(image_np, (x1, y2), (x2, y1), (0, 255, 0), 1)

        image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
        # 바운딩 박스가 그려진 이미지를 Base64로 변환
        _, buffer = cv2.imencode('.png', image_np)
        image_with_boxes = base64.b64encode(buffer).decode('utf-8')

        return jsonify({
            'text': recognized_text,
            'image_with_boxes': image_with_boxes
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500