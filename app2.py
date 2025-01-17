from flask import Blueprint, request, jsonify, render_template
from PIL import Image
import easyocr
import base64
import cv2
import io
import numpy as np

ocr_blueprint = Blueprint('ocr', __name__)

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

        # 이미지를 PIL 형식으로 변환 후 흑백 변환
        image = Image.open(io.BytesIO(image_data))
        ori_img = image

        # 이미지를 흑백으로 변환
        image = image.convert("L")

        # PIL 이미지를 NumPy 배열로 변환
        image_np = np.array(image)
        ori_img_np = np.array(ori_img)
        reader = easyocr.Reader(selected_languages, gpu=False)

        # EasyOCR로 텍스트 인식
        results = reader.readtext(image_np)

        # Bounding Box 기반 텍스트 병합
        merged_text = []
        current_line = []
        current_y = None

        # 바운딩 박스를 OpenCV를 사용해 이미지에 그리기
        for (bbox, text, prob) in results:
            # y축 중심 좌표 계산
            y_center = (bbox[0][1] + bbox[2][1]) / 2  # 좌상단과 우하단 y좌표의 평균
            if current_y is None or abs(y_center - current_y) < 20:  # 같은 줄로 간주
                current_line.append(text)
                current_y = y_center
            else:  # 새로운 줄
                merged_text.append(" ".join(current_line))
                current_line = [text]
                current_y = y_center

            # 바운딩 박스 좌표 가져오기
            (top_left, top_right, bottom_right, bottom_left) = bbox
            top_left = tuple(map(int, top_left))
            bottom_right = tuple(map(int, bottom_right))

            # 박스 그리기
            cv2.rectangle(ori_img_np, top_left, bottom_right, (0, 255, 0), 2)

        # 마지막 줄 추가
        if current_line:
            merged_text.append(" ".join(current_line))

        ori_img_np = cv2.cvtColor(ori_img_np, cv2.COLOR_BGR2RGB)

        # 바운딩 박스가 그려진 이미지를 Base64로 변환
        _, buffer = cv2.imencode('.png', ori_img_np)
        image_with_boxes = base64.b64encode(buffer).decode('utf-8')

        return jsonify({
            'text': merged_text,
            'image_with_boxes': image_with_boxes
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500