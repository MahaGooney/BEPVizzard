(function () {
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

    function confirm_action(ev) {
        target = ev.target;
        console.log("confirm_action target: " + target);
        text = target.dataset.message || "Soll die Aktion wirklich durchgeführt werden?";
        if (!confirm(text)) {
            ev.preventDefault();
        }
    }
    function add_confirm() {
        document.querySelectorAll('a.button.danger').forEach(
            (x) => { x.onclick = confirm_action; }
        )
    }

    function closeAllSelect(elmnt) {
        /* A function that will close all select boxes in the document,
        except the current select box: */
        var x, y, i, xl, yl, arrNo = [];
        x = document.getElementsByClassName("select-items");
        y = document.getElementsByClassName("select-selected");
        xl = x.length;
        yl = y.length;
        for (i = 0; i < yl; i++) {
            if (elmnt == y[i]) {
                arrNo.push(i)
            } else {
                y[i].classList.remove("select-arrow-active");
            }
        }
        for (i = 0; i < xl; i++) {
            if (arrNo.indexOf(i)) {
                x[i].classList.add("select-hide");
            }
        }
    }

    function addSliderSync() {
        const fixkslider = document.getElementById('s_fixkosten');
        const fixk = document.getElementById('fixkosten');
        fixkslider.addEventListener('input', () => {
            fixk.value = fixkslider.value;
        });
        fixk.addEventListener('input', () => {
            fixkslider.value = fixk.value;
        });

        const varkslider = document.getElementById('s_varkosten');
        const vark = document.getElementById('varkosten');
        varkslider.addEventListener('input', () => {
            vark.value = varkslider.value;
        });
        vark.addEventListener('input', () => {
            varkslider.value = vark.value;
        });

        const preisslider = document.getElementById('s_preis');
        const preis = document.getElementById('preis');
        preisslider.addEventListener('input', () => {
            preis.value = preisslider.value;
        });
        preis.addEventListener('input', () => {
            preisslider.value = preis.value;
        });

    }

    function addConfirmPasswordCheck() {
        const new_password = document.getElementById('new_password');
        const confirm_password = document.getElementById('confirm_password');
        const form = document.getElementById('change-password-form');

        let lastClickedButton = null;

        // Merken, welcher Button zuletzt geklickt wurde
        form.querySelectorAll('button[name="submit"]').forEach(button => {
            button.addEventListener('click', (e) => {
                lastClickedButton = e.target;
            });
        });

        function validatePasswordMatch(setValidity = false) {
            const match = new_password.value === confirm_password.value && new_password.value !== "";
            if (match) {
                confirm_password.classList.remove('no-match');
                // Validity zurücksetzen
                if (setValidity) confirm_password.setCustomValidity("");
            } else {
                confirm_password.classList.add('no-match');
                if (setValidity) {
                    confirm_password.setCustomValidity("Die Passwörter stimmen nicht überein.");
                } else {
                    // Zwischenzeitlich keine Meldung
                    confirm_password.setCustomValidity("");
                }
            }
            return match;
        }

        // Eingabe: nur Farbe
        confirm_password.addEventListener('input', () => validatePasswordMatch(false));

        // Beim Submit: mit Validity-Message
        form.addEventListener('submit', function (e) {
            const isRealSubmit = lastClickedButton?.value === "submit";
            if (isRealSubmit) {
                const match = validatePasswordMatch(true);
                if (!match) {
                    confirm_password.reportValidity();
                    e.preventDefault();
                }
            } else {
                // Bei "cancel" sicherheitshalber Validierungszustand entfernen
                confirm_password.setCustomValidity("");
            }
        });
    }

    function addUserEditSelect() {
        var x, i, j, l, ll, selElmnt, a, b, c;
        /* Look for any elements with the class "custom-select": */
        x = document.getElementsByClassName("custom-select");
        l = x.length;
        for (i = 0; i < l; i++) {
            selElmnt = x[i].getElementsByTagName("select")[0];
            ll = selElmnt.length;
            /* For each element, create a new DIV that will act as the selected item: */
            a = document.createElement("DIV");
            a.setAttribute("class", "select-selected");
            a.innerHTML = selElmnt.options[selElmnt.selectedIndex].innerHTML;
            x[i].appendChild(a);
            /* For each element, create a new DIV that will contain the option list: */
            b = document.createElement("DIV");
            b.setAttribute("class", "select-items select-hide");
            for (j = 1; j < ll; j++) {
                /* For each option in the original select element,
                create a new DIV that will act as an option item: */
                c = document.createElement("DIV");
                c.innerHTML = selElmnt.options[j].innerHTML;
                c.addEventListener("click", function (e) {
                    /* When an item is clicked, update the original select box,
                    and the selected item: */
                    var y, i, k, s, h, sl, yl;
                    s = this.parentNode.parentNode.getElementsByTagName("select")[0];
                    sl = s.length;
                    h = this.parentNode.previousSibling;
                    for (i = 0; i < sl; i++) {
                        if (s.options[i].innerHTML == this.innerHTML) {
                            s.selectedIndex = i;
                            h.innerHTML = this.innerHTML;
                            y = this.parentNode.getElementsByClassName("same-as-selected");
                            yl = y.length;
                            for (k = 0; k < yl; k++) {
                                y[k].removeAttribute("class");
                            }
                            this.setAttribute("class", "same-as-selected");
                            break;
                        }
                    }
                    h.click();
                });
                b.appendChild(c);
            }
            x[i].appendChild(b);
            a.addEventListener("click", function (e) {
                /* When the select box is clicked, close any other select boxes,
                and open/close the current select box: */
                e.stopPropagation();
                closeAllSelect(this);
                this.nextSibling.classList.toggle("select-hide");
                this.classList.toggle("select-arrow-active");
            });
        }
        /* If the user clicks anywhere outside the select box,
        then close all select boxes: */
        document.addEventListener("click", closeAllSelect);
    }

    function main() {
        add_discard_function();
        add_confirm();
        currentpage = window.location.pathname;
        if (currentpage.endsWith("change_password")) {
            addConfirmPasswordCheck();
        }
        if (currentpage.endsWith("bep_calc")) {
            addSliderSync();
        }
        if (currentpage.endsWith("edit") || currentpage.endsWith("add_user")) {
            addUserEditSelect();
        }
    }

    main();
})()