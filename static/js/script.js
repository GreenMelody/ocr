document.addEventListener("DOMContentLoaded", function () {
    const imageTab = document.getElementById("image-tab");
    const processedImageTab = document.getElementById("processed-image-tab");
    const imageArea = document.getElementById("image-area");
    const processedImageArea = document.getElementById("processed-image-area");
    const processBtn = document.getElementById("process-btn");
    const resultArea = document.getElementById("recognized-text");
    const loadingOverlay = document.getElementById("loading-overlay");

    let imageBase64 = "";

    // 이미지 붙여넣기 처리
    imageArea.addEventListener("paste", function (e) {
        const items = (e.clipboardData || e.originalEvent.clipboardData).items;
        for (const item of items) {
            if (item.type.indexOf("image") === 0) {
                const file = item.getAsFile();
                const reader = new FileReader();

                reader.onload = function (event) {
                    // 배경 이미지 설정
                    imageArea.style.backgroundImage = `url(${event.target.result})`;
                    imageArea.style.backgroundSize = "contain";
                    imageArea.style.backgroundRepeat = "no-repeat";
                    imageArea.style.backgroundPosition = "center";

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

        // 선택된 언어 가져오기
        const selectedLanguages = Array.from(
            document.querySelectorAll("#language-selection input:checked")
        ).map((checkbox) => checkbox.value);

        if (selectedLanguages.length === 0) {
            alert("최소한 하나의 언어를 선택하세요.");
            return;
        }

        // 로딩 화면 표시
        loadingOverlay.style.display = "block";

        fetch("/ocr/process_image", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                image: imageBase64,
                languages: selectedLanguages,
            }),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.error) {
                    alert("오류: " + data.error);
                    return;
                }

                // 인식된 텍스트 표시
                if (Array.isArray(data.text)) {
                    // 텍스트가 배열인 경우
                    resultArea.innerHTML = data.text.join("<br>");
                } else {
                    // 텍스트가 문자열인 경우
                    resultArea.textContent = data.text;
                }

                // 처리된 이미지를 처리된 이미지 영역에 표시
                processedImageArea.style.backgroundImage = `url(data:image/png;base64,${data.image_with_boxes})`;
                processedImageArea.style.backgroundSize = "contain";
                processedImageArea.style.backgroundRepeat = "no-repeat";
                processedImageArea.style.backgroundPosition = "center";

                // 탭 전환: 처리된 이미지 탭 활성화
                processedImageTab.click();
            })
            .catch((error) => console.error("Error:", error))
            .finally(() => {
                // 로딩 화면 숨기기
                loadingOverlay.style.display = "none";
            });
    });
});
