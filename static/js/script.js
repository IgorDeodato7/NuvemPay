
const togglePassword = document.getElementById("togglePassword");
const passwordInput = document.getElementById("senha");

togglePassword.addEventListener("click", () => {
    const mostrando = passwordInput.type === "text";

    passwordInput.type = mostrando ? "password" : "text";
    togglePassword.textContent = mostrando
        ? "Mostrar"
        : "Ocultar";

    togglePassword.setAttribute(
        "aria-label",
        mostrando ? "Mostrar senha" : "Ocultar senha"
    );
});
