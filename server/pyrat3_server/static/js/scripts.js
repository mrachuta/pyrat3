$(document).ready(function(){
    $('input[type="radio"]').click(function(){
        var command = $(this).val();
        $("div.form-area-initial-args-box").hide();
        $("div.form-area-command-args-box").hide();
        $("div.form-area-command-args-box > .form-area-arg-field textarea, select").each(function() {
            $(this).removeAttr('required');
        });
        $("#form_area_" + command + "_args_box").show();
        $("#form_area_" + command + "_args_box > .form-area-arg-field textarea, select").each(function() {
            $(this).attr('required', 'required');
        });
    });
    $('#command_form').on('submit', function(e) {
        e.preventDefault();

        var args_dict = {};
        var selected_command = $('#form_area_command_box input:checked').attr('value');
        var command_id = $('#id_command_id').val();
        console.log(selected_command);

        $(`#form_area_${selected_command}_args_box input`).each(function () {
            args_dict[this.id] = this.value;
        });
        $(`#form_area_${selected_command}_args_box textarea`).each(function () {
            args_dict[this.id] = this.value;
        });
        $(`#form_area_${selected_command}_args_box select`).each(function () {
            args_dict[this.id] = this.value;
        });

        args_str = JSON.stringify(args_dict);
        console.log(args_str);

        $('#id_command_args').val(args_str);

        // exclude divs and inputs
        var data_str = $('#command_form :not(.form-area-arg-field textarea, .form-area-arg-field select)')
        .serialize();

        $.ajax({
            url: 'index',
            type: 'POST',
            data: data_str,
        })
        .done(function(to_command_resp) {
            console.log(to_command_resp);
            $('#ajax_status').empty();
            if (to_command_resp.form_valid) {
                $('#ajax_status').text(
                `AJAX request with command ${selected_command} (command_id: ${command_id})
                was successfully processed.`
                );
            } else {
                $('#ajax_status').text(
                `Server was not returned confirmation about processing command
                ${selected_command} (command_id: ${command_id}) Try again.`
                 );
            }
            $.ajax({
                url: 'generate_command_id',
                type: 'GET',
            })
            .done(function(to_command_id_resp) {
                console.log(to_command_id_resp);
                $('#id_command_id').val(to_command_id_resp.command_id);
                })
            .fail(function(uid_response) {
                console.log(uid_response);
                alert('Unable to get new command_id, please hit CTRL+R to refresh site!');
            });
        })
        .fail(function(to_command_resp) {
            console.log(to_command_resp);
            if (!to_command_resp.form_valid) {
                $('#ajax_status').text(
                `AJAX request with command ${selected_command} (command_id: ${command_id})
                was not successfully processed. Form validation failed.`
                );
            } else {
                $('#ajax_status').text(
                `Server was unable to process AJAX request with command
                ${selected_command}(command_id: ${command_id}) Unknown error.`
                );
            }
        });
    });
    setInterval(function(){
        $.ajax({
            url: 'client_table #client_table',
        })
        .done(function(fetched_table) {
            // console.log(fetched_table);
            $('#fresh_client_table').html(fetched_table);
        })
        .fail(function() {
            $('#fresh_client_table').text('Unable to load data.');
        });
    }, 10000);
    /* może ttuaj ttrzeba odrębną funkcje ?????? */
    var sec = 10;
    setInterval(function() {
        sec--;
        $('#refresh_counter').text(`Remaning time to refresh: ${sec} seconds.`);
        if (sec == 0) {
            sec = 10;
        }
    }, 1000);
});
function show_or_hide_info(element) {
    console.log($(element).parents().eq(1).attr('id'));
    var cli_id = $('#' + $(element).parents().eq(1).attr('id') + ' td:nth-child(2)').text();
    var div_id = "#client_table_" + cli_id + "_info_row";
    if ($(div_id).is(":visible")) {
        $(div_id).hide();
    } else {
        $(div_id).show();
    }
};
