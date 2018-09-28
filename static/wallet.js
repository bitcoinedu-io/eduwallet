// Use available button - Set amount to total balance
$("#available").click(function() {
  $("#amount").val( $("#balance").text() );
});
$.ajaxSetup({
  error: function(xhr, status, error) {
    console.log("An AJAX error occured: " + status + "\nError: " + error + "\nError detail: " + xhr.responseText);
  } 
});
// send transaction
// Do basic verifications of form entry
// passes along server error from bitcoin node
// if successful, switches payment button for a home button instead
$("#makepayment").click(function(event) {
  $("#makepayment").prop("disabled", true);
  var payfrom = $("#payfrom").text();
  var balance = parseFloat($("#balance").text());
  var payto = $("#payto").val();
  var amount = $("#amount").val().replace(",", ".");
  amount = parseFloat(amount);
  var trouble = false;
  if (isNaN(amount) || amount <= 0.0 || amount > balance) {
    $("#amount").addClass("is-invalid");
    trouble = true;
  } else {
    $("#amount").removeClass("is-invalid");
  }
  if (payto.length < 10) {
    $("#payto").addClass("is-invalid");
    trouble = true;
  } else {
    $("#payto").removeClass("is-invalid");
  }
  if (trouble) {
    event.preventDefault();
    event.stopPropagation();
    $("#makepayment").prop("disabled", false);
    return;
  }
  $.post('/api/makepayment', {payfrom: payfrom, payto: payto, amount: amount})
  .done(function(myJson) {
    console.log(JSON.stringify(myJson));
    if ("error" in myJson && myJson["error"] != null) {
	// something went wrong, display danger div
	var mess = myJson["error"];
        if ("message" in mess) {
	  mess = mess["message"];
	}
	$("#paystatus").removeClass("alert-success");
	$("#paystatus").addClass("alert-danger").text("Error: " + JSON.stringify(mess));
        $("#makepayment").prop("disabled", false);
    } else {
	// success, display success div
	var txid = myJson['result'];
	mess = "Success: " + amount + " BTE sent to " + payto + "<br>Tx ID: " + txid +
	    "<br>The transaction will typically be included in the next block (on average every 10 min).";
	$("#paystatus").removeClass("alert-danger");
	$("#paystatus").addClass("alert-success").html(mess);
	$("#makepayment").hide();
	$("#gohome").show();
	$("#newpay").show();
	updateBal(payfrom);
    }
  });
});
$("#makepayment2").click(function(event) {
  $("#makepayment").prop("disabled", true);
  var payfrom = $("#payfrom").text();
  var balance = parseFloat($("#balance").text());
  var payto = $("#payto").val();
  var amount = $("#amount").val().replace(",", ".");
  amount = parseFloat(amount);
  var trouble = false;
  if (isNaN(amount) || amount <= 0.0 || amount > balance) {
    $("#amount").addClass("is-invalid");
    trouble = true;
  } else {
    $("#amount").removeClass("is-invalid");
  }
  if (payto.length < 10) {
    $("#payto").addClass("is-invalid");
    trouble = true;
  } else {
    $("#payto").removeClass("is-invalid");
  }
  if (trouble) {
    event.preventDefault();
    event.stopPropagation();
    $("#makepayment").prop("disabled", false);
    return;
  }
  fetch('/api/makepayment', {
    method: "POST",
    mode: "same-origin",
    cache: "no-cache",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({payfrom: payfrom, payto: payto, amount: amount})
  })
  .then(function(response) {
    console.log(response);
    return response.json();
  })
  .then(function(myJson) {
    if ("error" in myJson && myJson["error"] != null) {
	var mess = myJson["error"];
        if ("message" in mess) {
	  mess = mess["message"];
	}
	$("#paystatus").removeClass("alert-success");
	$("#paystatus").addClass("alert-danger").text("Error: " + JSON.stringify(mess));
        $("#makepayment").prop("disabled", false);
    } else {
	var txid = myJson['result'];
	mess = "Success: " + amount + " BTE sent to " + payto + "<br>Tx ID: " + txid +
	    "<br>The transaction will typically be included in the next block (on average every 10 min).";
	$("#paystatus").removeClass("alert-danger");
	$("#paystatus").addClass("alert-success").html(mess);
	$("#makepayment").hide();
	$("#gohome").show();
	$("#newpay").show();
	updateBal(payfrom);
    }
    console.log(JSON.stringify(myJson));
  })
  .catch(function(error) { return console.error('Error:', error); });
});
// Fetch current balance from server, update "Balance" on page
var updateBal = function(addr) {
  $.get( "/api/getbalance",{addr: addr})
  .done(function(data) {
    $("#balance").text(data['balance']);
  });
};
// Update balance from server every 3 min
// Only initiate this for pages that seem to contain a balance field
(function() {
  if ($("#balance").length > 0 && $("#payfrom").length > 0) {
    addr = $("#payfrom").text();
    setInterval(function(){ updateBal(addr); }, 3 * 60 * 1000);
  }
})();
// testing
