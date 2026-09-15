document.addEventListener("DOMContentLoaded", () => {

    const links = document.querySelectorAll('a[href^="#"]');

    links.forEach(link => {
        link.addEventListener("click", function(e) {

            const target = document.querySelector(this.getAttribute("href"));

            if(target){

                e.preventDefault();

                target.scrollIntoView({
                    behavior: "smooth"
                });

            }

        });
    });

    const cards = document.querySelectorAll(".category-card,.feature-box");

    const observer = new IntersectionObserver((entries)=>{

        entries.forEach(entry=>{

            if(entry.isIntersecting){

                entry.target.style.opacity="1";
                entry.target.style.transform="translateY(0px)";

            }

        });

    },{
        threshold:0.2
    });

    cards.forEach(card=>{

        card.style.opacity="0";
        card.style.transform="translateY(40px)";
        card.style.transition="0.6s";

        observer.observe(card);

    });

    const button=document.querySelector(".btn");

    if(button){

        button.addEventListener("mouseenter",()=>{

            button.style.transform="scale(1.05)";

        });

        button.addEventListener("mouseleave",()=>{

            button.style.transform="scale(1)";

        });

    }

});