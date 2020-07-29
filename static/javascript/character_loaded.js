/********************************/
/* OSGA - character_loaded.js   */
/* Written by Charlotte Lafage  */
/* (GitHub: Miloceane)          */
/********************************/

let grave_messages_icons = document.getElementsByClassName('delete_message');
for (var i = 0; i < grave_messages_icons.length; i++) 
{
	grave_messages_icons[i].addEventListener('click', delete_message_box);
}

document.getElementById("confirm_delete_message").addEventListener('click', confirm_delete_message);