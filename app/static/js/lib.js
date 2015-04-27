var app_history = [];

/* 
 * displays an alert in the shared alert area
 */
function addAlert (message, type)
{
	var color = "alert-info";
	if (type != undefined)
	{
		if (type == "success")
		{
			color = "alert-success";
		} else if (type == "error")
		{
			color = "alert-danger";
		}
	}
	$("#alerts-area").
		prepend("<div class='row'> <div class='col'>" +
			"<div class='alert " + color + "'>" +
			"<button type='button' class='close'" + 
			"data-dismiss='alert' aria-hidden='true'>" +
			"x </button> <p>" + message + "</p>" +
			"</div> </div> </div>");
	$("alerts-area").show();
}

/*
 * updates user reference. call after changing user data.
 */
function loadUser(callback)
{
	safeGet("/me", function (data) {
		user = data;
		if (callback != undefined) {
			callback();
		}
	});
}

/*
 * wrapper function for making JSON GET request from server
 *
 *	path - the URL to request from
 *	success - required callback on success
 *	error - optional handler for errors, default is provided
 *	params - optional params JSON object to pass to server
 */
function safeGet (path, success, error, params)
{
	var data = params == undefined ? {} : params;

	function errorHandler (data)
	{
		addAlert("Something is wrong with the server right now... Try again later",
				"error");	
	}

	function successHandler (data) 
	{
		if ("status_code" in data)
		{
			switch (data.status_code)
			{
				// no errors
				case 0:
					success(data);
					break;
				// not authenticated
				// bad request
				default:
					if (error != undefined)
					{
						error(data);
					} 
					else 
					{
						addAlert("An unexpected error occurred while" +
							" accessing " + path);
					}
					break;
			}
		}
		else 
		{
			// API error or server down
			errorHandler(data);
		}
	}

	$.ajax({
			url: path,
			data: params,
			datatype: 'json',
			success : successHandler,
			error: errorHandler,
			timeout: 5000,
			cache: false
		});
}
/*
 wrapper function for displaying a jinja template
 
page = "/static/js-templates/test.html", parameters = {"test":"fuck"} 
*/
function changePage(page, parameters) {
	app_history.push({ page : page, parameters : parameters });
	$.get(page, function(template) {
		try {
		  var fn = jinja.compile(template).render(parameters);
		} catch(e) {
		  //todo: update error panel
		  return;
		}
		src = fn.toString();
		$('#content-div').html(src);

	});

	setTimeout(function () {
		clearAlerts();
	}, 3000);
}

/*
 * navigate back a page
 */ 
function backPage()
{
	// make sure we can go back
	if (app_history.length > 1)
	{
		app_history.pop();
		var last_page = app_history.pop();

		changePage(last_page.page, last_page.parameters);
	}

	setTimeout(function () {
		clearAlerts();
	}, 3000);
}

/*
 * clears the page of alerts
 */ 
function clearAlerts()
{
	$("#alerts-area").fadeOut(1000, function () {
		console.log("finished fading")
		$("#alerts-area").html("");
	});
}

/*
 * reload the current page
 */
function refreshPage()
{
	var current_page = app_history.pop();
	changePage(current_page.page, current_page.parameters);
	clearAlerts();
}

/* shortcuts to go to a certain type of page */
function goToTask(task_id)
{
	changePage("static/js-templates/task.html", { id : task_id });
}
function goToVolunteerTask(task_id)
{
	changePage("static/js-templates/volunteer-task.html", { id : task_id });
}

function goToEvent(id)
{
	changePage("static/js-templates/event.html", { id : id });
}

function goToVolunteerEvent(id)
{
	changePage("static/js-templates/volunteer.html", { id : id });
}

function dateToString(date)
{
	var day = date.getDay();
	var month = date.getMonth();
	var year = date.getFullYear();

	return day + "/" + month + "/" + year;
}

function bindList(listTarget, searchInput)
{
	$("#" + listTarget).btsListFilter("#" + searchInput, {itemChild: 'span'});
}
