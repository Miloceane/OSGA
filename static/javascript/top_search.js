var json_shows_list = ""

function get_top_search_options(e) 
{
	if (json_shows_list.length == 0)
	{
		var xhttp = new XMLHttpRequest(); 

		ajax_url = "/get_shows_list";
		xhttp.open("GET", ajax_url, true);
		xhttp.setRequestHeader("Content-Type", "application/json");
		
        xhttp.onreadystatechange = function () 
        {
            if (xhttp.readyState === 4 && xhttp.status === 200) 
            {
                json_shows_list = JSON.parse(xhttp.response);

                let top_search_div = document.getElementById("top_dropdown_list");

		        for (i = 0; i < json_shows_list.length; i++)
		        {
		        	let search_link = document.createElement("a");
		        	search_link.innerHTML = json_shows_list[i].name;
		        	search_link.href = "/cemetery/" + json_shows_list[i].id;

		        	top_search_div.appendChild(search_link);
		        }
            }
        };
        xhttp.send();
    }
}

function top_dropdown_function() 
{
	document.getElementById("top_input").classList.toggle("show");
}

function filter_function() 
{
	var input, filter, ul, li, a, i, last_good_i;
	input = document.getElementById("top_input");
	div = document.getElementById("top_dropdown_list");
	a = div.getElementsByTagName("a");
		
	if (input.value.length > 0)
	{
		filter = input.value.toUpperCase();
		
		last_good_i = 0;

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
