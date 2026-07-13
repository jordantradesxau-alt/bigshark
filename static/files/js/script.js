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
    // PREMIUM CINEMATIC INTRO (Only on first visit)
    // --------------------------

    // Check if intro has been shown before in this session
    if (sessionStorage.getItem('introShown')) {
        // Skip intro - show page immediately
        $("#intro-overlay").css("display", "none");
        $("body").removeClass("loading");
        $("#page-content").addClass("show");
        $("body").css("overflow", "auto");
    } else {
        // Show intro
        $("body").addClass("loading");

        // Create particles dynamically
        function createParticles() {
            var particlesContainer = document.getElementById('intro-particles');
            if (!particlesContainer) return;
            
            for (var i = 0; i < 60; i++) {
                var particle = document.createElement('div');
                particle.className = 'intro-particle';
                var size = Math.random() * 5 + 2;
                particle.style.width = size + 'px';
                particle.style.height = size + 'px';
                particle.style.left = Math.random() * 100 + '%';
                particle.style.animationDuration = (Math.random() * 25 + 18) + 's';
                particle.style.animationDelay = (Math.random() * 12) + 's';
                particle.style.opacity = Math.random() * 0.5 + 0.1;
                particle.style.background = 'rgba(100, 180, 255, ' + (Math.random() * 0.3 + 0.1) + ')';
                particlesContainer.appendChild(particle);
            }
        }

        createParticles();

        // Phase 1: Logo appears from almost invisible with 3D rotation
        setTimeout(function () {
            $("#intro-logo").css({
                transition: "all 1.8s cubic-bezier(0.16, 1, 0.3, 1)",
                transform: "perspective(1200px) rotateY(-8deg) rotateX(4deg) scale(0.4)",
                opacity: "0.1"
            });
        }, 200);

        // Phase 2: Logo scales to full with wave effect
        setTimeout(function () {
            $("#intro-logo").css({
                transform: "perspective(1200px) rotateY(2deg) rotateX(-1deg) scale(1.1)",
                opacity: "1",
                filter: "drop-shadow(0 0 40px rgba(0,183,255,0.6)) drop-shadow(0 0 80px rgba(0,183,255,0.3))"
            });
        }, 800);

        // Phase 3: Logo settles with slight wave
        setTimeout(function () {
            $("#intro-logo").css({
                transform: "perspective(1200px) rotateY(-3deg) rotateX(1deg) scale(1)",
                transition: "all 1.2s cubic-bezier(0.16, 1, 0.3, 1)"
            });
        }, 1800);

        // Phase 4: Dramatic pause - light sweep intensifies
        setTimeout(function () {
            $(".intro-light-sweep").css({
                animation: "lightSweep 1.5s ease-in-out"
            });
        }, 2500);

        // Phase 5: Logo shrinks and flies upward
        setTimeout(function () {
            $("#intro-logo-wrapper").css({
                transition: "all 1.8s cubic-bezier(0.16, 1, 0.3, 1)",
                transform: "translateY(-120px) scale(0.35)"
            });
            
            $("#intro-logo").css({
                transition: "all 1.8s cubic-bezier(0.16, 1, 0.3, 1)",
                transform: "perspective(1200px) rotateY(0deg) rotateX(0deg) scale(0.9)",
                filter: "drop-shadow(0 0 20px rgba(0,183,255,0.3))"
            });
        }, 3200);

        // Phase 6: Homepage fades in, intro disappears
        setTimeout(function () {
            $("#intro-overlay").addClass("hide");
            $("body").removeClass("loading");
            $("#page-content").addClass("show");
            $("body").css("overflow", "auto");
            
            // Mark intro as shown for this session
            sessionStorage.setItem('introShown', 'true');
        }, 4200);

        // Clean up intro overlay after transition
        setTimeout(function () {
            $("#intro-overlay").css("display", "none");
        }, 5000);
    }


    // --------------------------
    // AJAX ADD TO CART (No page reload)
    // --------------------------

    function updateCartCount(count) {
        var cartBadge = document.querySelector('.badge.bg-danger');
        if (cartBadge) {
            cartBadge.textContent = count;
        } else {
            // If no badge exists, create one
            var cartLink = document.querySelector('a[href="/cart"]');
            if (cartLink) {
                cartLink.classList.add('position-relative');
                var badge = document.createElement('span');
                badge.className = 'position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger';
                badge.textContent = count;
                cartLink.appendChild(badge);
            }
        }
    }

    function showToast(message, type) {
        // Remove existing toasts
        $('.toast-notification').remove();
        
        var toast = document.createElement('div');
        toast.className = 'toast-notification ' + type;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(function() {
            toast.classList.add('show');
        }, 100);
        
        setTimeout(function() {
            toast.classList.remove('show');
            setTimeout(function() {
                toast.remove();
            }, 300);
        }, 3000);
    }

    // Handle add to cart forms
    $(document).on('submit', 'form[action="/add_to_cart"]', function(e) {
        e.preventDefault(); // Stop page reload
        
        var form = $(this);
        var formData = new FormData(this);
        
        // Show loading state on button
        var btn = form.find('button[type="submit"]');
        var originalText = btn.html();
        btn.html('⏳ Adding...');
        btn.prop('disabled', true);
        
        $.ajax({
            url: '/add_to_cart',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            dataType: 'json',
            success: function(data) {
                if (data.success) {
                    // Update cart count
                    updateCartCount(data.cart_count);
                    showToast(data.message, 'success');
                    
                    // Update any other cart count displays
                    $('.cart-count').text(data.cart_count);
                } else {
                    showToast(data.message || 'Error adding to cart', 'error');
                }
            },
            error: function() {
                showToast('Error adding to cart. Please try again.', 'error');
            },
            complete: function() {
                // Reset button
                btn.html(originalText);
                btn.prop('disabled', false);
            }
        });
    });


    // --------------------------
    // SCROLL REVEAL (Enhanced)
    // --------------------------

    // Use IntersectionObserver for better performance
    function setupIntersectionObservers() {
        // Fade-up elements
        var fadeElements = document.querySelectorAll('.fade-up');
        if (fadeElements.length > 0) {
            var fadeObserver = new IntersectionObserver(function(entries) {
                entries.forEach(function(entry) {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('visible');
                    }
                });
            }, { threshold: 0.15, rootMargin: '0px 0px -50px 0px' });
            
            fadeElements.forEach(function(el) {
                fadeObserver.observe(el);
            });
        }

        // Zoom reveal
        var zoomElements = document.querySelectorAll('.reveal-zoom');
        if (zoomElements.length > 0) {
            var zoomObserver = new IntersectionObserver(function(entries) {
                entries.forEach(function(entry) {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('visible');
                    }
                });
            }, { threshold: 0.15, rootMargin: '0px 0px -50px 0px' });
            
            zoomElements.forEach(function(el) {
                zoomObserver.observe(el);
            });
        }

        // Rotate reveal
        var rotateElements = document.querySelectorAll('.reveal-rotate');
        if (rotateElements.length > 0) {
            var rotateObserver = new IntersectionObserver(function(entries) {
                entries.forEach(function(entry) {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('visible');
                    }
                });
            }, { threshold: 0.15, rootMargin: '0px 0px -50px 0px' });
            
            rotateElements.forEach(function(el) {
                rotateObserver.observe(el);
            });
        }

        // Depth reveal
        var depthElements = document.querySelectorAll('.reveal-depth');
        if (depthElements.length > 0) {
            var depthObserver = new IntersectionObserver(function(entries) {
                entries.forEach(function(entry) {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('visible');
                    }
                });
            }, { threshold: 0.15, rootMargin: '0px 0px -50px 0px' });
            
            depthElements.forEach(function(el) {
                depthObserver.observe(el);
            });
        }

        // Floating elements - start animation when visible
        var floatElements = document.querySelectorAll('.float-element');
        if (floatElements.length > 0) {
            var floatObserver = new IntersectionObserver(function(entries) {
                entries.forEach(function(entry) {
                    if (entry.isIntersecting) {
                        entry.target.style.animationPlayState = 'running';
                    }
                });
            }, { threshold: 0.1 });
            
            floatElements.forEach(function(el) {
                el.style.animationPlayState = 'paused';
                floatObserver.observe(el);
            });
        }
    }

    // Fallback for older browsers
    function fallbackReveal() {
        $(".fade-up, .reveal-zoom, .reveal-rotate, .reveal-depth").each(function() {
            var top = $(this).offset().top;
            var winBottom = $(window).scrollTop() + $(window).height();
            if (winBottom > top + 80) {
                $(this).addClass("visible");
            }
        });
    }

    // Use IntersectionObserver if available
    if (window.IntersectionObserver) {
        setupIntersectionObservers();
    } else {
        // Fallback for older browsers
        fallbackReveal();
        $(window).on("scroll", function() {
            fallbackReveal();
        });
    }


    // --------------------------
    // PARALLAX EFFECT
    // --------------------------

    function handleParallax() {
        var parallaxElements = document.querySelectorAll('.parallax-section');
        if (parallaxElements.length === 0) return;
        
        var scrollY = window.pageYOffset || document.documentElement.scrollTop;
        
        parallaxElements.forEach(function(el) {
            var speed = parseFloat(el.getAttribute('data-speed')) || 0.3;
            var offset = scrollY * speed;
            el.style.transform = 'translateY(' + offset + 'px)';
        });
    }

    // Throttled scroll for parallax
    var parallaxTimeout;
    $(window).on('scroll', function() {
        if (!parallaxTimeout) {
            parallaxTimeout = setTimeout(function() {
                handleParallax();
                parallaxTimeout = null;
            }, 10);
        }
    });


    // --------------------------
    // NAVBAR ANIMATION
    // --------------------------

    var navbar = document.getElementById('navbar');
    if (navbar) {
        var navbarHeight = navbar.offsetHeight;
        var lastScroll = 0;
        
        $(window).on('scroll', function() {
            var currentScroll = window.pageYOffset || document.documentElement.scrollTop;
            
            if (currentScroll > 100) {
                navbar.style.background = 'rgba(2, 6, 13, 0.92)';
                navbar.style.backdropFilter = 'blur(20px)';
                navbar.style.boxShadow = '0 4px 30px rgba(0,0,0,0.4)';
                navbar.style.borderBottom = '1px solid rgba(0,183,255,0.1)';
            } else {
                navbar.style.background = 'rgba(255,255,255,0.85)';
                navbar.style.backdropFilter = 'blur(12px)';
                navbar.style.boxShadow = 'none';
                navbar.style.borderBottom = '1px solid rgba(0,0,0,0.05)';
            }
            
            // Hide/show navbar on scroll direction
            if (currentScroll > navbarHeight) {
                if (currentScroll > lastScroll) {
                    // Scrolling down - hide navbar
                    navbar.style.transform = 'translateY(-100%)';
                    navbar.style.transition = 'transform 0.3s cubic-bezier(0.16, 1, 0.3, 1)';
                } else {
                    // Scrolling up - show navbar
                    navbar.style.transform = 'translateY(0)';
                    navbar.style.transition = 'transform 0.3s cubic-bezier(0.16, 1, 0.3, 1)';
                }
            } else {
                navbar.style.transform = 'translateY(0)';
            }
            
            lastScroll = currentScroll;
        });
    }


    // --------------------------
    // BACK TO TOP BUTTON
    // --------------------------

    var backToTop = document.getElementById('back-to-top');
    if (backToTop) {
        $(window).on('scroll', function() {
            var scroll = window.pageYOffset || document.documentElement.scrollTop;
            if (scroll > 400) {
                backToTop.style.display = 'flex';
                backToTop.style.opacity = '1';
            } else {
                backToTop.style.opacity = '0';
                setTimeout(function() {
                    if (parseInt(backToTop.style.opacity) === 0) {
                        backToTop.style.display = 'none';
                    }
                }, 300);
            }
        });
        
        backToTop.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }


    // --------------------------
    // SMOOTH ANCHOR SCROLLING
    // --------------------------

    $(document).on('click', 'a[href^="#"]', function(e) {
        var targetId = $(this).attr('href');
        if (targetId === '#') return;
        
        var target = document.querySelector(targetId);
        if (target) {
            e.preventDefault();
            var navbarHeight = document.getElementById('navbar') ? 
                document.getElementById('navbar').offsetHeight : 0;
            var targetPosition = target.getBoundingClientRect().top + 
                window.pageYOffset - navbarHeight - 20;
            
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    });


    // --------------------------
    // PERSPECTIVE MOVEMENT (Mouse tracking)
    // --------------------------

    var perspectiveElements = document.querySelectorAll('.perspective-container');
    if (perspectiveElements.length > 0 && window.innerWidth > 768) {
        $(document).on('mousemove', function(e) {
            var mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
            var mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
            
            perspectiveElements.forEach(function(el) {
                var children = el.querySelectorAll('.perspective-child');
                children.forEach(function(child) {
                    var speed = parseFloat(child.getAttribute('data-speed')) || 8;
                    var rotateY = mouseX * speed;
                    var rotateX = -mouseY * speed;
                    child.style.transform = 'rotateY(' + rotateY + 'deg) rotateX(' + rotateX + 'deg) translateZ(20px)';
                });
            });
        });
    }


    // --------------------------
    // HERO ANIMATION
    // --------------------------

    var heroSection = document.querySelector('.hero-section');
    if (heroSection) {
        $(window).on('scroll', function() {
            var scroll = window.pageYOffset || document.documentElement.scrollTop;
            var heroTop = heroSection.offsetTop;
            var heroHeight = heroSection.offsetHeight;
            
            if (scroll > heroTop - 100 && scroll < heroTop + heroHeight) {
                var progress = (scroll - heroTop + 100) / heroHeight;
                if (progress < 1) {
                    heroSection.style.transform = 'scale(' + (1 + progress * 0.02) + ')';
                    heroSection.style.opacity = 1 - progress * 0.3;
                }
            }
        });
    }


    // --------------------------
    // STAGGERED SECTION ANIMATIONS
    // --------------------------

    // Add staggered delay to child elements of sections
    $('.section-layered, .row, .col-md-4, .col-md-6, .col-md-12').each(function() {
        var children = $(this).children('.fade-up, .reveal-zoom, .reveal-rotate, .reveal-depth');
        if (children.length > 1) {
            children.each(function(index) {
                var delay = index * 0.1;
                $(this).css('transition-delay', delay + 's');
            });
        }
    });


    // --------------------------
    // ANIMATED BACKGROUNDS
    // --------------------------

    var animatedBgs = document.querySelectorAll('.animated-bg');
    if (animatedBgs.length > 0) {
        animatedBgs.forEach(function(el) {
            var intensity = parseFloat(el.getAttribute('data-intensity')) || 1;
            var bgEl = el.querySelector('.animated-bg-inner') || el;
            bgEl.style.animationDuration = (8 / intensity) + 's';
        });
    }


    // --------------------------
    // FLOATING ELEMENTS INIT
    // --------------------------

    // Ensure floating elements start paused until visible
    $('.float-element').each(function() {
        if (!$(this).hasClass('visible')) {
            this.style.animationPlayState = 'paused';
        }
    });


    // --------------------------
    // ORIGINAL SCROLL REVEAL (Keep for compatibility)
    // --------------------------

    function revealElements() {
        $(".fade-up").each(function() {
            if (!$(this).hasClass('visible')) {
                var top = $(this).offset().top;
                var winBottom = $(window).scrollTop() + $(window).height();
                if (winBottom > top + 80) {
                    $(this).addClass("visible");
                }
            }
        });
    }

    // Only run fallback if IntersectionObserver is not supported
    if (!window.IntersectionObserver) {
        revealElements();
        $(window).on("scroll", revealElements);
    }


    // --------------------------
    // PERFORMANCE: Clean up
    // --------------------------

    // Debounce resize events
    var resizeTimeout;
    $(window).on('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(function() {
            // Handle any resize-specific logic if needed
        }, 250);
    });


    // --------------------------
    // LOGGING
    // --------------------------

    console.log('✅ Big Shark - Premium experience loaded');
    console.log('🚀 Cinematic intro, parallax, and scroll effects active');

}); // END document.ready
