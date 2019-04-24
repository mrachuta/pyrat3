function changeCommandWrapper () {
  $('input[type="radio"]').click(function () {
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
}

function addOrRemoveArgsField () {
  var maxFields = 8;
  var minFields = 2;
  var fieldCounter = 1;
  var wrapper = $('#form_area_run_command_args_box');

  $(wrapper).on('click', '#add_input', function (e) {
    e.preventDefault();
    var totalFields = $('#form_area_run_command_args_box > div').length
    if(totalFields <= maxFields){
      // Additional div must be added, for removing button function
      $(wrapper).append(`<div class="form-area-arg-field"><label for="arg${fieldCounter}">Arg${fieldCounter}:</label>\
      <textarea name="arg${fieldCounter}" id="arg${fieldCounter}" required="required"></textarea></div>`);
      fieldCounter++;
    } else {
      alert('Maximum field count was reached');
    }
  });
  $(wrapper).on('click', '#remove_input', function (e) {
    e.preventDefault();
    var totalFields = $('#form_area_run_command_args_box > div').length
    if(totalFields > minFields){
      $(wrapper).children().last().remove();
      fieldCounter--;
    } else {
      alert('Minimum field count was reached');
    }
  });
}

function submitCommand () {
  $('#command_form').on('submit', function (element) {
    element.preventDefault();

    var argsDict = {};
    var selectedCommand = $('#form_area_command_box input:checked').attr('value');
    var commandId = $('#id_command_id').val();
    console.log(selectedCommand);

    $(`#form_area_${selectedCommand}_args_box input`).each(function () {
      argsDict[this.id] = this.value;
    });
    $(`#form_area_${selectedCommand}_args_box textarea`).each(function () {
      argsDict[this.id] = this.value;
    });
    $(`#form_area_${selectedCommand}_args_box select`).each(function () {
      argsDict[this.id] = this.value;
    });

    var argsStr = JSON.stringify(argsDict);
    console.log(argsStr);

    $('#id_command_args').val(argsStr);

    // exclude divs and inputs
    var dataStr = $(
    '#command_form :not(.form-area-arg-field textarea, .form-area-arg-field select)'
    ).serialize();

    $.ajax({
      url: '/pyrat3_server/index/',
      type: 'POST',
      data: dataStr,
    })
    .done(function (toCommandResp) {
      console.log(toCommandResp);
      $('#ajax_status').empty();
      if (toCommandResp.form_valid) {
        $('#ajax_status').text(
        `AJAX request with command ${selectedCommand} (command_id: ${commandId})
        was successfully processed.`
        );
      } else {
        $('#ajax_status').text(
        `Server was not returned confirmation about processing command
        ${selectedCommand} (command_id: ${commandId}) Try again.`
         );
    }
    $.ajax({
      url: '/pyrat3_server/generate_command_id/',
      type: 'GET',
    })
    .done(function (toCommandIdResp) {
      console.log(toCommandIdResp);
      $('#id_command_id').val(toCommandIdResp.command_id);
      })
    .fail(function (uidResponse) {
      console.log(uidResponse);
      alert('Unable to get new command_id, please hit CTRL+R to refresh site!');
    });
    })
      .fail(function (toCommandResp) {
        console.log(toCommandResp);
        if (!toCommandResp.form_valid) {
          $('#ajax_status').text(
          `AJAX request with command ${selectedCommand} (command_id: ${commandId})
          was not successfully processed. Form validation failed.`
          );
        } else {
          $('#ajax_status').text(
          `Server was unable to process AJAX request with command
          ${selectedCommand}(command_id: ${commandId}) Unknown error.`
          );
        }
      });
  });
}

function loadClientTable () {
  var refreshInterval = 10;
  setInterval(function () {
    $.ajax({
      url: '/pyrat3_server/client_table/#client_table',
    })
    .done(function (fetchedTable) {
      // console.log(fetched_table);
      $('#fresh_client_table').html(fetchedTable);
    })
    .fail(function() {
      $('#fresh_client_table').text('Unable to load data.');
    });
  }, (refreshInterval*1000));
  setInterval(function () {
      refreshInterval--;
      $('#refresh_counter').text(`Remaning time to refresh: ${refreshInterval} seconds.`);
      if (refreshInterval == 0) {
          refreshInterval = 10;
      }
  }, 1000);
}

function showOrHideInfo (element) {
  var elementGrandFather = $(element).parents().eq(1).attr('id');
  console.log(elementGrandFather);
  var clientId = $(`#${elementGrandFather} td:nth-child(2)`).text();
  var divId = `#client_table_${clientId}_info_row`;
  if ($(divId).is(":visible")) {
    $(divId).hide();
  } else {
    $(divId).show();
  }
};

$(document).ready(function () {
  changeCommandWrapper();
  addOrRemoveArgsField();
  submitCommand();
  loadClientTable();
});