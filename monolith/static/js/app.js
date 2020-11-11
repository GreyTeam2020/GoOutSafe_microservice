//document ready routine
$(document).ready(function() {
    if ($("#myreservation").length){
        $('#myreservation').DataTable();
    }
    if ($("#allrestaurants").length){
        $('#allrestaurants').DataTable();
    }
    if ($("#mymenu").length){
        $('#mymenu').DataTable();
        $("#submitDish").click(() => {$("#addDishForm").submit();});
    }
    if ($("#myreservations").length){
        $('#myreservations').DataTable();
    }
    if ($("#mytables").length){
        $('#mytables').DataTable();
        $("#submitTable").click(() => {$("#addTableForm").submit();});
    }
    if ($("#submitReview").length){
        $("#submitReview").click(() => {$("#reviewForm").submit();});
    }

    if($("#reservation_date").length) {
        $('#reservation_date').datetimepicker({
            inline: true,
            format: 'd/m/Y H:i'
        });
        $("#newBook").click(function () {
            $("#bookTableForm").submit();
        });
        $(".showBooking").click(function () {
            $("#restaurant_id").val($(this).data("id"));
            $("#bookTable").modal("show");
        });


        $(".showUpdateBooking").click(function () {
            $("#reservation_id").val($(this).data("reservation_id"));
            $("#restaurant_id").val($(this).data("rest_id"));
            $("#reservation_date").val($(this).data("reservation_date"));
            $("#people_number").val($(this).data("people_number"));
            $("#bookUpdateTable").modal("show");
        });
    }

    let ratingItems = $(".ratingStats");
    if (ratingItems.length){
        ratingItems.each(function(index, e){
            let rating = parseFloat($(e).data("rating"));
			$(e).html("")
            for (let i=1; i<6; i++){
                if (rating >= 1){
                    $(e).append("<span class=\"material-icons\"> star </span>");
                } else if (rating > 0.5){
                    console.log(rating);
                    $(e).append("<span class=\"material-icons\"> star_half </span>");
                } else {
                    $(e).append("<span class=\"material-icons\"> star_border </span>");
                }
                rating--;
            }
        })
    }

    var switchView = $("#switchView");
    if (switchView.length){
        console.log("ci sono")
        switchView.click(function(){
            var cards = $("#card-view");
            var mapview = $("#map-view");
            if (mapview.is(":hidden")){
                cards.hide();
                mapview.show();
                map.invalidateSize()
                map.fitBounds(group.getBounds());
                switchView.html("Switch to Cards View");
            } else {
                mapview.hide();
                cards.show();
                switchView.html("Switch to Map View");
            }
        });
    }

    if ($("#registerRestaurantSubmit").length){
        $('#open_lunch').datetimepicker({
          datepicker:false,
          format:'H:i'
        });
        $('#close_lunch').datetimepicker({
          datepicker:false,
          format:'H:i'
        });
        $('#open_dinner').datetimepicker({
          datepicker:false,
          format:'H:i'
        });
        $('#close_dinner').datetimepicker({
          datepicker:false,
          format:'H:i'
        });
    }

    $("#searchSubmit").click(function(){
        let search = $("#searchbar").val();
        console.log(search)
        if (search){
            window.location = "/restaurant/search/"+search;
        } else {
            window.location = "/"
        }

    })

    $(".deleteBooking").click(deleteDialog);
    function deleteDialog() {
        var resId = $(this).data("id");
        Swal.fire({
          title: 'Do you want to cancel the reservation?',
          showDenyButton: true,
          showDenyButton: true,
          confirmButtonText: `Yes`,
          denyButtonText: `No`
        }).then((result) => {
          if (result.isConfirmed) {
            location.href = '/customer/deletereservations/' + resId;
          }
        })
    }

    $(".checkIn").click(checkinDialog);
    function checkinDialog() {
        var resId = $(this).data("id");
        Swal.fire({
          title: 'Checkin?',
          showDenyButton: true,
          showDenyButton: true,
          confirmButtonText: `Yes`,
          denyButtonText: `No`
        }).then((result) => {
          if (result.isConfirmed) {
            location.href = '/restaurant/checkinreservations/' + resId;
          }
        })
    }



});
