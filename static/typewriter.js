document.addEventListener("DOMContentLoaded", function () {
    const typewriter = document.getElementById("typewriter");
    const cursor = document.getElementById("cursor");

    if (!typewriter || !cursor) return;

    let lines = [];
    try {
        const dataLines = typewriter.dataset.lines;
        if (dataLines) {
            lines = JSON.parse(dataLines);
        }
    } catch (e) {
        console.error("解析数据出错:", e);
        const fallback = typewriter.dataset.lines;
        if (fallback) {
            lines = [fallback];
        }
    }

    if (lines.length === 0) return;

    let lineIndex = 0;
    let charIndex = 0;
    let displayText = "";

    function typeLine() {
        if (lineIndex >= lines.length) {
            cursor.style.display = 'none'; // 隐藏光标而不是移除
            return;
        }

        const line = lines[lineIndex];

        if (charIndex < line.length) {
            // 添加当前字符
            displayText += line.charAt(charIndex);
            typewriter.innerHTML = displayText.replace(/\n/g, '<br>');
            charIndex++;
            setTimeout(typeLine, 50); // 字符间隔
        } else {
            // 当前行完成，添加换行并进入下一行
            displayText += "\n";
            typewriter.innerHTML = displayText.replace(/\n/g, '<br>');
            lineIndex++;
            charIndex = 0;
            setTimeout(typeLine, 500); // 行间隔
        }
    }

    // 开始打字动画
    typeLine();
});