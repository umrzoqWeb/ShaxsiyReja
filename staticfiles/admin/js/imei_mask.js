document.addEventListener("DOMContentLoaded", function () {
    var imeiField = document.querySelector("#id_imei");
    if (imeiField) {
        $(imeiField).inputmask("999999999999999"); // faqat 15 ta raqam
    }
});
