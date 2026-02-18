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
        payload.include_capstone = document.getElementById("includeCapstone").checked;
    }

    if(plannerType === "personal"){
        payload.study_domain = getValue("studyDomain");
        payload.career_path = getValue("careerPath");
        payload.experience = getValue("experience");
        payload.pace = getValue("pace");
        payload.weekly_hours = getValue("weeklyHours");
        payload.duration = getValue("duration");
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
        // Show refinement UI after rendering
        try{ showRefineBox(); }catch(e){/* non-fatal */}

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

    let html = "";    
    // Store data globally FIRST for download buttons
    window.currentCurriculumData = data;
    console.log("Stored curriculum data:", data);
    // =====================================================
    // � PERSONAL ROADMAP MODE (NEW)
    // =====================================================
    if(data.roadmap){
        renderPersonalRoadmap(data);
        return;
    }

    // =====================================================
    // 🎓 SEMESTER PLANNER MODE
    // =====================================================
    if(data.semesters){

        html += `<h2>${data.program_title || "Curriculum Plan"}</h2>`;
        html += `<p>${data.summary || ""}</p>`;

        const resultDiv = document.getElementById("result");
        resultDiv.innerHTML = "";

        // Add download bar
        resultDiv.appendChild(createDownloadBar(data));

        // Create HTML content
        const contentDiv = document.createElement("div");

        data.semesters.forEach((sem, idx) => {

            html += `<div class="semester-card">`;
            const isCapstone = (idx === data.semesters.length - 1) && data.include_capstone;
            html += `<h3>Semester ${sem.semester}${isCapstone ? ' 🎓 CAPSTONE' : ''}</h3>`;

            sem.courses.forEach(course => {

                html += `<div class="course-card">`;
                html += `<b>${course.title}</b>`;
                
                // Difficulty badge
                if(course.difficulty){
                    const diffColor = course.difficulty === 'Beginner' ? '#4CAF50' : course.difficulty === 'Intermediate' ? '#FF9800' : '#f44336';
                    html += `<span style="background:${diffColor}; color:white; padding:2px 8px; border-radius:4px; font-size:12px; margin-left:8px;">${course.difficulty}</span>`;
                }
                
                // Skills
                if(course.skills && course.skills.length > 0){
                    html += `<p style="margin:8px 0 4px 0;"><strong>🎯 Skills:</strong></p>`;
                    html += `<ul style="margin:0 0 8px 0;">`;
                    course.skills.forEach(skill => {
                        html += `<li>${skill}</li>`;
                    });
                    html += `</ul>`;
                }
                
                // Topics
                if(course.topics && course.topics.length > 0){
                    html += `<p style="margin:8px 0 4px 0;"><strong>📚 Topics:</strong></p>`;
                    html += `<ul style="margin:0 0 8px 0;">`;
                    course.topics.forEach(t=>{
                        html += `<li>${t}</li>`;
                    });
                    html += `</ul>`;
                }
                
                // Outcome Project
                if(course.outcome_project){
                    html += `<p style="margin:8px 0 0 0;"><strong>💡 Deliverable:</strong> ${course.outcome_project}</p>`;
                }
                
                html += `</div>`;
            });

            html += `</div>`;
        });

        contentDiv.innerHTML = html;
        resultDiv.appendChild(contentDiv);
    }

    // =====================================================
    // ❌ UNKNOWN FORMAT (SAFETY FALLBACK)
    // =====================================================
    else{
        html = `<div class="semester-card">⚠ Unknown data format received from agents.</div>`;
        console.error("Unknown response format:", data);
        document.getElementById("result").innerHTML = html;
    }
}


// ===============================
// RENDER PERSONAL ROADMAP
// ===============================
function renderPersonalRoadmap(data){

    let html = "";

    html += `<h2>${data.program_title || "Learning Path Roadmap"}</h2>`;
    html += `<p>${data.summary || ""}</p>`;

    // Program metadata
    if(data.total_weeks || data.weekly_hours){
        html += `<div class="program-meta">`;
        if(data.total_weeks) html += `<span><b>Duration:</b> ${data.total_weeks} weeks</span>`;
        if(data.weekly_hours) html += `<span><b>Weekly Commitment:</b> ${data.weekly_hours} hours</span>`;
        html += `</div>`;
    }

    const resultDiv = document.getElementById("result");
    resultDiv.innerHTML = "";

    // Add download bar
    resultDiv.appendChild(createDownloadBar(data));

    // Create HTML content
    const contentDiv = document.createElement("div");

    data.roadmap.forEach(phase => {

        html += `<div class="phase-card">`;
        html += `<h3>${phase.phase}</h3>`;

        // Phase timeline
        if(phase.duration_weeks || phase.weeks){
            html += `<div class="phase-timeline">`;
            if(phase.weeks) html += `<span>${phase.weeks}</span>`;
            if(phase.duration_weeks) html += `<span>(${phase.duration_weeks} weeks)</span>`;
            html += `</div>`;
        }

        phase.milestones.forEach(milestone => {

            html += `<div class="milestone-card">`;
            html += `<h4>${milestone.title}</h4>`;

            // Milestone timeline and hours
            if(milestone.timeline_weeks || milestone.estimated_total_hours){
                html += `<div class="milestone-meta">`;
                if(milestone.timeline_weeks) html += `<span>📅 ${milestone.timeline_weeks}</span>`;
                if(milestone.estimated_total_hours) html += `<span>⏱️ ${milestone.estimated_total_hours} hours</span>`;
                html += `</div>`;
            }

            // Skills
            if(milestone.skills && milestone.skills.length > 0){
                html += `<div class="skills-section">`;
                html += `<b>🎯 Skills:</b>`;
                html += `<ul>`;
                milestone.skills.forEach(skill => {
                    html += `<li>${skill}</li>`;
                });
                html += `</ul>`;
                html += `</div>`;
            }

            // Certification (optional)
            if(milestone.certification && typeof milestone.certification === 'object' && Object.keys(milestone.certification).length > 0){
                html += `<div class="cert-section">`;
                html += `<b>🏅 Certification:</b>`;
                html += `<ul>`;
                Object.keys(milestone.certification).forEach(k => {
                    const v = milestone.certification[k];
                    html += `<li><b>${k}:</b> ${typeof v === 'string' ? v : JSON.stringify(v)}</li>`;
                });
                html += `</ul>`;
                html += `</div>`;
            }

            // Topics
            if(milestone.topics && milestone.topics.length > 0){
                html += `<div class="topics-section">`;
                html += `<b>📚 Topics:</b>`;
                html += `<ul>`;
                milestone.topics.forEach(topic => {
                    // Handle both string topics (old format) and object topics (new format)
                    if(typeof topic === 'string'){
                        html += `<li>${topic}</li>`;
                    } else {
                        html += `<li>`;
                        html += `${topic.name}`;
                        if(topic.estimated_hours) html += ` <span class="topic-hours">(${topic.estimated_hours}h)</span>`;
                        if(topic.weeks) html += ` <span class="topic-weeks">${topic.weeks}</span>`;
                        html += `</li>`;
                    }
                });
                html += `</ul>`;
                html += `</div>`;
            }

            html += `</div>`;
        });

        html += `</div>`;
    });

    contentDiv.innerHTML = html;
    resultDiv.appendChild(contentDiv);
}


function downloadJSON(data){
    const file = new Blob(
        [JSON.stringify(data, null, 2)],
        {type: "application/json"}
    );
    const a = document.createElement("a");
    a.href = URL.createObjectURL(file);
    a.download = "curriculum.json";
    a.click();
}

function downloadPDF(data){
    // Use global data if not passed
    if(!data) {
        data = window.currentCurriculumData;
    }
    
    console.log("downloadPDF called with data:", data);
    
    if(!data) {
        alert("No curriculum data available. Please generate a curriculum first.");
        return;
    }
    
    // Check if jsPDF is available
    if(!window.jspdf || !window.jspdf.jsPDF){
        alert("PDF library not loaded. Please refresh the page and try again.");
        return;
    }

    try {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        console.log("PDF generation started");
        let yPosition = 10;
        const pageHeight = doc.internal.pageSize.getHeight();
        const margin = 10;
        const maxWidth = doc.internal.pageSize.getWidth() - 2 * margin;

    // Title
    doc.setFontSize(16);
    doc.text(data.program_title || "Curriculum", margin, yPosition);
    yPosition += 10;

    // Summary
    if(data.summary){
        doc.setFontSize(10);
        doc.setTextColor(100);
        const summaryLines = doc.splitTextToSize(data.summary, maxWidth);
        doc.text(summaryLines, margin, yPosition);
        yPosition += summaryLines.length * 5 + 5;
    }

    // Metadata
    if(data.total_weeks || data.weekly_hours){
        doc.setFontSize(9);
        doc.setTextColor(0);
        if(data.total_weeks) doc.text(`Duration: ${data.total_weeks} weeks`, margin, yPosition);
        yPosition += 5;
        if(data.weekly_hours) doc.text(`Weekly Hours: ${data.weekly_hours}`, margin, yPosition);
        yPosition += 8;
    }

    // Roadmap or Semesters
    if(data.roadmap){
        data.roadmap.forEach(phase => {
            if(yPosition > pageHeight - 20) {
                doc.addPage();
                yPosition = 10;
            }
            doc.setFontSize(12);
            doc.setTextColor(0);
            doc.text(phase.phase, margin, yPosition);
            yPosition += 7;

            phase.milestones.forEach(milestone => {
                if(yPosition > pageHeight - 20) {
                    doc.addPage();
                    yPosition = 10;
                }
                doc.setFontSize(11);
                doc.setTextColor(50);
                doc.text(`• ${milestone.title}`, margin + 2, yPosition);
                yPosition += 5;

                if(milestone.skills){
                    doc.setFontSize(9);
                    doc.setTextColor(100);
                    doc.text("Skills: " + milestone.skills.join(", "), margin + 4, yPosition);
                    yPosition += 4;
                }

                yPosition += 2;
            });
            yPosition += 3;
        });
    }
    else if(data.semesters){
        data.semesters.forEach(sem => {
            if(yPosition > pageHeight - 20) {
                doc.addPage();
                yPosition = 10;
            }
            doc.setFontSize(12);
            doc.setTextColor(0);
            doc.text(`Semester ${sem.semester}`, margin, yPosition);
            yPosition += 7;

            sem.courses.forEach(course => {
                if(yPosition > pageHeight - 20) {
                    doc.addPage();
                    yPosition = 10;
                }
                doc.setFontSize(10);
                doc.text(`• ${course.title}`, margin + 2, yPosition);
                yPosition += 5;
            });
            yPosition += 3;
        });
    }

        doc.save("curriculum.pdf");
        console.log("PDF downloaded successfully");
    } catch(error) {
        console.error("PDF generation error:", error);
        alert("Error generating PDF: " + error.message);
    }
}

function createDownloadBar(data){
    console.log("createDownloadBar called with:", data);
    
    const bar = document.createElement("div");
    bar.className = "download-bar";
    
    const jsonBtn = document.createElement("button");
    jsonBtn.className = "download-btn download-json";
    jsonBtn.textContent = "📥 JSON";
    jsonBtn.onclick = () => downloadJSON(window.currentCurriculumData);
    
    const pdfBtn = document.createElement("button");
    pdfBtn.className = "download-btn download-pdf";
    pdfBtn.textContent = "📄 PDF";
    pdfBtn.onclick = () => downloadPDF(window.currentCurriculumData);
    
    bar.appendChild(jsonBtn);
    bar.appendChild(pdfBtn);
    
    return bar;
}


// ===============================
// REFINEMENT UI HANDLERS
// ===============================
function showRefineBox(){
    const container = document.getElementById("refineContainer");
    if(container){
        container.style.display = "block";
    }
}

async function refinePlan(){
    const btn = document.getElementById("refineBtn");
    const text = document.getElementById("refineText");

    if(!text || !btn){
        alert("Refine UI not available");
        return;
    }

    const instruction = text.value.trim();
    if(!instruction){
        alert("Please enter a refinement instruction.");
        return;
    }

    if(!window.currentCurriculumData){
        alert("No generated curriculum found. Generate one first.");
        return;
    }

    try{
        btn.disabled = true;
        btn.textContent = "Refining...";

        const res = await fetch('/refine-plan',{
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ instruction: instruction, current_plan: window.currentCurriculumData })
        });

        if(!res.ok){
            const err = await res.text();
            throw new Error(err || 'Refinement failed');
        }

        const newData = await res.json();

        // Replace current plan and re-render
        window.currentCurriculumData = newData;
        console.log('Plan refined, new data stored:', newData);
        renderCurriculum(newData);

    }catch(e){
        console.error('Refinement error:', e);
        alert('Refinement failed: ' + (e.message || e));
    }finally{
        btn.disabled = false;
        btn.textContent = 'Refine Curriculum';
    }
}


