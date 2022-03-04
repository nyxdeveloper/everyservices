/*
Author URI: http://webthemez.com/
Note: 
Licence under Creative Commons Attribution 3.0 
Do not remove the back-link in this web template 
-------------------------------------------------------*/

$(window).load(function () {
    $("#record-date").val(new Date().toISOString().substring(0, 10));

    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            $("#free-times").html(xhr.responseText);
        }
    }
    var date = $("#record-date").val();
    if (date === "") {
        $("free-times").html("");
        return
    }
    var service = $("#service-select").find(":selected").val();
    var url = this.origin + "/portfolio/get_free_time/" + service + "/" + date + "/";
    xhr.open("GET", url, true);
    xhr.send(null);

    jQuery('#all').click();
    return false;
});

$(document).ready(function () {
    $('.carousel').carousel();
    $('#header_wrapper').scrollToFixed();
    $('.res-nav_click').click(function () {
        $('.main-nav').slideToggle();
        return false

    });

    function resizeText() {
        var preferredWidth = 767;
        var displayWidth = window.innerWidth;
        var percentage = displayWidth / preferredWidth;
        var fontsizetitle = 25;
        var newFontSizeTitle = Math.floor(fontsizetitle * percentage);
        $(".divclass").css("font-size", newFontSizeTitle)
    }

    if ($('#main-nav ul li:first-child').hasClass('active')) {
        $('#main-nav').css('background', 'none');
    }
    $('#mainNav').onePageNav({
        currentClass: 'active',
        changeHash: false,
        scrollSpeed: 950,
        scrollThreshold: 0.2,
        filter: '',
        easing: 'swing',
        begin: function () {
        },
        end: function () {
            if (!$('#main-nav ul li:first-child').hasClass('active')) {
                $('.header').addClass('addBg');
            } else {
                $('.header').removeClass('addBg');
            }

        },
        scrollChange: function ($currentListItem) {
            if (!$('#main-nav ul li:first-child').hasClass('active')) {
                $('.header').addClass('addBg');
            } else {
                $('.header').removeClass('addBg');
            }
        }
    });

    var container = $('#portfolio_wrapper');


    container.isotope({
        animationEngine: 'best-available',
        animationOptions: {
            duration: 200,
            queue: false
        },
        layoutMode: 'fitRows'
    });

    $('#filters a').click(function () {
        $('#filters a').removeClass('active');
        $(this).addClass('active');
        var selector = $(this).attr('data-filter');
        container.isotope({
            filter: selector
        });
        setProjects();
        return false;
    });

    function splitColumns() {
        var winWidth = $(window).width(),
            columnNumb = 1;


        if (winWidth > 1024) {
            columnNumb = 4;
        } else if (winWidth > 900) {
            columnNumb = 2;
        } else if (winWidth > 479) {
            columnNumb = 2;
        } else if (winWidth < 479) {
            columnNumb = 1;
        }

        return columnNumb;
    }

    function setColumns() {
        var winWidth = $(window).width(),
            columnNumb = splitColumns(),
            postWidth = Math.floor(winWidth / columnNumb);

        container.find('.portfolio-item').each(function () {
            $(this).css({
                width: postWidth + 'px'
            });
        });
    }

    function setProjects() {
        setColumns();
        container.isotope('reLayout');
    }

    container.imagesLoaded(function () {
        setColumns();
    });


    $(window).bind('resize', function () {
        setProjects();
    });

    $(".fancybox").fancybox();
});

wow = new WOW({
    animateClass: 'animated',
    offset: 100
});
wow.init();
// document.getElementById('').onclick = function () {
//     var section = document.createElement('section');
//     section.className = 'wow fadeInDown';
//     section.className = 'wow shake';
//     section.className = 'wow zoomIn';
//     section.className = 'wow lightSpeedIn';
//     this.parentNode.insertBefore(section, this);
// };

$("#service-select").change(function () {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            $("#free-times").html(xhr.responseText);
        }
    }
    var date = $("#record-date").val();
    if (date === "") {
        return
    }
    var service = $("#service-select").find(":selected").val();
    var url = document.defaultView.origin + "/portfolio/get_free_time/" + service + "/" + date + "/";
    xhr.open("GET", url, true);
    xhr.send(null);
})

$("#record-date").change(function () {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            $("#free-times").html(xhr.responseText);
        }
    }
    var date = $("#record-date").val();
    if (date === "") {
        return
    }
    var service = $("#service-select").find(":selected").val();
    var url = document.defaultView.origin + "/portfolio/get_free_time/" + service + "/" + date + "/";
    xhr.open("GET", url, true);
    xhr.send(null);
})