document.addEventListener("DOMContentLoaded", function () {
    const imageArea = document.getElementById("image-area");
    const processBtn = document.getElementById("process-btn");
    const resultArea = document.getElementById("recognized-text");
    const resultImage = document.getElementById("result-image");

    let imageBase64 = "";

    // 이미지 붙여넣기 처리
    imageArea.addEventListener("paste", function (e) {
        const items = (e.clipboardData || e.originalEvent.clipboardData).items;
        for (const item of items) {
            if (item.type.indexOf("image") === 0) {
                const file = item.getAsFile();
                const reader = new FileReader();

                reader.onload = function (event) {
                    imageArea.style.backgroundImage = `url(${event.target.result})`;
                    imageBase64 = event.target.result.split(",")[1]; // Base64 데이터

                    // "이미지를 여기에 붙여넣으세요." 텍스트 숨기기
                    const placeholderText = imageArea.querySelector("p");
                    if (placeholderText) {
                        placeholderText.style.display = "none";
                    }
                };

                reader.readAsDataURL(file);
            }
        }
    });

    // 서버로 이미지 전송
    processBtn.addEventListener("click", function () {
        if (!imageBase64) {
            alert("이미지를 붙여넣으세요!");
            return;
        }

        fetch("/ocr/process_image", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ image: imageBase64 }),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.error) {
                    alert("오류: " + data.error);
                    return;
                }

                // 인식된 텍스트 표시
                resultArea.innerHTML = data.text.join("<br>");

                // 바운딩 박스가 표시된 이미지 표시
                resultImage.src = `data:image/png;base64,${data.image_with_boxes}`;
            })
            .catch((error) => console.error("Error:", error));
    });
});
