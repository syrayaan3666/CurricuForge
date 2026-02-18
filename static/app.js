// ===============================
// SMALL UTILITY
// ===============================
function sleep(ms){
    return new Promise(resolve => setTimeout(resolve, ms));
}

// ===============================
// GENERATE FUNCTION
// ===============================
async function generate(){

    const plannerTypeEl = document.getElementById("plannerType");

    if(!plannerTypeEl){
        console.error("plannerType not found in DOM");
        return;
    }

    const plannerType = plannerTypeEl.value;

    if(!plannerType){
        alert("Please select Planner Type");
        return;
    }

    // timeline elements
    const planner = document.getElementById("planner");
    const generator = document.getElementById("generator");
    const validator = document.getElementById("validator");

    const resultBox = document.getElementById("result");

    planner.className="agent-step";
    generator.className="agent-step";
    validator.className="agent-step";

    resultBox.innerHTML =
        `<div class="semester-card">AI Agents Designing Curriculum...</div>`;

    // ========================
    // SAFE GETTER FUNCTION
    // ========================
    function getValue(id){
        const el = document.getElementById(id);
        return el ? el.value : "";
    }

    // ========================
    // BUILD PAYLOAD SAFELY
    // ========================
    let payload = {
        planner_type: plannerType
    };

    if(plannerType === "semester"){
        payload.skill = getValue("skill");
        payload.level = getValue("level");
        payload.semesters = getValue("semesters");
        payload.weekly_hours = getValue("hours");
        payload.focus = getValue("focus");
    }

    if(plannerType === "personal"){
        payload.learning_pace = getValue("pace");
        payload.experience_level = getValue("experience");
        payload.goal_type = getValue("goal");
    }

    // ========================
    // AGENT ANIMATION
    // ========================
    planner.classList.add("agent-active");
    await sleep(700);

    planner.classList.remove("agent-active");
    planner.classList.add("agent-done");

    generator.classList.add("agent-active");

    try{

        const res = await fetch("/generate",{
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body:JSON.stringify(payload)
        });

        const data = await res.json();

        generator.classList.remove("agent-active");
        generator.classList.add("agent-done");

        validator.classList.add("agent-active");

        await sleep(600);

        validator.classList.remove("agent-active");
        validator.classList.add("agent-done");

        renderCurriculum(data);

    }catch(e){
        console.error(e);
        resultBox.innerHTML =
            `<div class="semester-card">Error generating curriculum</div>`;
    }
}



// ===============================
// RENDER RESULT
// ===============================
function renderCurriculum(data){

    console.log("API RESPONSE:", data); // 👈 debug

     html += `
        <div class="download-bar">
            <button class="download-btn" onclick='downloadCurriculum(${JSON.stringify(data)})'>
                ⬇ Download
            </button>
        </div>
    `;

    // handle formatter_agent output structure
    const curriculum = data.curriculum || data;

    if(!curriculum.semesters){
        document.getElementById("result").innerHTML =
        `<div class="semester-card">No curriculum data returned</div>`;
        return;
    }

    let html = `<h2>${curriculum.program_title || "Curriculum Plan"}</h2>`;
    html += `<p>${curriculum.summary || ""}</p>`;

    curriculum.semesters.forEach(sem => {

        html += `<div class="semester-card">`;
        html += `<h3>Semester ${sem.semester}</h3>`;

        sem.courses.forEach(course => {

            html += `<div class="course-card">`;
            html += `<b>${course.title}</b>`;
            html += `<ul>`;

            course.topics.forEach(t=>{
                html += `<li>${t}</li>`;
            });

            html += `</ul></div>`;
        });

        html += `</div>`;
    });

    document.getElementById("result").innerHTML = html;
}

function downloadCurriculum(data){

    const file = new Blob(
        [JSON.stringify(data, null, 2)],
        {type: "application/json"}
    );

    const a = document.createElement("a");
    a.href = URL.createObjectURL(file);
    a.download = "curriculum.json";
    a.click();
}


