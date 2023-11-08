// document.getElementById("button_sign_up").addEventListener("click", sign_up)

// function sign_up() {
//   document.getElementById("button_sign_up").style.disable = "disable";
//   document.getElementById("sign_up_form").submit();
// }

// document.getElementById("cancelation").addEventListener("click", cancelation)

// function cancelation() {
//   // let form = document.getElementById("cancelation_form");
//   document.getElementById("button_cancelation").style.disable = "disable";
//   // document.getElementById("modal_sign_up");
//   document.getElementById("cancelation_form").submit();
// }


// document.getElementById("location_filter").addEventListener("change", location_filter_func);

function location_filter_func() {
  // let form = document.getElementById("cancelation_form");
  let filter  = document.getElementById("location_filter");
  let new_url = filter.value
  window.location.href =  new_url;
  // document.getElementById("modal_sign_up");
}