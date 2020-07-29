/********************************/
/* OSGA - main_search.js        */
/* Written by Charlotte Lafage  */
/* (GitHub: Miloceane)          */
/********************************/

function main_dropdown_function() 
{
	document.getElementById("main_input").classList.toggle("show");
}

function filter_function() 
{
	var input, filter, ul, li, a, i;
	input = document.getElementById("main_input");
	div = document.getElementById("main_dropdown_list");
	a = div.getElementsByTagName("a");
		
	if (input.value.length > 0)
	{
		filter = input.value.toUpperCase();
		
		var last_good_i = 0;

		for (i = 0; i < a.length; i++) 
		{
	    	txtValue = a[i].textContent || a[i].innerText;
	    	if (txtValue.toUpperCase().indexOf(filter) > -1) 
	    	{
	    	  	a[i].style.display = "block";
	    	  	a[last_good_i].style.borderBottom = "none";
	    	  	last_good_i = i;
	    	} 
	    	else 
	    	{
	      		a[i].style.display = "none";
	    	}
	  	}

	  	a[last_good_i].style.borderBottom = "1px solid gray";
	}
	else
	{			
		for (i = 0; i < a.length; i++) 
		{
			a[i].style.display = "none"
		}
	}
}

