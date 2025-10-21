$(document).ready(function() {
    // Crear Categoría
    $('#crearCategoriaForm').submit(function(e) {
        e.preventDefault();
        
        var formData = {
            'nombre': $('#nombre_categoria').val(),
            'descripcion': $('#descripcion_categoria').val()
        };

        if (!formData.nombre) {
            alert('Por favor, ingrese un nombre para la categoría.');
            return;
        }

        var submitBtn = $(this).find('button[type=submit]');
        var originalText = submitBtn.html();
        submitBtn.html('<i class="bi bi-hourglass"></i> Creando...');
        submitBtn.prop('disabled', true);

        $.ajax({
            url: '/inventario/ajax/crear-categoria/',
            method: 'POST',
            headers: {
                'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()
            },
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(response) {
                if (response.success) {
                    $('#id_categoria').append($('<option>', {
                        value: response.id,
                        text: response.nombre
                    })).val(response.id);
                    $('#crearCategoriaModal').modal('hide');
                    $('#crearCategoriaForm')[0].reset();
                } else {
                    alert('Error al crear la categoría: ' + JSON.stringify(response.errors));
                }
            },
            error: function(xhr) {
                alert('Error de servidor: ' + xhr.responseText);
            },
            complete: function() {
                submitBtn.html(originalText);
                submitBtn.prop('disabled', false);
            }
        });
    });

    // Crear Proveedor
    $('#crearProveedorForm').submit(function(e) {
        e.preventDefault();

        var formData = {
            'nombre': $('#nombre_proveedor').val(),
            'contacto': $('#contacto_proveedor').val(),
            'telefono': $('#telefono_proveedor').val(),
            'email': $('#email_proveedor').val(),
            'direccion': $('#direccion_proveedor').val()
        };

        if (!formData.nombre) {
            alert('Por favor, ingrese un nombre para el proveedor.');
            return;
        }

        var submitBtn = $(this).find('button[type=submit]');
        var originalText = submitBtn.html();
        submitBtn.html('<i class="bi bi-hourglass"></i> Creando...');
        submitBtn.prop('disabled', true);

        $.ajax({
            url: '/inventario/ajax/crear-proveedor/',
            method: 'POST',
            headers: {
                'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()
            },
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(response) {
                if (response.success) {
                    $('#id_proveedor').append($('<option>', {
                        value: response.id,
                        text: response.nombre
                    })).val(response.id);
                    $('#crearProveedorModal').modal('hide');
                    $('#crearProveedorForm')[0].reset();
                } else {
                    alert('Error al crear el proveedor: ' + JSON.stringify(response.errors));
                }
            },
            error: function(xhr) {
                alert('Error de servidor: ' + xhr.responseText);
            },
            complete: function() {
                submitBtn.html(originalText);
                submitBtn.prop('disabled', false);
            }
        });
    });
});