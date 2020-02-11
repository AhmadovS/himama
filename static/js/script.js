function startTimer() {

	var timer = new Date();
	let time = timer.getHours() + ":" + timer.getMinutes() + ":" + timer.getSeconds();
	let clockInTime = timer.getTime();

	$.ajax({
            url: '/clock-in',
            type: 'POST',
            data: {
                "clock_in": clockInTime},
            success: function(response) {
                window.location.reload();

            }
        });

}

function stopTimer(){
    var clockInfo = document.getElementById('clockInfo')

    let timer = new Date();
    let clockOutTime = timer.getTime()
    $.ajax({
            url: '/clock-out',
            type: 'POST',
            data: {
                "clock_out": clockOutTime},
            success: function(response) {
                window.location.reload();

            }
        });

}

function deleteLog(){
    var id = $(this).attr('id');

    $.ajax({
        url:'/delete-log',
        type: 'POST',
        data: {
            'log_id':id},
        success: function (response) {
            window.location.reload();

        }
    })
}

$(document).ready(function() {
	document.getElementById("startTimer").onclick = function() {
		startTimer();
		var stopTimerButton = document.getElementById('stopTimer');
		stopTimerButton.disabled = false

        var startTimerButton = document.getElementById('startTimer');
		startTimerButton.disabled = true
	};

	document.getElementById("stopTimer").onclick = function() {
		stopTimer();
		var stopTimerButton = document.getElementById('stopTimer');
		stopTimerButton.disabled = true

        var startTimerButton = document.getElementById('startTimer');
		startTimerButton.disabled = false
	};

});