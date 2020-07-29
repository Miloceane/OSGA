let graves_plaques = document.getElementsByClassName('grave_plaque');
for (var i = 0; i < graves_plaques.length; i++) 
{
	current_grave = graves_plaques[i];
	current_grave.addEventListener('click', change_last_click, true);
	current_grave.addEventListener('click', add_to_grave);
}

grave_plaque_height = graves_plaques[0].scrollHeight; 
grave_plaque_width = graves_plaques[0].scrollWidth;