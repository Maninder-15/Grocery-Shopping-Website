const searchInput = document.getElementById("searchInput");
const productCards = document.querySelectorAll(".product-card");
const categoryButtons = document.querySelectorAll(".category-buttons button");

searchInput.addEventListener("keyup", function () {

    const value = this.value.toLowerCase();

    productCards.forEach(card => {

        const productName = card.querySelector("h3").textContent.toLowerCase();

        if(productName.includes(value)){
            card.style.display = "block";
        }else{
            card.style.display = "none";
        }

    });

});

categoryButtons.forEach(button => {

    button.addEventListener("click", function () {

        categoryButtons.forEach(btn => btn.classList.remove("active"));
        this.classList.add("active");

        const category = this.textContent.toLowerCase();

        productCards.forEach(card => {

            const productName = card.querySelector("h3").textContent.toLowerCase();

            if(category === "all"){
                card.style.display = "block";
            }
            else if(category === "fruits"){

                if(productName === "apple" || productName === "banana"){
                    card.style.display = "block";
                }else{
                    card.style.display = "none";
                }

            }
            else if(category === "vegetables"){

                if(productName === "tomato"){
                    card.style.display = "block";
                }else{
                    card.style.display = "none";
                }

            }
            else if(category === "dairy"){

                if(productName === "milk"){
                    card.style.display = "block";
                }else{
                    card.style.display = "none";
                }

            }
            else if(category === "beverages"){

                if(productName === "orange juice"){
                    card.style.display = "block";
                }else{
                    card.style.display = "none";
                }

            }
            else if(category === "bakery"){

                if(productName === "bread"){
                    card.style.display = "block";
                }else{
                    card.style.display = "none";
                }

            }

        });

    });

});

document.querySelectorAll(".cart-btn").forEach(button => {

    button.addEventListener("click", function () {

        alert("Product added to cart.");

    });

});

document.querySelectorAll(".buy-btn").forEach(button => {

    button.addEventListener("click", function () {

        window.location.href="/checkout";

    });

});