const generateBtn = document.getElementById("generateBtn");
const copyBtn = document.getElementById("copyBtn");
const result = document.getElementById("result");
const loader = document.getElementById("loader");

generateBtn.addEventListener("click", async () => {
    const situation = document.getElementById("situation").value.trim();
    const category = document.getElementById("category").value;
    const tone = document.getElementById("tone").value;
    const language = document.getElementById("language").value;
    const length = document.getElementById("length").value;

    if (situation === "") {
        result.textContent = "Please Write your situation first...";
        return;
    }

    generateBtn.disabled = true;
    generateBtn.textContent = "Generating...";
    
    result.innerHTML = `
<h3>🤖 AI is thinking...</h3>
<p>Please wait while your excuse is being generated.</p>
`;
    loader.style.display = "block";

    try {
        const response = await fetch("/generate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                situation: situation,
                category: category,
                tone: tone,
                language: language,
                length: length
            })
        });

        const data = await response.json();

        if (!response.ok) {
            result.textContent = data.error || "Something Problem";
            return;
        }

       typeText(data.excuse);

    } catch (error) {
        console.error(error);
        result.textContent = "Unable to connect server";
    } finally {
        loader.style.display = "none";
        generateBtn.disabled = false;
        generateBtn.textContent = "Generate Excuse";
    }
});

copyBtn.addEventListener("click", async () => {
    const excuse = result.textContent.trim();

    if (
        excuse === "" ||
        excuse === "Generated excuse will show here." ||
        excuse === "AI is generating execuse"
    ) {
        alert("There is no execuse to copy...");
        return;
    }

    try {
        await navigator.clipboard.writeText(excuse);

        copyBtn.textContent = "Copied!";

        setTimeout(() => {
            copyBtn.textContent = "Copy Excuse";
        }, 1500);

    } catch (error) {
        alert("Unable to copy execuse..");
    }
});
regenerateBtn.addEventListener("click", () => {
    generateBtn.click();
});
function typeText(text) {
    result.textContent = "";

    let index = 0;

    const typing = setInterval(() => {
        result.textContent += text.charAt(index);
        index++;

        if (index >= text.length) {
            clearInterval(typing);
        }
    }, 20);
}