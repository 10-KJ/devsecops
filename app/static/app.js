(function () {
  var chips = document.querySelectorAll(".chip"), rows = document.querySelectorAll("#tbl tbody tr"), shown = document.getElementById("shown");
  function apply() {
    var on = {}; chips.forEach(function (c) { if (c.classList.contains("on")) on[c.dataset.level] = true; });
    var n = 0; rows.forEach(function (r) { var show = !!on[r.dataset.level]; r.hidden = !show; if (show) n++; });
    shown.textContent = n + " students shown";
  }
  chips.forEach(function (c) { c.addEventListener("click", function () { c.classList.toggle("on"); apply(); }); });
  apply();
})();
