function toggleTheme() {
    const body = document.body;
    const themeIcon = document.getElementById('themeIcon');
    const themeText = document.getElementById('themeText');

    body.classList.toggle('light-mode');

    // Animate icon rotation
    themeIcon.classList.add('rotate');
    setTimeout(() => themeIcon.classList.remove('rotate'), 500);

    if (body.classList.contains('light-mode')) {
        themeIcon.classList.remove('fa-moon');
        themeIcon.classList.add('fa-sun');
        themeText.textContent = 'Light';
        localStorage.setItem('theme', 'light');
    } else {
        themeIcon.classList.remove('fa-sun');
        themeIcon.classList.add('fa-moon');
        themeText.textContent = 'Dark';
        localStorage.setItem('theme', 'dark');
    }
}

// Preserve theme on page load
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme');
    const themeIcon = document.getElementById('themeIcon');
    const themeText = document.getElementById('themeText');

    if (savedTheme === 'light') {
        document.body.classList.add('light-mode');
        themeIcon.classList.replace('fa-moon', 'fa-sun');
        themeText.textContent = 'Light';
    } else {
        document.body.classList.remove('light-mode');
        themeIcon.classList.replace('fa-sun', 'fa-moon');
        themeText.textContent = 'Dark';
    }
});

// Handle the short announcement in the landing page
const announcements = [
    "System admin panel is under development.",
    "This is a demo only!",
    "Mobile app version coming soon!",
    "Stay tuned for system improvements!"
];

let index = 0;
const textElement = document.getElementById("announcementText");

setInterval(() => {
    index = (index + 1) % announcements.length;
    textElement.style.opacity = 0;
    setTimeout(() => {
        textElement.textContent = announcements[index];
        textElement.style.opacity = 1;
    }, 500);
}, 3500);

// Handle Passwords show or not show
const togglePassword = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');

    togglePassword.addEventListener('click', () => {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);

        // Toggle icon
        togglePassword.classList.toggle('fa-eye');
        togglePassword.classList.toggle('fa-eye-slash');
});