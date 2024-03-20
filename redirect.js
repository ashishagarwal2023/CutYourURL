const redirectDomain = "https://cutyoururl.pythonanywhere.com/";
const path = window.location.pathname;
const search = window.location.search;
const newUrl = redirectDomain + path + search;
window.location.replace(newUrl);

