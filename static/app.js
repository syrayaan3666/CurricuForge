async function generate(){
    document.getElementById("result").innerHTML =
    `<div class="semester-card loading">AI Agents Designing Curriculum...</div>`;


    const planner = document.getElementById("planner");
    const generator = document.getElementById("generator");
    const validator = document.getElementById("validator");

    // reset states
    planner.className="agent-step";
    generator.className="agent-step";
    validator.className="agent-step";

    const payload = {
    mode: document.getElementById("mode").value,   // ⭐ NEW
    skill: document.getElementById("skill").value,
    level: document.getElementById("level").value,
    semesters: document.getElementById("semesters").value,
    weekly_hours: document.getElementById("hours").value,
    industry_focus: document.getElementById("focus").value
};


    planner.classList.add("agent-active");
    await sleep(700);

    planner.classList.remove("agent-active");
    planner.classList.add("agent-done");

    generator.classList.add("agent-active");

    const res = await fetch("/generate", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
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
}

function sleep(ms){
    return new Promise(resolve => setTimeout(resolve, ms));
}



function renderCurriculum(data){

    let html = "";

    // ===== 🧠 Persona Mode Badge =====
    if(data.learner_profile){
        html += `
        <div class="semester-card" style="
            border:1px solid #3b82f6;
            box-shadow:0 0 18px rgba(59,130,246,0.6);
            margin-bottom:15px;
        ">
            <b>🧠 Persona Mode Active</b>
        </div>
        `;
    }

    // ===== 🧠 Learner Profile Card =====
    if(data.learner_profile){

        const lp = data.learner_profile;

        html += `
        <div class="semester-card">
            <h3>🧠 Learner Profile</h3>
            <p><b>Style:</b> ${lp.learning_style || "Adaptive"}</p>
            <p><b>Pace:</b> ${lp.learning_pace || "Balanced"}</p>
            <p><b>Strengths:</b> ${(lp.strengths || []).join(", ")}</p>
            <p><b>Risk Areas:</b> ${(lp.risk_areas || []).join(", ")}</p>
        </div>
        `;
    }

    // ===== 🎓 Program Title =====
    html += `<h2>${data.program_title || ""}</h2>`;
    html += `<p>${data.summary || ""}</p>`;


    // ===== 📚 Semester Rendering =====
    if(data.semesters){

        data.semesters.forEach(sem => {

            html += `<div class="semester-card">`;
            html += `<h3>Semester ${sem.semester}</h3>`;

            if(sem.courses){

                sem.courses.forEach(course => {

                    html += `<div class="course-card">`;
                    html += `<b>${course.title}</b>`;
                    html += `<ul>`;

                    if(course.topics){
                        course.topics.forEach(t=>{
                            html += `<li>${t}</li>`;
                        });
                    }

                    html += `</ul>`;
                    html += `</div>`;
                });

            }

            html += `</div>`;
        });

    }

    document.getElementById("result").innerHTML = html;
}

