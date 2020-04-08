var attr = [];
var prefs = [];
var divs = [];
var cap = {};
var preferences_bounds = {};

$(document).ready( function() {
    $("#add_attribute").click( function() {
        var name = $('#attribute_name').val();
        element = document.createElement("li");
        element.innerHTML = name;
        attr.push(name);
        $("#attributes").append(element);
        $('#attribute_name').val("");
    });

    $("#add_preference").click( function() {
        let name = $('#preference_name').val();
        let min_value = $('#preference_min').val();
        let max_value = $('#preference_max').val();
        let groups_number = $('#groups_number').val();
        let lower_bound = min_value !== "" ? min_value : 0;
        let upper_bound = max_value !== "" ? max_value : groups_number;
        preferences_bounds[name] = {"min": lower_bound, "max": upper_bound};
        element = document.createElement("li");
        element.innerHTML = name + " (min: " + lower_bound.toString() + " - max: " + upper_bound.toString() + ")";
        prefs.push(name);
        $("#preferences").append(element);
        $('#preference_name').val("");
        $('#preference_min').val("");
        $('#preference_max').val("");
    });

    $("#add_division").click( function() {
        let name = $('#division_name').val();
        cap[name] = $('#division_capacity').val();
        element = document.createElement("li");
        element.innerHTML = name + " (Capacidad: " + cap[name].toString() + ")";
        divs.push(name);
        $("#divisions").append(element);
        $('#division_name').val("");
        $('#division_capacity').val("");

    });

    $('#attributes').on('click', 'li', function(e) { 
        attr = attr.filter(item => item !== $(this).text()); 
        $(this).remove(); 
    });  

    $('#preferences').on('click', 'li', function(e) { 
        prefs = prefs.filter(item => item !== $(this).text()); 
        $(this).remove(); 
    });  

    $('#divisions').on('click', 'li', function(e) { 
        divs = divs.filter(item => item !== $(this).text()); 
        $(this).remove(); 
    }); 

    $("#generate_template").click( function() {
      let p_number = $('#students_preferences_number').val();
      $.post("initial_form.html", {attributes: attr,
                                   preferences: prefs,
                                   divisions: divs,
                                   capacity: cap,
                                   students_preferences_number: p_number}, function() {
                                        $('#template_link').text("Descargar template");
                                        $("#upload").toggle();
                                        });
    });

    $("#upload_template").click( function() {
      var fd = new FormData();
      var files = $('#file')[0].files[0];
      fd.append('file',files);

      $.ajax({
        url: 'input.html',
        type: 'post',
        data: fd,
        contentType: false,
        processData: false,
        success: function(response){
            alert('Plantilla subida exitosamente');
            $("#create_groups").toggle();
            },
       });
    });

    $("#create_groups").click( function() {
      let g_number = $('#groups_number').val();
      let l_number = $('#lower_number').val();
      let u_number = $('#upper_number').val();
      let p_number = $('#students_preferences_number').val();
      $.post("create_groups.html", {
                                   attributes: attr,
                                   preferences: preferences_bounds,
                                   divisions: divs,
                                   capacity: cap,
                                   groups_number: g_number,
                                   lower_number: l_number,
                                   upper_number: u_number,
                                   students_preferences_number: p_number
                                   },
                                   function(data, status) {
                                        $('#results').text('Descargar resultados');
                                   }
                                   );
    });
});