$(document).ready(function() {
    console.log("ready");
    var csrftoken = $("[name=csrfmiddlewaretoken]").val();
    var time = 1
    $(".fades").each(function(i) {
        $(this).delay(600*i*time).fadeIn(600*time)
        if ($(this).hasClass("UA-img")) {
            $('.UA-img').delay(600).animate({height: "100px", width: "300px"})
            $(".reviews-form").delay(3500).fadeIn(500);
        } else {
            $(this).fadeOut(600*time);
            time -= 0.05
        };
    });

    var winwidth = $( window ).width()
    $('.submit').click(function() {
        $('.form-title').fadeOut(250)
        $(".reviews-form").animate({height: "100px", width: winwidth, top: "0px"});
        $('.form-info').animate({paddingLeft:"300px", paddingTop:"10px"})
        $(".pad").each(function(i) {
            $(this).addClass('col-lg-2');
        })

        $.ajax({
            url: 'reviews',
            type: 'POST',
            headers:{
                "X-CSRFToken": csrftoken
            },
            data: $(".form-info").serialize(),
            cache: true,
            success: function(data) { 
                var reviews = data.reviews
                var table = "<table class='table table-bordered'>";
                table+="<thead>";
                table+="<tr>";
                table+="<th>Tour</th>";
                table+="<th>Date of Review</th>";
                table+="<th>Trip Advisor, Yelp, UAL, Viator</th>";
                table+="<th>Reviewer User Name</th>";
                table+="</tr>";
                table+="</thead>";
                for (var i = 0; i < reviews.length; i++) {
                    table+="<tr>";
                    table+="<td>"+reviews[i].tour+"</td>";
                    table+="<td>"+reviews[i].date+"</td>";
                    table+="<td>"+reviews[i].link+"</td>";
                    table+="<td>"+reviews[i].user+"</td>";
                    table+="</tr>";
                }
                table+="</table>";
                if ($('.results-table:hidden')){
                    $('.results-table').fadeIn(500)
                }
                $("#inner-table").html(table);
            },
        });
        console.log($(".form-info").serialize())

    });

});