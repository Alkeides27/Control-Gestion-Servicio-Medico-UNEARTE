$(document).ready(function() {
    // Crear Tipo de Cita
    $('#crearTipoForm').submit(function(e) {
        e.preventDefault();
        var nombre = $('#nombre_tipo').val();
        var descripcion = $('#descripcion_tipo').val();
        var duracion = $('#duracion_tipo').val();
        
        if (!nombre) {
            alert('Por favor, ingrese un nombre para el tipo de cita');
            return;
        }
        
        // Mostrar indicador de carga
        var submitBtn = $(this).find('button[type=submit]');
        var originalText = submitBtn.html();
        submitBtn.html('<i class="bi bi-hourglass"></i> Creando...');
        submitBtn.prop('disabled', true);
        
        $.ajax({
            url: '/citas/ajax/crear-tipo-cita/',
            method: 'POST',
            headers: {
                'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()
            },
            contentType: 'application/json',
            data: JSON.stringify({
                'nombre': nombre,
                'descripcion': descripcion,
                'duracion_estimada': parseInt(duracion) || 30
            }),
            success: function(response) {
                if (response.success) {
                    // Agregar opción al select
                    $('#id_tipo_cita').append(
                        $('<option>', {
                            value: response.id,
                            text: response.nombre
                        })
                    );
                    // Seleccionar la nueva opción
                    $('#id_tipo_cita').val(response.id);
                    // Cerrar modal
                    $('#crearTipoModal').modal('hide');
                    // Limpiar formulario
                    $('#crearTipoForm')[0].reset();
                    // Mostrar mensaje de éxito
                    alert('Tipo de cita creado exitosamente');
                } else {
                    alert('Error al crear el tipo de cita: ' + JSON.stringify(response.errors));
                }
            },
            error: function(xhr, status, error) {
                console.log('Error detallado:', xhr.responseText);
                alert('Error al crear el tipo de cita: ' + error);
            },
            complete: function() {
                // Restaurar botón
                submitBtn.html(originalText);
                submitBtn.prop('disabled', false);
            }
        });
    });
    
    // Crear Motivo de Cita
    $('#crearMotivoForm').submit(function(e) {
        e.preventDefault();
        var nombre = $('#nombre_motivo').val();
        var descripcion = $('#descripcion_motivo').val();
        
        if (!nombre) {
            alert('Por favor, ingrese un nombre para el motivo de cita');
            return;
        }
        
        // Mostrar indicador de carga
        var submitBtn = $(this).find('button[type=submit]');
        var originalText = submitBtn.html();
        submitBtn.html('<i class="bi bi-hourglass"></i> Creando...');
        submitBtn.prop('disabled', true);
        
        $.ajax({
            url: '/citas/ajax/crear-motivo-cita/',
            method: 'POST',
            headers: {
                'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()
            },
            contentType: 'application/json',
            data: JSON.stringify({
                'nombre': nombre,
                'descripcion': descripcion
            }),
            success: function(response) {
                if (response.success) {
                    // Agregar opción al select
                    $('#id_motivo').append(
                        $('<option>', {
                            value: response.id,
                            text: response.nombre
                        })
                    );
                    // Seleccionar la nueva opción
                    $('#id_motivo').val(response.id);
                    // Cerrar modal
                    $('#crearMotivoModal').modal('hide');
                    // Limpiar formulario
                    $('#crearMotivoForm')[0].reset();
                    // Mostrar mensaje de éxito
                    alert('Motivo de cita creado exitosamente');
                } else {
                    alert('Error al crear el motivo de cita: ' + JSON.stringify(response.errors));
                }
            },
            error: function(xhr, status, error) {
                console.log('Error detallado:', xhr.responseText);
                alert('Error al crear el motivo de cita: ' + error);
            },
            complete: function() {
                // Restaurar botón
                submitBtn.html(originalText);
                submitBtn.prop('disabled', false);
            }
        });
    });
    
    // Crear Estado de Cita
    $('#crearEstadoForm').submit(function(e) {
        e.preventDefault();
        var nombre = $('#nombre_estado').val();
        var descripcion = $('#descripcion_estado').val();
        var color = $('#color_estado').val();
        
        if (!nombre) {
            alert('Por favor, ingrese un nombre para el estado de cita');
            return;
        }
        
        // Mostrar indicador de carga
        var submitBtn = $(this).find('button[type=submit]');
        var originalText = submitBtn.html();
        submitBtn.html('<i class="bi bi-hourglass"></i> Creando...');
        submitBtn.prop('disabled', true);
        
        $.ajax({
            url: '/citas/ajax/crear-estado-cita/',
            method: 'POST',
            headers: {
                'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()
            },
            contentType: 'application/json',
            data: JSON.stringify({
                'nombre': nombre,
                'descripcion': descripcion,
                'color': color
            }),
            success: function(response) {
                if (response.success) {
                    // Agregar opción al select
                    $('#id_estado').append(
                        $('<option>', {
                            value: response.id,
                            text: response.nombre
                        })
                    );
                    // Seleccionar la nueva opción
                    $('#id_estado').val(response.id);
                    // Cerrar modal
                    $('#crearEstadoModal').modal('hide');
                    // Limpiar formulario
                    $('#crearEstadoForm')[0].reset();
                    // Mostrar mensaje de éxito
                    alert('Estado de cita creado exitosamente');
                } else {
                    alert('Error al crear el estado de cita: ' + JSON.stringify(response.errors));
                }
            },
            error: function(xhr, status, error) {
                console.log('Error detallado:', xhr.responseText);
                alert('Error al crear el estado de cita: ' + error);
            },
            complete: function() {
                // Restaurar botón
                submitBtn.html(originalText);
                submitBtn.prop('disabled', false);
            }
        });
    });
});