$(document).ready(function() {
    const csrfToken = $('input[name=csrfmiddlewaretoken]').val();

    // --- LÓGICA MODAL ALERGIAS ---
    $('#crearAlergiaForm').submit(function(e) {
        e.preventDefault();
        const nombreAlergia = $('#nueva_alergia_nombre').val().trim();
        if (!nombreAlergia) return;

        $.ajax({
            url: '/historiales/ajax/crear-alergia/',
            method: 'POST',
            headers: { 'X-CSRFToken': csrfToken },
            contentType: 'application/json',
            data: JSON.stringify({ nombre: nombreAlergia }),
            success: function(response) {
                if (response.success) {
                    const newCheckbox = `
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" name="alergias" value="${response.id}" id="id_alergias_${response.id}">
                            <label class="form-check-label" for="id_alergias_${response.id}">${response.nombre}</label>
                        </div>`;
                    $('#id_alergias_container').append(newCheckbox);
                    $('#crearAlergiaModal').modal('hide');
                    $('#nueva_alergia_nombre').val('');
                } else {
                    alert(`Error al crear la alergia: ${response.errors}`);
                }
            },
            error: function() {
                alert('Ocurrió un error de comunicación al crear la alergia.');
            }
        });
    });

    // --- LÓGICA MODAL ENFERMEDADES ---
    $('#crearEnfermedadForm').submit(function(e) {
        e.preventDefault();
        const nombreEnfermedad = $('#nueva_enfermedad_nombre').val().trim();
        if (!nombreEnfermedad) return;

        $.ajax({
            url: '/historiales/ajax/crear-enfermedad/',
            method: 'POST',
            headers: { 'X-CSRFToken': csrfToken },
            contentType: 'application/json',
            data: JSON.stringify({ nombre: nombreEnfermedad }),
            success: function(response) {
                if (response.success) {
                    const newCheckbox = `
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" name="enfermedades_preexistentes" value="${response.id}" id="id_enfermedades_preexistentes_${response.id}">
                            <label class="form-check-label" for="id_enfermedades_preexistentes_${response.id}">${response.nombre}</label>
                        </div>`;
                    $('#id_enfermedades_preexistentes_container').append(newCheckbox);
                    $('#crearEnfermedadModal').modal('hide');
                    $('#nueva_enfermedad_nombre').val('');
                } else {
                    alert(`Error al crear la enfermedad: ${response.errors}`);
                }
            },
            error: function() {
                alert('Ocurrió un error de comunicación al crear la enfermedad.');
            }
        });
    });

    // --- LÓGICA MODAL MEDICAMENTOS (UNIFICADO) ---
    const medForm = $('#crearMedicamentoForm');
    const catSelect = medForm.find('#id_categoria');
    const provSelect = medForm.find('#id_proveedor');

    // Delegación de eventos para los botones "Nuevo" y "Cancelar"
    $(document).on('click', '#new-categoria-btn', function() {
        catSelect.prop('disabled', true).parent().hide();
        $('#new-categoria-form').show();
    });
    $(document).on('click', '#cancel-new-categoria-btn', function() {
        $('#new-categoria-form').hide();
        catSelect.prop('disabled', false).parent().show();
        $('#new-categoria-name').val('');
    });

    $(document).on('click', '#new-proveedor-btn', function() {
        provSelect.prop('disabled', true).parent().hide();
        $('#new-proveedor-form').show();
    });
    $(document).on('click', '#cancel-new-proveedor-btn', function() {
        $('#new-proveedor-form').hide();
        provSelect.prop('disabled', false).parent().show();
        $('#new-proveedor-name').val('');
    });

    // Envío del formulario de medicamentos
    medForm.submit(async function(e) {
        e.preventDefault();
        console.log("Formulario de medicamento enviado.");

        medForm.find('.is-invalid').removeClass('is-invalid');
        medForm.find('.invalid-feedback').text('');

        let categoriaId = catSelect.val();
        let proveedorId = provSelect.val();

        try {
            const newCatName = $('#new-categoria-name').val().trim();
            if (newCatName) {
                console.log(`Intentando crear nueva categoría: ${newCatName}`);
                const catResponse = await $.ajax({
                    url: '/inventario/ajax/crear-categoria/',
                    method: 'POST',
                    headers: { 'X-CSRFToken': csrfToken },
                    contentType: 'application/json',
                    data: JSON.stringify({ nombre: newCatName })
                });
                console.log("Respuesta de creación de categoría:", catResponse);
                categoriaId = catResponse.id;
                catSelect.append(new Option(catResponse.nombre, catResponse.id, true, true));
                $('#cancel-new-categoria-btn').click();
            }

            const newProvName = $('#new-proveedor-name').val().trim();
            if (newProvName) {
                console.log(`Intentando crear nuevo proveedor: ${newProvName}`);
                const provResponse = await $.ajax({
                    url: '/inventario/ajax/crear-proveedor/',
                    method: 'POST',
                    headers: { 'X-CSRFToken': csrfToken },
                    // --- Corrección aquí ---
                    contentType: 'application/json', // Especificar que se envía JSON
                    data: JSON.stringify({ nombre: newProvName }) // Convertir datos a string JSON
                    // --- Fin Corrección ---
                });
                console.log("Respuesta de creación de proveedor:", provResponse);
                proveedorId = provResponse.id;
                provSelect.append(new Option(provResponse.nombre, provResponse.id, true, true));
                $('#cancel-new-proveedor-btn').click();
            }

            const medData = {
                nombre: medForm.find('#id_nombre').val(),
                precio_unitario: medForm.find('#id_precio_unitario').val(),
                categoria: categoriaId,
                proveedor: proveedorId
            };
            console.log("Intentando crear medicamento con datos:", medData);

            const medResponse = await $.ajax({
                url: '/inventario/ajax/crear-medicamento/',
                method: 'POST',
                headers: { 'X-CSRFToken': csrfToken },
                data: medData
            });
            console.log("Respuesta de creación de medicamento:", medResponse);

            const newCheckbox = `
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" name="medicamentos_actuales" value="${medResponse.id}" id="id_medicamentos_actuales_${medResponse.id}">
                    <label class="form-check-label" for="id_medicamentos_actuales_${medResponse.id}">${medResponse.nombre}</label>
                </div>`;
            $('#id_medicamentos_actuales_container').append(newCheckbox);
            $('#crearMedicamentoModal').modal('hide');
            medForm[0].reset();
            $('#cancel-new-categoria-btn').click();
            $('#cancel-new-proveedor-btn').click();
            // Re-enable selects for next time
            catSelect.prop('disabled', false);
            provSelect.prop('disabled', false);

        } catch (error) {
            console.error("Error completo en el bloque catch:", error);
            const response = error.responseJSON;
            if (response && response.errors) {
                console.error("Errores de validación del backend:", response.errors);
                for (const field in response.errors) {
                    const input = medForm.find(`#id_${field}`);
                    input.addClass('is-invalid');
                    input.next('.invalid-feedback').text(response.errors[field]);
                }
            } else {
                alert("Ocurrió un error inesperado. Revisa la consola para más detalles.");
            }
        }
    });
});
