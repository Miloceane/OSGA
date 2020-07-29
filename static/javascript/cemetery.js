/********************************/
/* OSGA - cemetery.js           */
/* Written by Charlotte Lafage  */
/* (GitHub: Miloceane)          */
/********************************/

let screen_width = window.screen.width;
let counter_flowers = [];
let counter_messages = [];
let graves_messages = [];
let current_flower_id = 0;
let current_character_id = 0;

// Initializes height and width of grave plaque. Actual value is given at the end of this page, after DOM is loaded.
var grave_plaque_height = 0;
var grave_plaque_width = 0;

let last_click_pos = { x:0, y:0 }

function change_current_flower(flower_id)
{
	current_flower_id = flower_id;
	let plaques = document.getElementsByClassName('grave_plaque');

	for (var i = 0; i < plaques.length; i++)
	{
		let current_plaque = plaques[i]
		current_plaque.style.cursor = "url('/static/images/flowers/" + current_flower_id + "_small.png'), url('/static/images/flowers/scroll_small.png'), pointer";
	}
}

function change_last_click(e) 
{
	var rect = e.target.getBoundingClientRect();
	var x = Math.round((e.clientX - rect.left) * 100 / grave_plaque_width);
	var y = Math.round((e.clientY - rect.top) * 100 / grave_plaque_height);
	last_click_pos = { x, y };
	return { x,	y };
}

function add_message(grave_id, character_id)
{
	document.querySelector('#add_message_box').grave = grave_id;
	document.querySelector('#add_message_box').style.display = "block";
	current_character_id = character_id;
}

function add_flower(grave_id, character_id)
{
	if (counter_flowers[grave_id])
	{
		counter_flowers[grave_id]++;
	}
	else
	{
		counter_flowers[grave_id] = parseInt(document.querySelector('#grave_'+grave_id+'_count').innerHTML) + 1;
	}

	let grave = document.querySelector('#grave_'+grave_id+'_count');
	grave.innerHTML = counter_flowers[grave_id];
	
	let flower = document.createElement("img");
	flower.src = "/static/images/flowers/"+current_flower_id+".png";
	flower.alt = "flower";
	flower.height = "20";
	flower.style.position = "absolute"
	flower.style.top = Math.min(last_click_pos.y - 15, 75) + "%"
	flower.style.left = Math.max(0, Math.min(last_click_pos.x - 10, 90)) + "%"

	document.querySelector('#grave_'+grave_id).appendChild(flower);
}

function add_to_grave(e) 
{
	grave_id = e.target.getAttribute('grave_id');
	character_id = e.target.getAttribute('character_id');

	if (current_flower_id == -1)
	{
		add_message(grave_id, character_id);
	}
	else
	{
		add_flower(grave_id, character_id);	

		// Sends AJAX request to save flower
		var xhttp = new XMLHttpRequest();
		ajax_url = "/save_flower";
		xhttp.open("POST", ajax_url, true);
		xhttp.setRequestHeader("Content-Type", "application/json");
		
        xhttp.onreadystatechange = function () 
        {
            if (xhttp.readyState === 4 && xhttp.status === 200) 
            {
                var jsonData = JSON.parse(xhttp.response);
                // console.log(jsonData);
            }
        };

        var data = JSON.stringify({
        	"flowertype_id": current_flower_id,
        	"character_id": character_id,
        	"pos_x": last_click_pos.x, 
        	"pos_y": last_click_pos.y });

        console.log(data);
        xhttp.send(data);
	} 
}


function leave_message()
{
	grave_id = document.querySelector('#add_message_box').grave;
	new_message = document.querySelector('#message_text').value;

	if (!graves_messages[grave_id])
	{
		graves_messages[grave_id] = [];
		counter_messages[grave_id] = 1;
	}
	else
	{
		counter_messages[grave_id]++;
	}

	graves_messages[grave_id].push(new_message);

	let message_div = document.createElement("span");
	message_div.id = "grave_message"+grave_id;
	message_div.classList.add("grave_message");
	document.querySelector('#grave_'+grave_id).appendChild(message_div);

	let message_text = document.createElement("span");
	message_text.classList.add("grave_message_text");
	message_text.innerHTML = new_message;
	document.querySelector('#grave_message'+grave_id).appendChild(message_text);

	let message = document.createElement("img");
	message.src = "/static/images/flowers/scroll.png";
	message.alt = "message";
	message.height = "20";
	document.querySelector('#grave_message'+grave_id).appendChild(message);

	var xhttp = new XMLHttpRequest();
	ajax_url = "/save_message";
	xhttp.open("POST", ajax_url, true);
	xhttp.setRequestHeader("Content-Type", "application/json");
	
    xhttp.onreadystatechange = function () 
    {
        if (xhttp.readyState === 4 && xhttp.status === 200) 
        {
            var jsonData = JSON.parse(xhttp.response);
            // console.log(jsonData);
        }
    };
    
    var data = JSON.stringify({"message": new_message, "character_id": current_character_id });
    console.log(data);
    xhttp.send(data);

	document.querySelector('#add_message_box').style.display = "none";	
}


function display_spoiler_cemetery() {
	document.querySelector('#cemetery_grounds').style.display = "flex";
	document.querySelector('#display_spoiler_cemetery').style.display = "none";			
}

