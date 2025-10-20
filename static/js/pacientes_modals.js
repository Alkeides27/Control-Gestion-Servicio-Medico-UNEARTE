$(document).ready(function() {
    var currentSelectField;

    // Guardar la referencia al select field cuando se abre el modal
    $(document).on('click', '.btn-crear-tipotelefono', function() {
        var prefix = $(this).data('form-prefix');
        currentSelectField = $('#id_' + prefix + '-tipo_telefono');
    });

    // Manejar la creación de Tipo de Teléfono vía AJAX
    $('#crearTipoTelefonoForm').submit(function(e) {
        e.preventDefault();
        var nombre = $('#nombre_tipo_telefono').val();
        var descripcion = $('#descripcion_tipo_telefono').val();

        if (!nombre) {
            alert('Por favor, ingrese un nombre para el tipo de teléfono.');
            return;
        }

        var submitBtn = $(this).find('button[type=submit]');
        var originalText = submitBtn.html();
        submitBtn.html('<i class="bi bi-hourglass"></i> Creando...');
        submitBtn.prop('disabled', true);

        $.ajax({
            url: '/pacientes/ajax/crear-tipo-telefono/',
            method: 'POST',
            headers: {
                'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()
            },
            contentType: 'application/json',
            data: JSON.stringify({
                'nombre': nombre
            }),
            success: function(response) {
                if (response.success) {
                    // Agregar la nueva opción a todos los selects de tipo_telefono en el formset
                    $('.telefono-form select[name$="-tipo_telefono"]').each(function() {
                        $(this).append($('<option>', {
                            value: response.id,
                            text: response.nombre
                        }));
                    });

                    // Seleccionar la nueva opción en el select que abrió el modal
                    if (currentSelectField) {
                        currentSelectField.val(response.id);
                    }
                    
                    $('#crearTipoTelefonoModal').modal('hide');
                    $('#crearTipoTelefonoForm')[0].reset();

                } else {
                    alert('Error al crear el tipo de teléfono: ' + JSON.stringify(response.errors));
                }
            },
            error: function(xhr, status, error) {
                console.log('Error detallado:', xhr.responseText);
                alert('Error de servidor al crear el tipo de teléfono.');
            },
            complete: function() {
                submitBtn.html(originalText);
                submitBtn.prop('disabled', false);
            }
        });
    });
});
