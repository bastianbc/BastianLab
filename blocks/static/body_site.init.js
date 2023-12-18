const MAX_TIER = 4;

const row = document.getElementsByClassName("body-site-row")[0];

document.addEventListener('DOMContentLoaded', (event) => {

  var bodySites = getBodySites("");

  removeDropdownList(1);

  if (bodySites.length > 0) {

    addNewDropdownList(bodySites,1);

  }

  setBodySite();

});

function getBodySites(parent_id) {

  var result = [];

  $.ajax({
      url: "/body/get_bodies/" + parent_id,
      type: "GET",
      async: false,
      success: function (data) {

        result = data;

      }
  });

  return result;

}

function addNewDropdownList(items,tier) {

  if (tier > 4) {

    return;

  }

  var element = document.getElementById("id_mock_body_site");

  var col = document.createElement("div");
  col.classList.add("col-2");

  var label = document.createElement("label");
  label.innerHTML = "";
  label.htmlFor = "body_site_" + tier;

  var select = document.createElement("select");
  select.name = "body_site_" + tier;
  select.id = "id_mock_body_site_" + tier;
  select.classList.add("select","form-control");;

  var option = document.createElement("option");
  option.value = null;
  option.text = "-----------";
  select.appendChild(option);

  for (const item of items)
  {
    var option = document.createElement("option");
    option.value = item.id;
    option.text = item.name;
    select.appendChild(option);
  }

  col.appendChild(label);
  col.appendChild(select);

  row.appendChild(col);

  select.addEventListener("change", function () {

    var bodySites = getBodySites(this.value);

    removeDropdownList(tier + 1);

    if (bodySites.length > 0) {

      addNewDropdownList(bodySites, tier + 1);

    }

    setBodySite();

  });

}

function removeDropdownList(tier) {

  for (var i = tier; i <= MAX_TIER; i++) {

    var element = document.getElementById("id_mock_body_site_" + i);

    if (element) {

      element.parentElement.remove();

    }

  }

}

function setBodySite() {

  for (var i = 1; i <= MAX_TIER; i++) {

    var element = document.getElementById("id_mock_body_site_" + i);

    if (element) {
      document.getElementById("id_body_site").value = element.value;

    }

  }

}
