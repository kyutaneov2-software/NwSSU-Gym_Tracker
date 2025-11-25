// Show/hide student number requirement based on member type
document.getElementById('member_type').addEventListener('change', function() {
    const studentNumberField = document.getElementById('student_number');
    const studentNumberLabel = studentNumberField.parentElement.querySelector('label');

    if (this.value === 'Student') {
        studentNumberField.required = true;
        studentNumberLabel.innerHTML = 'Student Number <span class="required">*</span>';
    } else {
        studentNumberField.required = false;
        studentNumberLabel.textContent = 'Student Number';
    }
});

function togglePassword(id, icon) {
    const input = document.getElementById(id);

    if (input.type === "password") {
        input.type = "text";
        icon.classList.remove("fa-eye");
        icon.classList.add("fa-eye-slash");
    } else {
        input.type = "password";
        icon.classList.remove("fa-eye-slash");
        icon.classList.add("fa-eye");
    }
}




