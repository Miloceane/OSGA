/********************************/
/* OSGA - character.js          */
/* Written by Charlotte Lafage  */
/* (GitHub: Miloceane)          */
/********************************/

function display_spoiler_character() {
	document.querySelector('#character_info').style.display = "block";
	document.querySelector('#other_characters').style.display = "block";
	document.querySelector('#display_spoiler_cemetery').style.display = "none";			
}

function delete_message_box(e) {
	let message_id = e.target.getAttribute("message_id");
	document.getElementById('confirm_delete_message').setAttribute("message_id", message_id);
	document.getElementById('validation_box').style.display='block';
}

function confirm_delete_message(e) {
	let message_id = e.target.getAttribute("message_id");

	// Sends AJAX request to delete message
	var xhttp = new XMLHttpRequest();
	ajax_url = "/delete_character_message/"+message_id;
	xhttp.open("GET", ajax_url, true);
	xhttp.send();

	let message_element = document.getElementById("message_" + message_id);
	message_element.remove();

	document.getElementById('validation_box').style.display='none';
}
