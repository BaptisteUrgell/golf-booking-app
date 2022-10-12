function display_players(){
    let nb_players = document.getElementById("nb_players").value;
    for(i = 2; i <= 4; i++){
        if (i <= nb_players){
            document.getElementById(`player_${i}`).removeAttribute("hidden");
            console.log("remove");
            document.getElementById(`input_player_${i}`).setAttribute("required","");
        }else{
            document.getElementById(`input_player_${i}`).removeAttribute("required");
            document.getElementById(`player_${i}`).setAttribute("hidden","");
            console.log("add");
        }
    }
}

window.onbeforeunload = function() {
    document.getElementById("shutdown").submit()
}