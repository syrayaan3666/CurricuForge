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
    
    // === DETAILED DEBUG LOGGING ===
    console.log("=== RENDER CURRICULUM DEBUG ===");
    console.log("Data passed to renderCurriculum:", data);
    console.log("Stored in window.currentCurriculumData:", window.currentCurriculumData);
    
    if (data.semesters && data.semesters.length > 0) {
        console.log(`NUMBER OF SEMESTERS: ${data.semesters.length}`);
        
        data.semesters.forEach((sem, semIdx) => {
            console.log(`\n--- SEMESTER ${sem.semester} ---`);
            if (sem.courses && sem.courses.length > 0) {
                console.log(`Number of courses: ${sem.courses.length}`);
                
                sem.courses.forEach((course, courseIdx) => {
                    console.log(`\nCourse ${courseIdx + 1}: ${course.title}`);
                    console.log(`  Has title: ${!!course.title}`);
                    console.log(`  Has difficulty: ${!!course.difficulty} (value: ${course.difficulty})`);
                    console.log(`  Has skills: ${!!course.skills} (count: ${course.skills ? course.skills.length : 0})`);
                    console.log(`  Has topics: ${!!course.topics} (count: ${course.topics ? course.topics.length : 0})`);
                    console.log(`  Has outcome_project: ${!!course.outcome_project}`);
                    console.log(`  Full course object:`, course);
                });
            } else {
                console.log(`ERROR: Semester has no courses!`);
            }
        });
    }
    
    console.log("=== END DEBUG ===\n");
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

function downloadPDF(data) {
    // data is passed directly from button click — guaranteed to be the exact rendered data
    console.log("=== DOWNLOAD PDF (Direct Data Pass) ===");
    console.log("Received data object:", data);
    console.log("Data has semesters:", !!data.semesters);
    console.log("Number of semesters:", data.semesters ? data.semesters.length : 0);
    
    if (data.semesters && data.semesters.length > 0) {
        console.log("First semester courses:", data.semesters[0].courses.length);
        if (data.semesters[0].courses.length > 0) {
            console.log("First course:", JSON.stringify(data.semesters[0].courses[0], null, 2));
        }
    }
    console.log("=== END DEBUG ===\n");
    
    if (!data) {
        alert("No curriculum data available. Please generate a curriculum first.");
        return;
    }
    
    // Show loading state
    const btn = event.target;
    const originalText = btn.textContent;
    btn.textContent = "Generating PDF...";
    btn.disabled = true;
    
    // Log what we're sending to backend
    const payloadToSend = { curriculum: data };
    console.log("Sending to /export-pdf:", payloadToSend);
    
    // POST to backend PDF generator
    fetch("/export-pdf", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payloadToSend)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.blob();
    })
    .then(blob => {
        // Create a download link and trigger download
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "curriculum.pdf";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
        console.log("PDF downloaded successfully");
        
        // Restore button
        btn.textContent = originalText;
        btn.disabled = false;
    })
    .catch(error => {
        console.error("PDF download error:", error);
        alert("Error generating PDF: " + error.message);
        
        // Restore button
        btn.textContent = originalText;
        btn.disabled = false;
    });
}

function createDownloadBar(data){
    console.log("createDownloadBar called with:", data);
    
    const bar = document.createElement("div");
    bar.className = "download-bar";
    
    const jsonBtn = document.createElement("button");
    jsonBtn.className = "download-btn download-json";
    jsonBtn.textContent = "📥 JSON";
    jsonBtn.onclick = () => downloadJSON(data);  // Pass data directly
    
    const pdfBtn = document.createElement("button");
    pdfBtn.className = "download-btn download-pdf";
    pdfBtn.textContent = "📄 PDF";
    pdfBtn.onclick = () => downloadPDF(data);  // Pass data directly
    
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


