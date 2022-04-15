var table = document.getElementsByClassName('dataframe');
if (table.length > 0){
    table[0].setAttribute("class", "table table-dark table-hover table-responsive");
}



var images = document.getElementsByTagName('img');


for (var i=0; i<images.length; i++){
    images[i].setAttribute("class", "rounded mx-auto d-block");
}

var navbar = document.getElementById('nav-bar-placeholder');
navbar.innerHTML = '<!-- Image and text -->\n' +
    '<nav class="navbar navbar-expand-lg navbar-dark" style="background-color:darkgreen;">\n' +
    '  <a class="navbar-brand" href=".">\n' +
    '    <img src="https://static.djangoproject.com/img/logo-django.42234b631760.svg" width="30" height="30" class="d-inline-block align-top" alt="">\n' +
    '    <span style="color: aliceblue">Weather Production Project</span>\n' +
    '  </a>\n'+
    '  <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNavAltMarkup" aria-controls="navbarNavAltMarkup" aria-expanded="false" aria-label="Toggle navigation">\n' +
    '    <span class="navbar-toggler-icon"></span>\n' +
    '  </button>\n' +
    '  <div class="collapse navbar-collapse" id="navbarNavAltMarkup">\n' +
    '    <div class="navbar-nav">'+
    '        <a class="nav-item nav-link" href="./production" >Production</a>\n' +
        '        <a class="nav-item nav-link" href="./model" >Model</a>\n' +
    '</nav>';