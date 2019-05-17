/*
Definitions of global variables used in functions.
Integer values can be changed according to
user requirements.
*/

clientTableCurrUrl = '/pyrat3_server/client_table/#client_table';
refreshInterval = 10;
maxArgFields = 8;
minArgFields = 2;

/*
Function below make visible only selected by radio button
div. Attribute 'required' prevent from send empty form.
*/
function changeJobWrapper () {
  $('input[type="radio"]').click(function () {
    var command = $(this).val();
    // Hide initial message
    $(".form-area-initial-args-box").hide();
    // Make all inputs in selected div 'required'
    $(
    `#form_area_${command}_args_box > .form-area-arg-field textarea, .form-area-arg-field select`
    ).each(function () {
      $(this).attr('required', 'required');
    });
    $(`#form_area_${command}_args_box`).show();
    /*
    Iterate over rest of available command divs
    Each has the same class, so check if div id
    contains selected job. If not, remove 'required'
    attribute and clean field value.
    */
    $('.form-area-job-args-box').each(function () {
      elementId = $(this).attr('id');
      if (!elementId.includes(command)) {
        $(this).hide();
        $('.form-area-arg-field > textarea, select', this).each(function () {
          $(this).removeAttr('required');
          $(this).val('');
        })
      }
    });
  });
}

/*
Function adds additionally input fields for arguments
if 'run_command' job has been selected.
Important for commands with a lot of arguments.
Each argument and argument value should be in separate field.
*/

function addOrRemoveArgField () {
  // Set counter to 1, because field 0 is presented by default
  var fieldCounter = 1;
  var wrapper = $('#form_area_run_command_args_box');

  $(wrapper).on('click', '#add_input', function (element) {
    element.preventDefault();
    var totalArgFields = $('#form_area_run_command_args_box > div').length
    if(totalArgFields <= maxArgFields){
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
    var totalArgFields = $('#form_area_run_command_args_box > div').length
    if(totalArgFields > minArgFields){
      // Find last children (div) and remove it
      $(wrapper).children().last().remove();
      fieldCounter--;
    } else {
      alert('Minimum field count was reached');
    }
  });
}

/// AJAX Form submitting

function submitJob () {
  $('#job_form').on('submit', function (element) {
    element.preventDefault();

    var argsDict = {};
    // Get selected job
    var selectedJob = $(
    '#form_area_job_box input:checked').attr('value');
    /*
    Get Job ID generated on server side and inserted in hidden
    form field.
    */
    var jobId = $('#id_job_id').val();
    /*
    Iterate over all input fields in selected job argument's box
    and add it to dictionary.
    */
    $(`#form_area_${selectedJob}_args_box input`).each(function () {
      argsDict[this.id] = this.value;
    });
    $(`#form_area_${selectedJob}_args_box textarea`).each(function () {
      argsDict[this.id] = this.value;
    });
    $(`#form_area_${selectedJob}_args_box select`).each(function () {
      argsDict[this.id] = this.value;
    });
    // Prepare a JSON string from gathered arguments
    var argsStr = JSON.stringify(argsDict);
    // Insert arguments to hidden form field
    $('#id_job_args').val(argsStr);

    /*
    Serialize form data from all fields in form, excluding
    divs (with fields) related to arguments (because arguments
    was already provided as string to form field - see above).
    */
    var dataStr = $(
    '#job_form :not(.form-area-arg-field textarea, .form-area-arg-field select)'
    ).serialize();

    $.ajax({
      url: '/pyrat3_server/index/',
      type: 'POST',
      data: dataStr,
    })
    /*
    If request was done (server returned response and there is no errors),
    check status of response. This will able to prevent situation,
    when job request will be not processed successfully, but server
    returns no error. Only JSON response with form_valid value true
    will ensure, that job was processed by server without errors.
    */
    .done(function (toJobResp) {
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
      // After positive form submit, try to get new job_id from server
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
    // Continuation of form-submit process - depending of server response
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

// AJAX request for a list of clients

function loadClientTable () {
  $.ajax({
    url: clientTableCurrUrl,
  })
  .done(function (fetchedTable) {
    $('#fresh_client_table').html(fetchedTable);
  })
  .fail(function() {
    $('#fresh_client_table').text('Unable to load data.');
  });
}

/*
Function, that refresh list of clients, to receive
current jobs, results, etc
*/

function refreshClientTable () {
  var tempRefreshInterval = refreshInterval
  setInterval(loadClientTable, (refreshInterval*1000));
  setInterval(function () {
      tempRefreshInterval--;
      $('#refresh_counter').text(
      `Remaining time to refresh: ${tempRefreshInterval} seconds.`);
      if (tempRefreshInterval == 0) {
          tempRefreshInterval = refreshInterval;
      }
  }, 1000);
}

/*
Function below allow to show and hide dynamically client details.
Due to refreshing client list, there is localStorage implementation
to store information about visibility of each client-details.
This prevent to back to original state after refresh.
*/

function showOrHideClientDetails (element) {
  // Get second-level parent id (<tr> id) to find id of client
  var elementGrandFather = $(element).parents().eq(1).attr('id');
  // console.log(elementGrandFather);
  // Get id of client from second table row cell
  var clientId = $(`#${elementGrandFather} td:nth-child(2)`).text();
  var clientDetailsDivId = `#client_table_${clientId}_details_row`;
  var visibleDivs = [];
  var client = [];
  if ($(clientDetailsDivId).is(':visible')) {
    $(clientDetailsDivId).hide();
  } else {
    $(clientDetailsDivId).show();
  }
  /*
  Iterate over each class field and catch visible divs.
  Add them to dictionary, and keep it to localStorage.
  Function works only for current page. After change
  of page (pagination), data will be lost.
  */
  $('.client-table-details-row').each(function () {
    var rowId = `#${$(this).attr('id')}`;
    if ($(rowId).is(':visible')) {
      client = {id: rowId, visibility: true};
      visibleDivs.push(client);
    }
  });
  if (visibleDivs) {
    localStorage.setItem('visible_divs', JSON.stringify(visibleDivs));
  }
}

function showJobResultPopup (message) {
  this.preventDefault;
  $('.job-result-popup-content').html(message);
  $(this).trigger('click');
}

/* Exchange standard select multiple by custom field */
function applyMultiJs () {
  /* Main script loaded on base.html. Here only function is
  called */
  $('#id_client_id').multi();
}

// Run functions when page is loaded

$(document).ready(function () {
  changeJobWrapper();
  addOrRemoveArgField();
  submitJob();
  refreshClientTable();
  applyMultiJs();
});