function changeJobWrapper () {
  $('input[type="radio"]').click(function () {
    var command = $(this).val();
    $(".form-area-initial-args-box").hide();
    $(`#form_area_${command}_args_box > .form-area-arg-field textarea, .form-area-arg-field select`).each(function () {
      $(this).attr('required', 'required');
    });
    $(`#form_area_${command}_args_box`).show();
    $('.form-area-job-args-box').each(function () {
      // console.log(this);
      elementId = $(this).attr('id');
      // console.log(elementId);
      if (!elementId.includes(command)) {
        $(this).hide();
        $('.form-area-arg-field > textarea, select', this).each(function () {
          // console.log(this);
          $(this).removeAttr('required');
          $(this).val('');
        })
      }
    });
  });
}

function addOrRemoveArgField () {
  var maxFields = 8;
  var minFields = 2;
  var fieldCounter = 1;
  var wrapper = $('#form_area_run_command_args_box');

  $(wrapper).on('click', '#add_input', function (element) {
    element.preventDefault();
    var totalFields = $('#form_area_run_command_args_box > div').length
    if(totalFields <= maxFields){
      // Additional div must be added, for removing button function
      $(wrapper).append(
      `<div class="form-area-arg-field"><label for="arg${fieldCounter}">\
      Arg${fieldCounter}:</label><textarea name="arg${fieldCounter}"\
      id="arg${fieldCounter}" required="required"></textarea></div>`
      );
      fieldCounter++;
    } else {
      alert('Maximum field count was reached');
    }
  });
  $(wrapper).on('click', '#remove_input', function (element) {
    element.preventDefault();
    var totalFields = $('#form_area_run_command_args_box > div').length
    if(totalFields > minFields){
      $(wrapper).children().last().remove();
      fieldCounter--;
    } else {
      alert('Minimum field count was reached');
    }
  });
}

function submitJob () {
  $('#job_form').on('submit', function (element) {
    element.preventDefault();

    var argsDict = {};
    var selectedJob = $(
    '#form_area_job_box input:checked').attr('value');
    var jobId = $('#id_job_id').val();
    console.log(selectedJob);

    $(`#form_area_${selectedJob}_args_box input`).each(function () {
      argsDict[this.id] = this.value;
    });
    $(`#form_area_${selectedJob}_args_box textarea`).each(function () {
      argsDict[this.id] = this.value;
    });
    $(`#form_area_${selectedJob}_args_box select`).each(function () {
      argsDict[this.id] = this.value;
    });

    var argsStr = JSON.stringify(argsDict);
    console.log(argsStr);

    $('#id_job_args').val(argsStr);

    // exclude divs and inputs
    var dataStr = $(
    '#job_form :not(.form-area-arg-field textarea, .form-area-arg-field select)'
    ).serialize();

    console.log(dataStr);

    $.ajax({
      url: '/pyrat3_server/index/',
      type: 'POST',
      data: dataStr,
    })
    .done(function (toJobResp) {
      console.log(toJobResp);
      $('#ajax_status').empty();
      if (toJobResp.form_valid) {
        $('#ajax_status').text(
        `AJAX request with job ${selectedJob} (job_id: ${jobId})
        was successfully processed.`
        );
      } else {
        $('#ajax_status').text(
        `Server was not returned confirmation about processing job
        ${selectedJob} (job_id: ${jobId}) Try again.`
         );
    }
    $.ajax({
      url: '/pyrat3_server/generate_job_id/',
      type: 'GET',
    })
    .done(function (toJobIdResp) {
      console.log(toJobIdResp);
      $('#id_job_id').val(toJobIdResp.job_id);
      })
    .fail(function (toJobIdResp) {
      console.log(toJobIdResp);
      alert('Unable to get new job_id, please hit CTRL+R to refresh site!');
    });
    })
      .fail(function (toJobResp) {
        console.log(toJobResp);
        if (!toJobResp.form_valid) {
          $('#ajax_status').text(
          `AJAX request with job ${selectedJob} (job_id: ${jobId})
          was not successfully processed. Form validation failed.`
          );
        } else {
          $('#ajax_status').text(
          `Server was unable to process AJAX request with job
          ${selectedJob}(job_id: ${jobId}) Unknown error.`
          );
        }
      });
  });
}

clientTableCurrUrl = '/pyrat3_server/client_table/#client_table';

function loadClientTable () {
  $.ajax({
    url: clientTableCurrUrl,
  })
  .done(function (fetchedTable) {
    // console.log(fetched_table);
    $('#fresh_client_table').html(fetchedTable);
  })
  .fail(function() {
    $('#fresh_client_table').text('Unable to load data.');
  });
}

function refreshClientTable () {
  var refreshInterval = 10;
  setInterval(loadClientTable(), (refreshInterval*1000));
  setInterval(function () {
      refreshInterval--;
      $('#refresh_counter').text(
      `Remaning time to refresh: ${refreshInterval} seconds.`);
      if (refreshInterval == 0) {
          refreshInterval = 10;
      }
  }, 1000);
}

function showOrHideInfo (element) {
  var elementGrandFather = $(element).parents().eq(1).attr('id');
  // console.log(elementGrandFather);
  var clientId = $(`#${elementGrandFather} td:nth-child(2)`).text();
  var divId = `#client_table_${clientId}_info_row`;
  var visibleDivs = [];
  var client = [];
  if ($(divId).is(':visible')) {
    $(divId).hide();
  } else {
    $(divId).show();
  }
  $('.client-table-info-row').each(function () {
    var infoRowId = `#${$(this).attr('id')}`;
    if ($(infoRowId).is(':visible')) {
      client = {id: infoRowId, visibility: true};
      console.log(client);
      visibleDivs.push(client);
    }
  });
  localStorage.setItem('visible_divs', JSON.stringify(visibleDivs));
}

$(document).ready(function () {
  changeJobWrapper();
  addOrRemoveArgField();
  submitJob();
  refreshClientTable();
});