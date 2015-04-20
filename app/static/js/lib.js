/* 
 * displays an alert in the shared alert area
 */
function addAlert (message)
{
	$("#alerts-area").
		prepend("<div class='row'> <div class='col'>" +
			"<div class='alert alert-info'>" +
			"<button type='button' class='close'" + 
			"data-dismiss='alert' aria-hidden='true'>" +
			"x </button> <p>" + message + "</p>" +
			"</div> </div> </div>");
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
	$.getJSON(path, params)
		.done(function (data) {
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
		});
}