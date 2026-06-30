// ==============================
// BIG SHARK JAVASCRIPT
// ==============================

$(document).ready(function () {

    // --------------------------
    // LIGHT SLIDER
    // --------------------------

    $('.autoWidth').lightSlider({
        autoWidth: true,
        loop: true,
        onSliderLoad: function () {
            $('.autoWidth').removeClass('cS-hidden');
        }
    });


    // --------------------------
    // INTRO ANIMATION
    // --------------------------

    $("body").addClass("loading");

    setTimeout(function () {

        $("#intro-logo").css({
            transition: "all 1.5s ease",
            transform: "translateY(-220px) scale(.30)",
            opacity: ".95"
        });

    }, 2300);


    setTimeout(function () {

        $("#intro-overlay").addClass("hide");

        $("body").removeClass("loading");

        $("#page-content").addClass("show");

    }, 3800);



    // --------------------------
    // SCROLL REVEAL
    // --------------------------

    function revealElements() {

        $(".fade-up").each(function () {

            let top = $(this).offset().top;
            let winBottom = $(window).scrollTop() + $(window).height();

            if (winBottom > top + 80) {

                $(this).addClass("visible");

            }

        });

    }

    revealElements();

    $(window).on("scroll", revealElements);

});
