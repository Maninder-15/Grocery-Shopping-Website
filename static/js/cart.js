const plusButtons = document.querySelectorAll(".plus");
const minusButtons = document.querySelectorAll(".minus");
const removeButtons = document.querySelectorAll(".remove-btn");

function updateCart(){

    let subtotal = 0;

    document.querySelectorAll("tbody tr").forEach(row=>{

        const price = parseFloat(row.querySelector(".price").textContent);
        const quantity = parseInt(row.querySelector(".quantity").textContent);

        const total = price * quantity;

        row.querySelector(".total").textContent = total.toFixed(2);

        subtotal += total;

    });

    document.getElementById("subtotal").textContent = subtotal.toFixed(2);

    const delivery = 50;

    document.getElementById("grandTotal").textContent = (subtotal + delivery).toFixed(2);

}

plusButtons.forEach(button=>{

    button.addEventListener("click",()=>{

        const quantity = button.parentElement.querySelector(".quantity");

        quantity.textContent = parseInt(quantity.textContent) + 1;

        updateCart();

    });

});

minusButtons.forEach(button=>{

    button.addEventListener("click",()=>{

        const quantity = button.parentElement.querySelector(".quantity");

        let value = parseInt(quantity.textContent);

        if(value > 1){

            quantity.textContent = value - 1;

            updateCart();

        }

    });

});

removeButtons.forEach(button=>{

    button.addEventListener("click",()=>{

        button.closest("tr").remove();

        updateCart();

    });

});

updateCart();
