(function() {
    function discard_message(ev) {
        target = document.querySelector("#messages");
        while (target.firstChild) {
            target.removeChild(target.firstChild);
        }
    }

    function add_discard_function() {
        document.querySelectorAll('div[class="flash_close"]').forEach(
            (x) => { x.onclick = discard_message; }
        )
    }

    function main() {
        add_discard_function();
    }

    main();
})()