/**
 * Dashboard and main admin functionality
 */

// Page navigation
document.querySelectorAll('.menu a[data-page]').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const page = e.target.dataset.page;

        // Update active link
        document.querySelectorAll('.menu a').forEach(a => a.classList.remove('active'));
        e.target.classList.add('active');

        // Show page
        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
        document.getElementById(page + '-page').classList.add('active');

        // Load page data
        if (page === 'dashboard') loadDashboard();
        if (page === 'tests') loadTests();


        if (page === 'students') loadStudents();
    });
});

// Load dashboard
async function loadDashboard() {
    try {
        const response = await apiRequest('/api/v1/admin/students');
        const students = await response.json();

        const statsHtml = `
            <div class="stat-card">
                <h3>Jami talabalar</h3>
                <p class="stat-number">${students.length}</p>
            </div>
        `;
        document.getElementById('stats').innerHTML = statsHtml;
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Load tests
async function loadTests() {
    try {
        const response = await apiRequest('/api/v1/tests/');
        const tests = await response.json();

        let html = '<div class="test-cards">';
        tests.forEach(test => {
            html += `
                <div class="test-card">
                    <h3>${test.title}</h3>
                    <p>Kod: ${test.test_code}</p>
                    <p>${test.is_active ? '✅ Faol' : '❌ Nofaol'}</p>
                    <div class="test-card-actions">
                        <button class="btn-export" onclick="exportExcel('${test.id}')">📊 Excel yuklab olish</button>
                        <button class="btn-export" onclick="exportPDF('${test.id}')">📄 PDF yuklab olish</button>
                        <button class="btn-edit" onclick="openEditModal('${test.id}')">✏️ Tahrirlash</button>
                        <button class="btn-delete" onclick="deleteTest('${test.id}', '${test.title}')">🗑️ O'chirish</button>
                        <button class="btn-reset" onclick="clearSessions('${test.id}', '${test.title}')">🔄 Sessiyalarni tozalash</button>
                    </div>
                </div>
            `;
        });
        html += '</div>';

        document.getElementById('tests-list').innerHTML = html;
    } catch (error) {
        console.error('Error loading tests:', error);
    }
}



// Load students
async function loadStudents() {
    try {
        const response = await apiRequest('/api/v1/admin/students');
        const students = await response.json();

        let html = '<table><tr><th>Ism</th><th>Familiya</th><th>Viloyat</th><th>Ro\'yxatdan o\'tgan</th></tr>';
        students.forEach(student => {
            const date = new Date(student.created_at).toLocaleDateString();
            html += `<tr><td>${student.full_name}</td><td>${student.surname}</td><td>${student.region}</td><td>${date}</td></tr>`;
        });
        html += '</table>';

        document.getElementById('students-list').innerHTML = html;
    } catch (error) {
        console.error('Error loading students:', error);
    }
}

// Export functions
async function exportExcel(testId) {
    try {
        const response = await fetch(`${API_BASE}/api/v1/admin/export/${testId}/excel`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
            }
        });
        if (!response.ok) throw new Error('Yuklab olishda xatolik');
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'test_results.xlsx';
        a.click();
        URL.revokeObjectURL(url);
    } catch (error) {
        alert('Excel export xatolik: ' + error.message);
    }
}

async function exportPDF(testId) {
    try {
        const response = await fetch(`${API_BASE}/api/v1/admin/export/${testId}/pdf`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
            }
        });
        if (!response.ok) throw new Error('Yuklab olishda xatolik');
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'test_results.pdf';
        a.click();
        URL.revokeObjectURL(url);
    } catch (error) {
        alert('PDF export xatolik: ' + error.message);
    }
}

// ==========================================
// DELETE TEST
// ==========================================
async function deleteTest(testId, testTitle) {
    if (!confirm(`"${testTitle}" testini o'chirishni xohlaysizmi?\n\nBu amalni qaytarib bo'lmaydi! Barcha natijalar ham o'chiriladi.`)) {
        return;
    }

    try {
        await apiRequest(`/api/v1/tests/${testId}`, {
            method: 'DELETE'
        });

        alert('Test muvaffaqiyatli o\'chirildi!');
        loadTests();
    } catch (error) {
        alert('Xatolik: ' + error.message);
    }
}

// ==========================================
// CLEAR SESSIONS
// ==========================================
async function clearSessions(testId, testTitle) {
    if (!confirm(`"${testTitle}" testining barcha sessionlarini tozalashni xohlaysizmi?\n\nBarcha natijalar ham o'chiriladi va talabalar testni qayta topshira oladi.`)) {
        return;
    }

    try {
        const response = await apiRequest(`/api/v1/admin/sessions/${testId}`, {
            method: 'DELETE'
        });

        const data = await response.json();
        alert(`Tozalandi!\n${data.sessions_deleted} ta session va ${data.results_deleted} ta natija o'chirildi.`);
    } catch (error) {
        alert('Xatolik: ' + error.message);
    }
}

// ==========================================
// EDIT TEST
// ==========================================
let currentEditTestId = null;

async function openEditModal(testId) {
    currentEditTestId = testId;

    try {
        // Load test data with answer key
        const response = await apiRequest(`/api/v1/tests/${testId}`);
        const test = await response.json();

        // Fill in basic fields
        document.getElementById('edit-test-code').value = test.test_code;
        document.getElementById('edit-test-title').value = test.title;
        document.getElementById('edit-test-desc').value = test.description || '';
        document.getElementById('edit-test-active').checked = test.is_active;

        // Generate MCQ answer inputs
        let mcqGrid = '';
        for (let i = 1; i <= 35; i++) {
            const options = i <= 32
                ? ['A', 'B', 'C', 'D']
                : ['A', 'B', 'C', 'D', 'E', 'F'];

            const currentVal = (test.answer_key && test.answer_key.mcq_answers) ? (test.answer_key.mcq_answers[i] || 'A') : 'A';
            const optionsHTML = options.map(opt =>
                `<option value="${opt}" ${opt === currentVal ? 'selected' : ''}>${opt}</option>`
            ).join('');

            mcqGrid += `
                <div class="mcq-answer-input">
                    <label>Q${i}:</label>
                    <select id="edit-mcq-${i}">
                        ${optionsHTML}
                    </select>
                </div>
            `;
        }

        // Open-ended questions
        let openEndedHTML = '<div class="open-ended-section"><h3>Yozma savollar (36-37)</h3>';
        for (let i = 36; i <= 37; i++) {
            const aVal = (test.answer_key && test.answer_key.written_questions && test.answer_key.written_questions[i])
                ? (test.answer_key.written_questions[i].a || '') : '';
            const bVal = (test.answer_key && test.answer_key.written_questions && test.answer_key.written_questions[i])
                ? (test.answer_key.written_questions[i].b || '') : '';
            openEndedHTML += `
                <div class="open-question">
                    <h4>Savol ${i}</h4>
                    <div class="sub-answer">
                        <label>a)</label>
                        <input type="text" id="edit-open-${i}-a" value="${aVal}" placeholder="a) qism javobi">
                    </div>
                    <div class="sub-answer">
                        <label>b)</label>
                        <input type="text" id="edit-open-${i}-b" value="${bVal}" placeholder="b) qism javobi">
                    </div>
                </div>
            `;
        }
        openEndedHTML += '</div>';

        document.getElementById('edit-mcq-answers-grid').innerHTML = mcqGrid + openEndedHTML;
        document.getElementById('edit-test-modal').classList.remove('hidden');
    } catch (error) {
        alert('Test ma\'lumotlarini yuklashda xatolik: ' + error.message);
    }
}

document.getElementById('cancel-edit').addEventListener('click', () => {
    document.getElementById('edit-test-modal').classList.add('hidden');
    currentEditTestId = null;
});

document.getElementById('edit-test-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    // Collect MCQ answers
    const mcqAnswers = {};
    for (let i = 1; i <= 35; i++) {
        mcqAnswers[String(i)] = document.getElementById(`edit-mcq-${i}`).value;
    }

    // Collect open-ended answers
    const writtenQuestions = {};
    for (let i = 36; i <= 37; i++) {
        writtenQuestions[String(i)] = {
            a: document.getElementById(`edit-open-${i}-a`).value,
            b: document.getElementById(`edit-open-${i}-b`).value
        };
    }

    const updateData = {
        test_code: document.getElementById('edit-test-code').value,
        title: document.getElementById('edit-test-title').value,
        description: document.getElementById('edit-test-desc').value,
        is_active: document.getElementById('edit-test-active').checked,
        answer_key: {
            mcq_answers: mcqAnswers,
            written_questions: writtenQuestions
        }
    };

    try {
        await apiRequest(`/api/v1/tests/${currentEditTestId}`, {
            method: 'PATCH',
            body: JSON.stringify(updateData)
        });

        alert('Test muvaffaqiyatli yangilandi!');
        document.getElementById('edit-test-modal').classList.add('hidden');
        currentEditTestId = null;
        loadTests();
    } catch (error) {
        alert('Xatolik: ' + error.message);
    }
});


// ==========================================
// CREATE TEST MODAL
// ==========================================
document.getElementById('create-test-btn').addEventListener('click', () => {
    // Generate MCQ answer inputs
    let mcqGrid = '';
    for (let i = 1; i <= 35; i++) {
        const options = i <= 32
            ? ['A', 'B', 'C', 'D']
            : ['A', 'B', 'C', 'D', 'E', 'F'];

        const optionsHTML = options.map(opt => `<option value="${opt}">${opt}</option>`).join('');

        mcqGrid += `
            <div class="mcq-answer-input">
                <label>Q${i}:</label>
                <select id="mcq-${i}">
                    ${optionsHTML}
                </select>
            </div>
        `;
    }

    // Add open-ended questions (36-37)
    let openEndedHTML = '<div class="open-ended-section"><h3>Yozma savollar (36-37)</h3>';
    for (let i = 36; i <= 37; i++) {
        openEndedHTML += `
            <div class="open-question">
                <h4>Savol ${i}</h4>
                <div class="sub-answer">
                    <label>a)</label>
                    <input type="text" id="open-${i}-a" placeholder="a) qism javobi">
                </div>
                <div class="sub-answer">
                    <label>b)</label>
                    <input type="text" id="open-${i}-b" placeholder="b) qism javobi">
                </div>
            </div>
        `;
    }
    openEndedHTML += '</div>';

    document.getElementById('mcq-answers-grid').innerHTML = mcqGrid + openEndedHTML;

    // Reset form
    document.getElementById('create-test-form').reset();
    document.getElementById('create-test-modal').classList.remove('hidden');
});

document.getElementById('cancel-create').addEventListener('click', () => {
    document.getElementById('create-test-modal').classList.add('hidden');
});

document.getElementById('create-test-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    // Collect MCQ answers (1-35)
    const mcqAnswers = {};
    for (let i = 1; i <= 35; i++) {
        mcqAnswers[String(i)] = document.getElementById(`mcq-${i}`).value;
    }

    // Collect open-ended answers (36-37)
    const writtenQuestions = {};
    for (let i = 36; i <= 37; i++) {
        writtenQuestions[String(i)] = {
            a: document.getElementById(`open-${i}-a`).value,
            b: document.getElementById(`open-${i}-b`).value
        };
    }

    const testData = {
        test_code: document.getElementById('test-code').value,
        title: document.getElementById('test-title').value,
        description: document.getElementById('test-desc').value || null,
        answer_key: {
            mcq_answers: mcqAnswers,
            written_questions: writtenQuestions
        }
    };

    try {
        await apiRequest('/api/v1/tests/', {
            method: 'POST',
            body: JSON.stringify(testData)
        });

        alert('Test muvaffaqiyatli yaratildi!');
        document.getElementById('create-test-modal').classList.add('hidden');
        loadTests();
    } catch (error) {
        alert('Xatolik: ' + error.message);
    }
});

// Expose functions globally
window.submitGrade = submitGrade;
window.exportExcel = exportExcel;
window.exportPDF = exportPDF;
window.deleteTest = deleteTest;
window.openEditModal = openEditModal;
window.clearSessions = clearSessions;

// Load dashboard on init
if (isLoggedIn()) {
    loadDashboard();
}
