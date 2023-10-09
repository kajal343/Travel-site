const wrapper=document.querySelector('.wrapper');
const loginLink=document.querySelector('.login-link');
const registerLink=document.querySelector('.register-link');
const btnpop=document.querySelector('.butlogin');
const iconclose=document.querySelector('.icon-close');

registerLink.addEventListener('click', ()=>{
    wrapper.classList.add('active');
});
loginLink.addEventListener('click', ()=>{
    wrapper.classList.remove('active');
});
btnpop.addEventListener('click', ()=>{
    wrapper.classList.add('active-popup');
});
iconclose.addEventListener('click', ()=>{
    wrapper.classList.remove('active-popup');
});

// Login form submit event
document.getElementById('login').addEventListener('submit', function (event) {
    event.preventDefault();
    const username = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    // Send a POST request to your Flask backend's login endpoint
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/login', true);
    xhr.setRequestHeader('Content-Type', 'application/json');

    xhr.onload = function () {
        if (xhr.status === 200) {
            // Successful login, handle the response
            const response = JSON.parse(xhr.responseText);
            alert(response.message);
        } else {
            // Error occurred during login
            alert('Login failed. Please check your credentials.');
        }
    };

    const data = JSON.stringify({ email, password });
    xhr.send(data);
});

