// Personal Info
const nameInput = document.getElementById('name');
const emailInput = document.getElementById('email');
const phoneInput = document.getElementById('phone');
const linkedinInput = document.getElementById('linkedin');

nameInput.addEventListener('input', () => document.getElementById('preview-name').textContent = nameInput.value || 'Your Name');
emailInput.addEventListener('input', () => document.getElementById('preview-email').textContent = 'Email: ' + (emailInput.value || 'your.email@example.com'));
phoneInput.addEventListener('input', () => document.getElementById('preview-phone').textContent = 'Phone: ' + (phoneInput.value || '123-456-7890'));
linkedinInput.addEventListener('input', () => document.getElementById('preview-linkedin').textContent = 'LinkedIn: ' + (linkedinInput.value || 'linkedin.com/in/username'));

// Template Selection
document.getElementById('templateSelect').addEventListener('change', (e) => {
  const preview = document.getElementById('cvPreview');
  preview.className = 'cv-preview p-4 bg-white rounded shadow-sm ' + e.target.value;
});

// Dynamic Education
const educationFields = document.getElementById('educationFields');
const previewEdu = document.getElementById('preview-education');
document.getElementById('addEdu').addEventListener('click', () => addField('education'));

function addField(type){
  const div = document.createElement('div');
  div.classList.add('mb-2');
  const input = document.createElement('input');
  input.type = 'text';
  input.placeholder = type === 'education' ? 'Degree - Institution (Year)' : type === 'experience' ? 'Role - Company (Year)' : 'Project Name - Description';
  input.className = 'form-control';
  input.addEventListener('input', () => updatePreview(type));
  div.appendChild(input);
  if(type === 'education') educationFields.appendChild(div);
  if(type === 'experience') experienceFields.appendChild(div);
  if(type === 'project') projectFields.appendChild(div);
}

function updatePreview(type){
  const ul = type==='education'? previewEdu : type==='experience'? previewExp : previewProj;
  ul.innerHTML = '';
  const inputs = type==='education'? educationFields.querySelectorAll('input') :
                 type==='experience'? experienceFields.querySelectorAll('input') :
                 projectFields.querySelectorAll('input');
  inputs.forEach(inp => { if(inp.value){ const li=document.createElement('li'); li.textContent=inp.value; ul.appendChild(li); } });
}

// Dynamic Experience
const experienceFields = document.getElementById('experienceFields');
const previewExp = document.getElementById('preview-experience');
document.getElementById('addExp').addEventListener('click', () => addField('experience'));

// Dynamic Projects
const projectFields = document.getElementById('projectFields');
const previewProj = document.getElementById('preview-projects');
document.getElementById('addProj').addEventListener('click', () => addField('project'));

// Skills
const skillsFields = document.getElementById('skillsFields');
const previewSkills = document.getElementById('preview-skills');
document.getElementById('addSkill').addEventListener('click', () => {
  const div = document.createElement('div');
  div.className = 'mb-2 d-flex gap-2';
  const nameInput = document.createElement('input'); nameInput.type='text'; nameInput.placeholder='Skill Name'; nameInput.className='form-control skill-input';
  const valueInput = document.createElement('input'); valueInput.type='number'; valueInput.placeholder='Proficiency %'; valueInput.className='form-control skill-input';
  nameInput.addEventListener('input', updateSkills); valueInput.addEventListener('input', updateSkills);
  div.appendChild(nameInput); div.appendChild(valueInput);
  skillsFields.appendChild(div);
});
function updateSkills(){
  previewSkills.innerHTML = '';
  const skillDivs = skillsFields.querySelectorAll('div');
  skillDivs.forEach(div=>{
    const name = div.children[0].value; const val = div.children[1].value;
    if(name && val){
      const barOuter = document.createElement('div'); barOuter.className='skill-bar';
      const barInner = document.createElement('div'); barInner.className='skill-fill'; barInner.style.width=val+'%';
      barOuter.appendChild(barInner);
      const skillLabel = document.createElement('p'); skillLabel.textContent=name;
      previewSkills.appendChild(skillLabel); previewSkills.appendChild(barOuter);
    }
  });
}

// Download PDF
document.getElementById('downloadBtn').addEventListener('click', () => {
  html2pdf().set({ margin:0.5, filename:'My_CV.pdf', html2canvas:{ scale:2 } }).from(document.getElementById('cvPreview')).save();
});
