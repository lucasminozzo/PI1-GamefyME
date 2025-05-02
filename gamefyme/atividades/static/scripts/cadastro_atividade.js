function validarTempo(input) {
    const feedback = document.getElementById('tempo-feedback');
    const valor = input.value === "" ? null : parseInt(input.value);

    input.value = input.value.replace(/[^0-9]/g, '');

    if (input.value === "") {
        input.classList.remove('invalido');
        feedback.classList.remove('erro');
        feedback.textContent = 'Máximo 240 minutos (4 horas)';
        return;
    }

    if (valor < 1) {
        input.classList.add('invalido');
        feedback.classList.add('erro');
        feedback.textContent = 'Mínimo 1 minuto';
        return;
    }

    if (valor > 240) {
        input.classList.add('invalido');
        feedback.classList.add('erro');
        feedback.textContent = 'Máximo 240 minutos (4 horas)';
        return;
    }

    input.classList.remove('invalido');
    feedback.classList.remove('erro');
    feedback.textContent = `${valor} minutos`;
}